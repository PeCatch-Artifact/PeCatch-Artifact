
from slither.core.declarations import Function
from slither.core.expressions.identifier import Identifier
from slither.core.expressions.member_access import MemberAccess
from slither.core.expressions.index_access import IndexAccess
from slither.core.variables.state_variable import StateVariable
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations import OperationWithLValue
from slither.slithir.operations.assignment import Assignment
from slither.slithir.operations.unary import Unary
from slither.slithir.operations.binary import Binary
from slither.slithir.operations.call import Call
from slither.slithir.operations.delete import Delete
from slither.slithir.operations.event_call import EventCall
from slither.slithir.operations.library_call import LibraryCall
from slither.slithir.operations.high_level_call import HighLevelCall
from slither.slithir.operations.low_level_call import LowLevelCall
from slither.slithir.operations.internal_call import InternalCall
from slither.slithir.operations.solidity_call import SolidityCall
from slither.slithir.operations.index import Index
from slither.slithir.operations.length import Length
from slither.slithir.operations.phi import Phi
from slither.slithir.operations.member import Member
from slither.slithir.operations.codesize import CodeSize
from slither.slithir.variables.state_variable import StateIRVariable
from slither.slithir.variables.local_variable import LocalIRVariable
from slither.slithir.variables.reference_ssa import ReferenceVariableSSA
from slither.slithir.variables.temporary_ssa import TemporaryVariableSSA
from slither.slithir.variables.reference import ReferenceVariable
from slither.slithir.variables.constant import Constant
from slither.slithir.variables.temporary import TemporaryVariable
from slither.slithir.variables.local_variable import LocalVariable
from slither.core.variables.variable import Variable
from slither.core.solidity_types.user_defined_type import UserDefinedType
from slither.core.declarations.contract import Contract
from slither.core.declarations.structure import Structure
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.array_type import ArrayType
from slither.core.solidity_types.mapping_type import MappingType


from .cfg import *
from .loop import *
from .allocinloop import getAllBlocks,changeStack

