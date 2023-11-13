from slither.slithir.variables.local_variable import LocalIRVariable
from slither.slithir.variables.state_variable import StateIRVariable
from slither.slithir.variables.temporary_ssa import TemporaryVariableSSA
from slither.slithir.variables.reference_ssa import ReferenceVariableSSA
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


def getRefDict(f):
    refDict = {}
    for node in f.nodes:
        for ir in node.irs_ssa:
            if isinstance(ir, Index) or isinstance(ir, Member):
                refDict[ir.lvalue] = (ir.variable_left, ir.variable_right)
            elif isinstance(ir, Length):
                refDict[ir.lvalue] = (ir.value, "length")
            # elif isinstance(ir, Assignment) and not isinstance(ir.lvalue, Constant):
            #     refDict[ir.lvalue] = ir.rvalue
    return refDict

def assignValue(ir):
    return isinstance(ir, OperationWithLValue) and (isinstance(ir, Assignment) or isinstance(ir, Binary) or isinstance(ir, Unary) or isinstance(ir, Call) or isinstance(ir, CodeSize))

def getRefVar(v, refDict):
    if v not in refDict:
        if hasNonSSAVersion(v):
            return v.non_ssa_version
        else:
            return v
    res = ()
    leftv = v
    while leftv in refDict:
        if isinstance(refDict[leftv], tuple):
            rightv = refDict[leftv][1]
            leftv = refDict[leftv][0]
            if isinstance(rightv, ReferenceVariable):
                rightv = getRefVar(rightv, refDict)
            if hasNonSSAVersion(rightv):
                rightv = rightv.non_ssa_version
            if isinstance(rightv, tuple):
                res = rightv + res
            else:
                res = (rightv,) + res
        else:
            leftv = refDict[leftv]
    if hasNonSSAVersion(leftv):
        leftv = leftv.non_ssa_version
    res = (leftv,) + res
    return res

def getRefVarSSA(v, refDict):
    if v not in refDict:
        return v
    res = ()
    leftv = v
    while leftv in refDict:
        if isinstance(refDict[leftv], tuple):
            rightv = refDict[leftv][1]
            leftv = refDict[leftv][0]
            res = (rightv,) + res
        else:
            leftv = refDict[leftv]
    res = (leftv,) + res
    return res

def hasNonSSAVersion(v):
    if isinstance(v, LocalIRVariable) or isinstance(v, StateIRVariable) or isinstance(v, TemporaryVariableSSA) or isinstance(v, ReferenceVariableSSA):
       return True
    return False

def isComment(c):
    if str.strip(c).startswith("//"):
        return True
    if str.strip(c).startswith("*"):
        return True
    if str.strip(c).startswith("/*"):
        return True
    return False