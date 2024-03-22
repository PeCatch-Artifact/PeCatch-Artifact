from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations.length import Length
from slither.core.cfg.node import Node, NodeType
from slither.slithir.variables.temporary import TemporaryVariable
from slither.slithir.variables.reference import ReferenceVariable
from slither.slithir.variables.state_variable import StateVariable
from slither.core.declarations.solidity_variables import SolidityVariableComposed
from slither.slithir.operations.solidity_call import SolidityCall
from slither.slithir.operations.phi import Phi

from plugin.detectors.utils import *
from plugin.detectors.loop import *


def isLoadOrStore(target, loopVar, increased_arr, refDict, predInsts):
    origin = getRelatedVar(target, refDict, None, predInsts)

    if not isinstance(origin, tuple):
        return False
                
    if loopVar not in origin:
        return False
    
    return origin[0] in increased_arr

def isBoundBySize(node, var, visited, increased_arr, refDict, predInsts):
    if node.type == NodeType.ENTRYPOINT or node in visited:
        return False
    
    origins = []
    for ir in reversed(node.irs_ssa):
        if isinstance(ir, OperationWithLValue):
            if not ir.lvalue:
                continue
            if ir.lvalue == var or ir.lvalue.non_ssa_version == var:
                if isinstance(ir, Length):
                    if getDynamicArr(ir.value, refDict, increased_arr, predInsts):
                        return True
                origins.extend(ir.read)
            elif ir.lvalue in origins:
                if isinstance(ir, Length):
                    if getDynamicArr(ir.value, refDict, increased_arr, predInsts):
                        return True
                else:
                    origins.remove(ir.lvalue)
                    origins.extend(ir.read)
    visited.append(node)

    if not origins:
        for pre in node.fathers:
            tmp = isBoundBySize(pre, var, visited, increased_arr, refDict, predInsts)
            if tmp:
                return True
            
    for v in origins:
        if isinstance(v, Constant):
            continue
        for pre in node.fathers:
            tmp = isBoundBySize(pre, v, visited, increased_arr, refDict, predInsts)
            if tmp:
                return True
    
    visited.remove(node)
    return False

def detectLoop(f, loop, increased_arr, refDict, predInsts):
    compareIr, loopVar, boundVar = getLoopExitCondition(loop)
    if not compareIr or not loopVar:
        return None
    
    if not isBoundBySize(compareIr.node, compareIr.lvalue, [], increased_arr, refDict, predInsts):
        return False
    
    loadOrStore = False
    for node in loop:
        if node.type == NodeType.IFLOOP:
            continue
        for ir in node.irs_ssa:
            for v in ir.read:
                if isLoadOrStore(v, loopVar, increased_arr, refDict, predInsts):
                    loadOrStore = True
                    break
            if loadOrStore:
                break
            if isinstance(ir, OperationWithLValue):
                if isLoadOrStore(v, loopVar, increased_arr, refDict, predInsts):
                    loadOrStore = True
                    break
        if loadOrStore:
            break
    if not loadOrStore:
        return False
    
    resumble = isBoundByGas(compareIr.node, compareIr.lvalue, [])
    if not resumble:
        return compareIr
    
    loadVar = loadIndex(compareIr.node, loopVar, [])
    if not loadVar:
        return compareIr
    
    if not storeIndexToV(f, loopVar, loadVar, refDict, predInsts):
        return compareIr
    return False

def isBoundByGas(node, var, visited):
    if node.type == NodeType.ENTRYPOINT or node in visited:
        return False
    
    origins = []
    for ir in reversed(node.irs_ssa):
        if isinstance(ir, OperationWithLValue):
            if ir.lvalue == var or ir.lvalue.non_ssa_version == var:
                origins.extend(ir.read)
            elif ir.lvalue in origins:
                if isinstance(ir, SolidityCall) and ir.function.name == "gasleft()":
                    return True
                else:
                    for v in ir.read:
                        if isinstance(v, SolidityVariableComposed):
                            if v.name == "msg.gas":
                                return True
                    origins.remove(ir.lvalue)
                    origins.extend(ir.read)
    visited.append(node)

    if not origins:
        for pre in node.fathers:
            tmp = isBoundByGas(pre, var, visited)
            if tmp:
                return True

    for v in origins:
        if isinstance(v, TemporaryVariable) or isinstance(v, ReferenceVariable):
            for pre in node.fathers:
                tmp = isBoundByGas(pre, v, visited)
                if tmp:
                    return True
                
    visited.remove(node)
    return False

def loadIndex(node, var, visited):
    if node.type == NodeType.ENTRYPOINT or node in visited:
        return False
    
    origins = []
    for ir in reversed(node.irs_ssa):
        if isinstance(ir, OperationWithLValue):
            if ir.lvalue == var or ir.lvalue.non_ssa_version == var:
                for v in ir.read:
                    if isinstance(v, StateVariable):
                        return v
                origins.extend(ir.read)
            elif ir.lvalue in origins:
                origins.remove(ir.lvalue)
                origins.extend(ir.read)
    visited.append(node)

    if not origins:
        for pre in node.fathers:
            tmp = loadIndex(pre, var, visited)
            if tmp:
                return tmp
 
    for v in origins:
        if isinstance(v, Constant):
            continue
        for pre in node.fathers:
            tmp = loadIndex(pre, v, visited)
            if tmp:
                return tmp
    
    visited.remove(node)
    return False

def storeIndexToV(f, loopVar, storeVar, refDict, predInsts):
    storeIr = []
    for node in f.nodes:
        if storeVar.non_ssa_version in node.state_variables_written:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue):
                    if ir.lvalue.non_ssa_version == storeVar.non_ssa_version:
                        storeIr.append(ir)

    for ir in storeIr:
        for v in ir.read:
            related = getRelatedVar(v, refDict, None, predInsts)
            if isinstance(related, tuple):
                if loopVar in related:
                    return True
            else:
                if loopVar == related:
                    return True
    
    return False

def detect(f, increased_arr): 
    loops = []
    backedges = findBackedges(f.entry_point)
    for b in backedges:
        body = getLoopBody(b)
        loops.append(body)
    if not loops:
        return []
    
    refDict = getRefDict(f)
    predInsts, succInsts = generateIICFG(f)
    bugs = []
    for l in loops:
        tmp = detectLoop(f, l, increased_arr, refDict, predInsts)
        if tmp:
            bugs.append(tmp)
    return bugs


class UnboundedMassOp(AbstractDetector):
    """
    Documentation
    """

    ARGUMENT = 'unbounded'
    HELP = 'Help printed by slither'
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = 'Detects unbounded mass operations'

    WIKI_TITLE = 'NONE'
    WIKI_DESCRIPTION = 'NONE'
    WIKI_EXPLOIT_SCENARIO = 'NONE'
    WIKI_RECOMMENDATION = 'NONE'

    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            if c.is_interface:
                continue
            increased_arr = detectIncreasedStorage(c)
            if not increased_arr:
                continue
            for f in c.functions_and_modifiers:
                if not f.is_implemented:
                    continue
                bugs = detect(f, increased_arr)
                if len(bugs) > 0:
                    info = [ str(f.name) + '() @ ' + str(f.source_mapping) + '\n' ]

                    i = 0
                    while i < len(bugs):
                        info.append("[BUG:] ")
                        info.append(str(i))
                        info.append(": ") 
                        info.append(bugs[i].node)
                        info.append("\n")
                        i += 1
                    info.append("\n")
                    
                    res = self.generate_result(info)
                    results.append(res)

        return results