def getGenSet(ir, defDict):
    setGen = set()

    if ".pop(" in str(ir.node.expression) or ".push(" in str(ir.node.expression):
        return setGen

    # print(ir.node, ir, type(ir))
    if isinstance(ir, Phi):
        pass
    elif isinstance(ir, ReferenceVariableSSA):
        pass
    elif isinstance(ir, Index):
        pass
    elif isinstance(ir, EventCall) or isinstance(ir, HighLevelCall) or isinstance(ir, InternalCall) or isinstance(ir, LowLevelCall) or isinstance(ir, SolidityCall):
        if isinstance(ir, EventCall):
            call = ir.expression
        else:
            call = ir
        args = call.arguments
        if isinstance(ir, LibraryCall):
            if args and not isinstance(args[0].type, ElementaryType):
                args = args[1:]
            # print(ir.node, ir, type(ir), args[0], args[0].type, type(args[0].type))
        for arg in args:  
            if storageAndNotConstant(arg):
                if not isinstance(arg.type, ArrayType) and not isinstance(arg.type, MappingType):
                    setGen.add(arg.non_ssa_version)
            elif isinstance(arg, Identifier) and storageAndNotConstant_call(arg):
                if not isinstance(arg.type, ArrayType) and not isinstance(arg.type, MappingType):
                    setGen.add(arg.value)
            elif isinstance(arg, ReferenceVariable):
                tmpSet = getAllStateTuple(arg, defDict)
                if tmpSet:
                    setGen.add(tmpSet[0])
            else:
                getAllCallRead(arg, setGen) 
    elif isinstance(ir, Delete):
        for v in ir.read:
            if isinstance(v, ReferenceVariableSSA):
                if isinstance(defDict[v][0], Member):
                    continue   
                assert(isinstance(defDict[v][0], Index))
                if storageAndNotConstant(defDict[v][0].variable_right):
                    setGen.add(defDict[v][0].variable_right.non_ssa_version)
    elif isinstance(ir, Member):
        return setGen
    elif isinstance(ir, Assignment) and isinstance(ir.lvalue, TemporaryVariable):
        return setGen
    elif isinstance(ir, Length):
        return setGen
    else: 
        if isinstance(ir, Assignment) and isinstance(ir.lvalue, ReferenceVariableSSA):
            v = ir.lvalue
            if isinstance(defDict[v][0], Index):
                if storageAndNotConstant(defDict[v][0].variable_right):
                    setGen.add(defDict[v][0].variable_right.non_ssa_version)
            tmpSet = getAllStateTuple(v, defDict)
            if tmpSet and len(tmpSet[0]) > 2 and tmpSet[1]:
                setGen.add(tmpSet[0][:-1])
        for v in ir.read: 
            if storageAndNotConstant(v):
                setGen.add(v.non_ssa_version)
            elif isinstance(v, ReferenceVariableSSA):
                if isinstance(defDict[v][0], Length):
                    if storageAndNotConstant(defDict[v][0].value):
                        setGen.add((defDict[v][0].value.non_ssa_version, "length"))
                elif isinstance(defDict[v][0], Assignment):
                    for i in defDict[v][0].read:
                        if storageAndNotConstant(i):
                            setGen.add(i.non_ssa_version)
                elif isinstance(defDict[v][0], CodeSize):
                    if storageAndNotConstant(defDict[v][0].value):
                        setGen.add(defDict[v][0].value.non_ssa_version)
                elif isinstance(defDict[v][0], Call):
                    continue
                else:
                    if not isinstance(defDict[v][0], Index) and not isinstance(defDict[v][0], Member):
                        print(ir,v, defDict[v][0].expression, type(defDict[v][0]))
                    if not isinstance(defDict[v][0], Member):
                        assert(isinstance(defDict[v][0], Index))
                
                    if storageAndNotConstant(defDict[v][0].variable_right):
                        setGen.add(defDict[v][0].variable_right.non_ssa_version)
                    
                    tmpSet = getAllStateTuple(v, defDict)
                    if tmpSet:
                        setGen.add(tmpSet[0])
    return setGen

def getAllCallRead(arg, targetSet):
    tmpSet = ()
    v = arg
    isSateVar = False
    while isinstance(v, MemberAccess) or isinstance(v, IndexAccess):
        if isinstance(v, MemberAccess):
            if isinstance(v.expression, Identifier) and storageAndNotConstant_call(v.expression):
                tmpSet = (v.expression.value, v.member_name) + tmpSet
                isSateVar = True
                break
            tmpSet = (v.member_name,) + tmpSet
            v = v.expression
        if isinstance(v, IndexAccess):
            if isinstance(v.expression_left, Identifier) and storageAndNotConstant_call(v.expression_left):
                tmpSet = (v.expression_left.value, v.expression_right) + tmpSet
                isSateVar = True
                break
            tmpSet = (v.expression_right,) + tmpSet
            v = v.expression_left
    if isSateVar:
        subSet = ()
        for t in tmpSet:
            targetSet.add(subSet + (t,))
            subSet += (t,)

def getAllStateTuple(v, defDict):
    if isinstance(v.type, ArrayType) or isinstance(v.type, MappingType):
        return None
    tmpIr = defDict[v][0]
    tmpSet = ()
    isSateVar = False
    isStruct = False
    while isinstance(tmpIr, Index) or isinstance(tmpIr, Member):
        if len(tmpSet) < 1 and isinstance(tmpIr.variable_left, Variable) and isinstance(tmpIr.variable_left.type, UserDefinedType) \
            and isinstance(tmpIr.variable_left.type.type, Structure):
            isStruct = True
        if storageAndNotConstant(tmpIr.variable_left):
            rightVar = tmpIr.variable_right
            if isinstance(tmpIr.variable_right, ReferenceVariable):
                rightVar = getRefVar(tmpIr.variable_right, defDict)
                if not rightVar:
                    tmpSet = (tmpIr.variable_left.non_ssa_version, rightVar) + tmpSet
                else:
                    tmpSet = (tmpIr.variable_left.non_ssa_version,) + rightVar + tmpSet
            else:
                tmpSet = (tmpIr.variable_left.non_ssa_version, rightVar) + tmpSet
            isSateVar = True
            break
        
        rightVar = tmpIr.variable_right
        if isinstance(tmpIr.variable_right, ReferenceVariable):
            rightVar = getRefVar(tmpIr.variable_right, defDict)
            if not rightVar:
                tmpSet = (rightVar,) + tmpSet
            else:
                tmpSet = rightVar + tmpSet
        else:
            tmpSet = (rightVar,) + tmpSet
        if tmpIr.variable_left in defDict:
            tmpIr = defDict[tmpIr.variable_left][0]
        else:
            break
    if isSateVar:
        return (tmpSet, isStruct)

