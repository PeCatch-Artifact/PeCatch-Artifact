from slither.slithir.variables.local_variable import LocalIRVariable
from slither.slithir.variables.state_variable import StateIRVariable
from slither.slithir.variables.temporary_ssa import TemporaryVariableSSA
from slither.slithir.variables.reference_ssa import ReferenceVariableSSA
from slither.slithir.variables.temporary import TemporaryVariable
from slither.slithir.variables.reference import ReferenceVariable
from slither.slithir.variables.constant import Constant
from slither.slithir.operations.index import Index
from slither.slithir.operations.member import Member
from slither.slithir.operations.assignment import Assignment
from slither.slithir.operations.length import Length
from slither.slithir.operations.binary import Binary
from slither.slithir.operations.unary import Unary
from slither.slithir.operations.call import Call
from slither.slithir.operations.codesize import CodeSize
from slither.slithir.operations.lvalue import OperationWithLValue
from slither.core.solidity_types.array_type import ArrayType
from slither.slithir.operations.binary import Binary, BinaryType

from plugin.detectors.cfg import *

def getRefDict(f):
    refDict = {}
    for node in f.nodes:
        for ir in node.irs_ssa:
            if isinstance(ir, OperationWithLValue):
                if isinstance(ir.lvalue, TemporaryVariable) or isinstance(ir.lvalue, ReferenceVariable):
                    if ir.lvalue not in refDict:
                        refDict[ir.lvalue] = []
                    refDict[ir.lvalue].append(ir)
            # if isinstance(ir, Index) or isinstance(ir, Member):
            #     refDict[ir.lvalue] = (ir.variable_left, ir.variable_right)
            # elif isinstance(ir, Length):
            #     refDict[ir.lvalue] = (ir.value, Length)
            # elif isinstance(ir, Assignment) and not isinstance(ir.lvalue, Constant):
            #     refDict[ir.lvalue] = ir.rvalue
    return refDict

def assignValue(ir):
    return isinstance(ir, OperationWithLValue) and (isinstance(ir, Assignment) or isinstance(ir, Binary) or isinstance(ir, Unary) or isinstance(ir, Call) or isinstance(ir, CodeSize))

def getRelatedVar(v, refDict, lastIr, predInsts): 
    if v not in refDict:
        if hasNonSSAVersion(v):
            return v.non_ssa_version
        else:
            return v
        
    res = ()
    
    for ir in refDict[v]:
        if not lastIr or (lastIr and ir in predInsts[lastIr]):
            # print(ir, lastIr, ir.read)
            for item in ir.read:
                tmp = getRelatedVar(item, refDict, ir, predInsts)
                if isinstance(tmp, tuple):
                    res += tmp
                else:
                    res += (tmp,)
    return res

# def getRefVar(v, refDict):
    # if v not in refDict:
    #     if hasNonSSAVersion(v):
    #         return v.non_ssa_version
    #     else:
    #         return v
    # res = ()
    # leftv = v
    # while leftv in refDict:
    #     if isinstance(refDict[leftv], tuple):
    #         rightv = refDict[leftv][1]
    #         leftv = refDict[leftv][0]
    #         if isinstance(rightv, ReferenceVariable):
    #             rightv = getRefVar(rightv, refDict)
    #         if hasNonSSAVersion(rightv):
    #             rightv = rightv.non_ssa_version
    #         if isinstance(rightv, tuple):
    #             res = rightv + res
    #         else:
    #             res = (rightv,) + res
    #     else:
    #         leftv = refDict[leftv]
    # if hasNonSSAVersion(leftv):
    #     leftv = leftv.non_ssa_version
    # res = (leftv,) + res
    # return res


def hasNonSSAVersion(v):
    if isinstance(v, LocalIRVariable) or isinstance(v, StateIRVariable) or isinstance(v, TemporaryVariableSSA) or isinstance(v, ReferenceVariableSSA):
       return True
    return False

def detectIncreasedStorage(c): # all dynamic storage arr and check whether the length increases in some functions
    dynamic_sarr = []
    for v in c.state_variables:
        if isinstance(v.type, ArrayType):
            if v.type.is_dynamic:
                dynamic_sarr.append(v)
    
    # print("dynamic_sarr:", dynamic_sarr)
    res = []
    for f in c.functions_and_modifiers:
        if not f.is_implemented:
            continue
        # print(f, "************")
        svars = f.state_variables_read + f.state_variables_written
        # print(svars)
        overlap = list(set(svars) & set(dynamic_sarr) - set(res))
        # print("overlap:", overlap)
        if not overlap:
            continue

        refDict = getRefDict(f)
        predInsts, succInsts = generateIICFG(f)
        for node in f.nodes:
            # print(node)
            svars = node.state_variables_read + node.state_variables_written
            # print("svars:", svars)
            overlap = list(set(svars) & set(dynamic_sarr) - set(res))
            # print("overlap:", overlap)
            if not overlap:
                continue
            readLength = []
            increaseLength = []
            writeLength = []
            for ir in node.irs_ssa:
                # print(ir, type(ir))
                if isinstance(ir, Length):
                    var = getDynamicArr(ir.value, refDict, dynamic_sarr, predInsts)
                    # print("length var:", var)
                    if var and var not in res:
                        readLength.append(var)
                elif isinstance(ir, Binary) and ir.type == BinaryType.ADDITION:
                    var = getDynamicArr(ir.variable_left, refDict, dynamic_sarr, predInsts)
                    # print("Binary var:", var)
                    if var and var not in res:
                        increaseLength.append(var)
                    var = getDynamicArr(ir.variable_right, refDict, dynamic_sarr, predInsts)
                    # print("Binary var:", var)
                    if var and var not in res:
                        increaseLength.append(var)
                elif isinstance(ir, Assignment):
                    var = getDynamicArr(ir.lvalue, refDict, dynamic_sarr, predInsts)
                    # print("Assignment var:", var)
                    if var and var not in res:
                        writeLength.append(var)
            
            # print(readLength, increaseLength, writeLength)
            res.extend(list(set(readLength) & set(increaseLength) & set(writeLength)))

    return res

def getDynamicArr(var, refDict, dynamic_sarr, predInsts):
    if isinstance(var, Constant):
        return None
    if var.non_ssa_version in dynamic_sarr:
        return var.non_ssa_version
    elif var in refDict:
        related_var = getRelatedVar(var, refDict, None, predInsts)
        # print(var, related_var)
        for item in related_var:
            if item in dynamic_sarr:
                return item
    return None