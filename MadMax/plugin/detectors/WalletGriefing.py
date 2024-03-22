from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations.send import Send
from slither.slithir.operations.transfer import Transfer
from slither.slithir.operations.low_level_call import LowLevelCall
from slither.slithir.operations.solidity_call import SolidityCall
from slither.core.solidity_types.elementary_type import ElementaryType

from plugin.detectors.utils import *
from plugin.detectors.loop import *


def conditionFlowFrom(condVar, originVar, node, visited):
    if node.type == NodeType.ENTRYPOINT or node in visited:
        return False
    
    origins = []
    for ir in reversed(node.irs_ssa):
        if isinstance(ir, OperationWithLValue):
            if not ir.lvalue:
                continue
            if ir.lvalue == condVar or ir.lvalue.non_ssa_version == condVar:
                for v in ir.read:
                    if v == originVar:
                        return True
                origins.extend(ir.read)
            elif ir.lvalue in origins:
                for v in ir.read:
                    if v == originVar:
                        return True
                origins.remove(ir.lvalue)
                origins.extend(ir.read)
    visited.append(node)

    if not origins:
        for pre in node.fathers:
            tmp = conditionFlowFrom(condVar, originVar, pre, visited)
            if tmp:
                return True
            
    for v in origins:
        if isinstance(v, Constant):
            continue
        for pre in node.fathers:
            tmp = conditionFlowFrom(v, originVar, pre, visited)
            if tmp:
                return True
    
    visited.remove(node)
    return False

def detectLoop(loop, increased_arr, refDict, predInsts):
    compareIr, loopVar, boundVar = getLoopExitCondition(loop)
    if not compareIr or not loopVar:
        return None
    
    addressVar, condVar ={}, {}
    for node in loop:
        for ir in node.irs_ssa:
            if isinstance(ir, Send):
                addressVar[ir.destination] = {"ir": ir, "resVar": ir.lvalue}
            elif isinstance(ir, Transfer):
                addressVar[ir.destination] = {"ir": ir}
            elif isinstance(ir, SolidityCall):
                if "revert" in ir.function.name:
                    if node.irs_ssa.index(ir) == 0:
                        for pre in node.fathers:
                            lastIr = pre.irs_ssa[-1]
                            if isinstance(lastIr, Condition):
                                condVar[lastIr.value] = ir
                                break
                elif "assert" in ir.function.name or "require" in ir.function.name:
                    for v in ir.read:
                        if isinstance(v.type, ElementaryType) and "bool" in v.type.name:
                            condVar[v] = ir
                            break
            elif isinstance(ir, Condition):
                for suc in node.sons:
                    if suc.type == NodeType.THROW:
                        condVar[ir.value] = ir
                        break
            elif isinstance(ir, LowLevelCall):
                if ir.function_name == "call":
                    addressVar[ir.destination] = {"ir": ir, "resVar": ir.lvalue}
    
    if not addressVar:
        return None
    
    addressVar_pos = {}
    bugs = []
    for av in addressVar:
        relatedVar = getRelatedVar(av, refDict, None, predInsts)
        if isinstance(relatedVar, tuple) and loopVar in relatedVar and relatedVar[0] in increased_arr:
            if "resVar" not in addressVar[av]:
                bugs.append(addressVar[av]["ir"])
            else:
                addressVar_pos[av] = addressVar[av]   
    
    for var in condVar:
        for av in addressVar_pos:
            if conditionFlowFrom(var, addressVar_pos[av]["resVar"], condVar[var].node, []):
                bugs.append(addressVar[av]["ir"])

    return bugs


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
        tmp = detectLoop(l, increased_arr, refDict, predInsts)
        if tmp:
            bugs.extend(tmp)
    return bugs


class WalletGriefing(AbstractDetector):
    """
    Documentation
    """

    ARGUMENT = 'wallet-grief'
    HELP = 'Help printed by slither'
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = 'Detects non-isolated external calls'

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