def getRefVar(v, defDict):
    res = ()
    while isinstance(v, ReferenceVariable):
        if v not in defDict:
            return None
        tmpIr = defDict[v][0]
        if isinstance(tmpIr, Index) or isinstance(tmpIr, Member):
            res += (tmpIr.variable_left.non_ssa_version,)
            v = tmpIr.variable_right
        else:
            return None
    if hasNonSSAVersion(tmpIr.variable_right):
        res+=(tmpIr.variable_right.non_ssa_version,)
    else:
        res+=(tmpIr.variable_right,)
    return res

def storageAndNotConstant(var):
    if (isinstance(var, StateIRVariable) or (isinstance(var, LocalVariable) and var.location == "storage")) \
        and not var.is_constant and not var.non_ssa_version.is_immutable:
        if isinstance(var.type, UserDefinedType):
            if isinstance(var.type.type, Contract):
                return False
        return True
    return False

def storageAndNotConstant_call(arg):
    return (isinstance(arg.value, StateVariable) or (isinstance(arg.value, LocalVariable) and arg.value.location == "storage")) and not arg.value.is_constant and not arg.value.is_immutable

def getKillSet(ir, defDict):
    setKill = set()

    if isinstance(ir, OperationWithLValue) and ir.lvalue:
        
        if isinstance(ir, Phi):
            return setKill
        
        if isinstance(ir, Index) or isinstance(ir, Member):
            return setKill

        if storageAndNotConstant(ir.lvalue):
            if isinstance(ir, Assignment):
                setKill.add(ir.lvalue.non_ssa_version)
            elif isinstance(ir, Delete) and isinstance(ir.variable, ReferenceVariableSSA):
                assert(isinstance(defDict[ir.variable][0], Index))
                setKill.add((defDict[ir.variable][0].variable_left.non_ssa_version, defDict[ir.variable][0].variable_right))
            elif isinstance(ir, Binary):
                setKill.add(ir.lvalue.non_ssa_version)


        elif isinstance(ir.lvalue, ReferenceVariableSSA):
            if isinstance(defDict[ir.lvalue][0], Length):
                if storageAndNotConstant(defDict[ir.lvalue][0].lvalue):
                    setKill.add(ir.lvalue.non_ssa_version)
                return setKill
            elif isinstance(defDict[ir.lvalue][0], Assignment):
                return setKill
            elif isinstance(defDict[ir.lvalue][0], CodeSize):
                if storageAndNotConstant(defDict[ir.lvalue][0].lvalue):
                    setKill.add(defDict[ir.lvalue][0].lvalue.non_ssa_version)
            elif isinstance(defDict[ir.lvalue][0], Call):
                return setKill
            else:
                if not isinstance(defDict[ir.lvalue][0], Index) and not isinstance(defDict[ir.lvalue][0], Member):
                    print(ir,type(ir), ir.lvalue, defDict[ir.lvalue][0].expression, type(defDict[ir.lvalue][0]))
                if not isinstance(defDict[ir.lvalue][0], Member):
                    assert(isinstance(defDict[ir.lvalue][0], Index))

                tmpRes = getAllStateTuple(ir.lvalue, defDict)
                if tmpRes:
                    setKill.add(tmpRes[0])

    return setKill

def computeDef(f: "Function"):
    resDict = {}
    for node in f.nodes:
        for ir in node.irs_ssa:
            if isinstance(ir, OperationWithLValue) and ir.lvalue:
                if ir.lvalue not in resDict:
                    resDict[ir.lvalue] = []
                resDict[ir.lvalue].append(ir)
    
    return resDict
    
def compareAfterSets(set1, set2):
    if len(set1) != len(set2):
        return False

    for ir in set1:
        if ir not in set2:
            return False
        
        for it in set1[ir]:
            if it not in set2[ir]:
                return False

    return True

def computeBeforeAfter(f, defDict):
    beforeSets = {}
    afterSets = {}
    worklist = []

    predInsts, succInsts = generateIICFG(f)

    for node in f.nodes:
        for ir in node.irs_ssa:
            beforeSets[ir] = set()
            afterSets[ir] = set()
            worklist.append(ir)

    while len(worklist) > 0:
        ii = worklist.pop(0)

        newBefore = set()
        for pred in predInsts[ii]: 
            newBefore = newBefore.union(afterSets[pred])
        
        genSet = getGenSet(ii, defDict)
        killSet = getKillSet(ii, defDict)

        beforeSets[ii] = newBefore
        newAfter = genSet.union(newBefore) - killSet

        if not compareSets(newAfter, afterSets[ii]):
            afterSets[ii] = newAfter
            for succ in succInsts[ii]:
                worklist.append(succ)

    return beforeSets, afterSets

def compareSets(set1, set2):
    if len(set1) != len(set2):
        return False
    for item in set1:
        if item not in set2:
            return False
    return True 

def assignValue(ir):
    return isinstance(ir, OperationWithLValue) and (isinstance(ir, Assignment) or isinstance(ir, Binary) or isinstance(ir, Unary) or isinstance(ir, Call) or isinstance(ir, CodeSize))

def hasNonSSAVersion(v):
    if isinstance(v, LocalIRVariable) or isinstance(v, StateIRVariable) or isinstance(v, TemporaryVariableSSA) or isinstance(v, ReferenceVariableSSA):
       return True
    return False

def filterValueChange(ir, var, defDict):
    if not assignValue(ir):
        return var
    if not var or len(var) < 1:
        return var
    res = set()
    lvalue = ir.lvalue
    if isinstance(lvalue, ReferenceVariable):
        lvalue = getRefVar(lvalue, defDict)
    for v in var:
        if v == lvalue:
            continue
        elif isinstance(v, tuple):
            if isinstance(lvalue, tuple):
                if lvalue[0] in v:
                    index = v.index(lvalue[0]) 
                    if index+len(lvalue) < len(v) and v[index:index+len(lvalue)] == lvalue:
                        continue
            else:
                if lvalue in v:
                    continue
        res.add(v)
    return res

def checkLive(s, visited, sameVar, ir1, ir2, beforeSets, defDict):
    visited[s] = True

    if ir1.node == ir2.node and ir1 in s.irs_ssa:
        index1 = s.irs_ssa.index(ir1)
        index2 = s.irs_ssa.index(ir2)
        for i in range(index1+1, index2+1):
            sameVar = sameVar.intersection(beforeSets[s.irs_ssa[i]])
            if i < index2:
                sameVar = filterValueChange(s.irs_ssa[i], sameVar, defDict)
            if not sameVar or len(sameVar) < 1:
                return False     
        return sameVar
    elif ir1 in s.irs_ssa:
        index = s.irs_ssa.index(ir1)
        for i in range(index+1, len(s.irs_ssa)):
            sameVar = sameVar.intersection(beforeSets[s.irs_ssa[i]])
            sameVar = filterValueChange(s.irs_ssa[i], sameVar, defDict)
            if not sameVar or len(sameVar) < 1:
                return False       
    elif ir2 in s.irs_ssa:
        index = s.irs_ssa.index(ir2)
        for i in range(0, index+1):
            sameVar = sameVar.intersection(beforeSets[s.irs_ssa[i]])
            if i < index:
                sameVar = filterValueChange(s.irs_ssa[i], sameVar, defDict)
            if not sameVar or len(sameVar) < 1:
                return False      
        return sameVar
    else:
        for ir in s.irs_ssa:
            sameVar = sameVar.intersection(beforeSets[ir])
            sameVar = filterValueChange(ir, sameVar, defDict)
            if not sameVar or len(sameVar) < 1:               
                return False    
 
    for n in s.sons:
        if n not in visited or not visited[n]:
            res = checkLive(n, visited, sameVar, ir1, ir2, beforeSets, defDict)
            if isinstance(res, set):
                return res
    visited[s] = False

def checkNoDef(s, visited, var, ir1, ir2, defDict):
    visited[s] = True

    if ir1 in s.irs_ssa:
        index = s.irs_ssa.index(ir1)
        for i in range(index+1, len(s.irs_ssa)):
            if var in getKillSet(s.irs_ssa[i], defDict) or indexChanged(s.irs_ssa[i], var, defDict):
                return False        
    elif ir2 in s.irs_ssa:
        index = s.irs_ssa.index(ir2)
        for i in range(0, index):
            if var in getKillSet(s.irs_ssa[i], defDict) or indexChanged(s.irs_ssa[i], var, defDict):
                return False        
        return True
    else:
        for ir in s.irs_ssa:
            if var in getKillSet(ir, defDict) or indexChanged(ir, var, defDict):
                return False     
 
    for n in s.sons:
        if n not in visited or not visited[n]:
            res = checkNoDef(n, visited, var, ir1, ir2, defDict)
            if res == True:
                return res
    visited[s] = False

def indexChanged(ir, var, defDict):
    if not assignValue(ir):
        return False
    if not isinstance(var, tuple):
        return False
    
    leftV = ir.lvalue
    if isinstance(leftV, ReferenceVariable):
        leftV = getRefVar(leftV, defDict)
    if leftV in var:
        return True
    if isinstance(leftV, tuple):
        if leftV[0] in var:
            index = var.index(leftV[0]) 
            if index+len(leftV) < len(var) and var[index:index+len(leftV)] == leftV:
                return True
    return False
    
def detectRedundantSLoad(f: "Function"):
    defDict = computeDef(f)
    beforeSets, afterSets = computeBeforeAfter(f, defDict)
    dominators = computeDominators(f)

    bugs = []

    for node in f.nodes:
        for ir in node.irs_ssa:
            gen_ir = getGenSet(ir, defDict).intersection(beforeSets[ir])
            for d in dominators[ir]:
                gen_d = getGenSet(d, defDict)
                sameVar = gen_ir.intersection(gen_d)
                if len(sameVar) > 0:
                    sameVar = checkLive(d.node, {}, sameVar, d, ir, beforeSets, defDict)
                    if sameVar and len(sameVar) > 0:
                        for v in sameVar:
                            if (v, d, ir) not in bugs:
                                bugs.append((v, d, ir))
    
    bugs += detectSStoreAndSLoad(f, defDict, dominators)
                        
    return bugs

def detectSStoreAndSLoad(f: "Function", defDict, dominators):
    bugs = []
    
    for node in f.nodes:
        for ir in node.irs_ssa:
            gen = getGenSet(ir, defDict)
            for d in dominators[ir]:
                if isinstance(d, Assignment):
                    if isinstance(d.lvalue, StateIRVariable):
                        leftV = d.lvalue.non_ssa_version
                    elif isinstance(d.lvalue, ReferenceVariable):
                        leftV = getRefVar(d.lvalue, defDict)
                    else:
                        continue
                    if  leftV in gen:
                        if checkNoDef(d.node, {}, leftV, d, ir, defDict) == True:
                            if (leftV, d, ir) not in bugs:
                                bugs.append((leftV, d, ir))
            
    return bugs

def filterStackTooDeep(f, bugs):
    blocks = getAllBlocks(f.source_mapping)
    stack = []
    for p in f.parameters:
        stack.insert(0,p)
        if p.location == "calldata":         
            stack.insert(0,"calldata length")
    block_var_decl = {}
    new_vars = {}
    for t in bugs:
        if t[0] in new_vars:
            node_arr = new_vars[t[0]]
            if t[1].node not in node_arr:
                node_arr.append(t[1].node)
            if t[2].node not in node_arr:
                node_arr.append(t[2].node)
        else:
            new_vars[t[0]] = [t[1].node, t[2].node]
    can_var = []
    checkPath(f.entry_point, {}, stack, blocks, block_var_decl, new_vars, can_var)
    # print(can_var)
    new_bugs = []
    for t in bugs:
        if t[0] in can_var:
            new_bugs.append(t)
    return new_bugs

def addNewVar(new_vars, node, stack, blocks, block_var_decl):
    added = []
    for v in new_vars:
        if new_vars[v][0] == node:
            cline = node.source_mapping.lines[0]
            c_scol = node.source_mapping.starting_column
            c_ecol = node.source_mapping.ending_column
            for b in blocks:
                start_line = b[0]
                start_col = b[1]
                end_line = b[2]
                end_col = b[3]
                if (cline > start_line and cline < end_line) or (cline == start_line and c_scol > start_col) or (cline == end_line and c_ecol < end_col):
                    if (start_line,start_col) not in block_var_decl:
                        block_var_decl[(start_line,start_col)] = []
                    block_var_decl[(start_line,start_col)].append(v)
            stack.insert(0,v) 
            added.append(v)
        elif node in new_vars[v]:
            if stack.index(v) > 15:
                print(node, v)
                return (False,v)
            added.append(v)
    return (True, added) if len(added) > 0 else None

def checkPath(node, visited, stack, blocks, block_var_decl, new_vars, bugs):
    visited[node] = True
    if node.will_return:
        return stack
    new_res = addNewVar(new_vars, node, stack, blocks, block_var_decl)
    if new_res and not new_res[0]:
        return False

    if changeStack(node, stack, blocks, block_var_decl) == False:
        print(node)
        return False
    if new_res and new_res[0]:
        bugs.extend(new_res[1])
    for suc in node.sons:
        if suc not in visited or not visited[suc]:
            res = checkPath(suc, visited, stack.copy(), blocks, block_var_decl.copy(), new_vars, bugs)
            if res:
                return res
    visited[node] = False


class RedundantSLoad(AbstractDetector):  
    """
    Documentation
    """

    ARGUMENT = "redundant-sload" 
    HELP = "Help printed by slither"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "Detecting redundant sload"

    WIKI_TITLE = "NONE"
    WIKI_DESCRIPTION = "NONE"
    WIKI_EXPLOIT_SCENARIO = "NONE"
    WIKI_RECOMMENDATION = "NONE"

    def _detect(self):
        results = []
        for c in self.contracts:
            if "@" in c.source_mapping.filename.absolute:
                continue
            if c.is_interface:
                continue

            for f in c.functions_and_modifiers:
                if not f.is_implemented:
                    continue
                bugs = detectRedundantSLoad(f)
                if len(bugs) > 0:
                    bugs = filterStackTooDeep(f, bugs)

                if len(bugs) > 0:
                    info = [ str(f.name) + '() @ ' + str(f.source_mapping) + '\n' ]

                    i = 0
                    while i < len(bugs):
                        info.append("[BUG:] ")
                        info.append(str(i))
                        info.append(": ") 
                        if isinstance(bugs[i][0], tuple):
                            var_str = ""
                            for t in bugs[i][0]:
                                if isinstance(t, str):
                                    var_str += t + " "
                                else:
                                    var_str += t.name + " "
                            info.append(var_str)
                        else:
                            info.append(str(bugs[i][0]))
                        info.append("\t")
                        info.append(str(bugs[i][1].node.source_mapping))
                        info.append("\t")
                        info.append(str(bugs[i][2].node.source_mapping))
                        info.append("\n")
                        i += 1
                    info.append("\n")
                    
                    res = self.generate_result(info)
                    results.append(res)

        return results