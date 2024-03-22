from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.variables.state_variable import StateVariable
from slither.slithir.variables.constant import Constant
from slither.core.declarations.solidity_variables import SolidityVariableComposed
from slither.core.solidity_types.elementary_type import ElementaryType

from plugin.detectors.loop import *
from plugin.detectors.utils import *
from plugin.detectors.cfg import *


def detect(f):
    loops = []
    backedges = findBackedges(f.entry_point)
    for b in backedges:
        body = getLoopBody(b)
        loops.append(body)
    if not loops:
        return []
    
    bugs = []
    refDict = getRefDict(f)
    predInsts, succInsts = generateIICFG(f)
    for l in loops:
        resIr = detectOverflow(l, refDict, predInsts)
        if resIr:
            bugs.append(resIr)
                
    return bugs

def detectOverflow(loop, refDict, predInsts):
    compareIr, loopVar, boundVar = getLoopExitCondition(loop)
    # print(compareIr, loopVar, boundVar)
    if not compareIr or not loopVar or not boundVar:
        return None
    
    if not isinstance(loopVar.type, ElementaryType):
        return None
    
    if not loopVar.type.size <= 16:
        return None
    
    boundVar_no_index = ()
    for v in boundVar:
        if not isinstance(v, Constant) and v.non_ssa_version == loopVar:
            continue
        boundVar_no_index+=(v,)
    
    if len(boundVar_no_index) == 1:
        if isinstance(boundVar_no_index[0], Constant):
            if boundVar_no_index[0].value < pow(2,loopVar.type.size):
                return None
            else:
                return compareIr
    
    for v in boundVar_no_index:
        related = getRelatedVar(v, refDict, None, predInsts)
        if isinstance(related, tuple):
            for item in related:
                if isinstance(item, StateVariable) or isinstance(item, SolidityVariableComposed):
                    return compareIr
        else:
            if isinstance(related, StateVariable) or isinstance(related, SolidityVariableComposed):
                return compareIr

    return None


class LoopOverflow(AbstractDetector):
    """
    Documentation
    """

    ARGUMENT = 'loop-overflow'
    HELP = 'Help printed by slither'
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = 'Detects integer overflow in loop'

    WIKI_TITLE = 'NONE'
    WIKI_DESCRIPTION = 'NONE'
    WIKI_EXPLOIT_SCENARIO = 'NONE'
    WIKI_RECOMMENDATION = 'NONE'

    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            if c.is_interface:
                continue
            for f in c.functions_and_modifiers:
                if not f.is_implemented:
                    continue
                bugs = detect(f)
                if len(bugs) > 0:
                    info = [ str(f.name) + '() @ ' + str(f.source_mapping) + '\n' ]

                    i = 0
                    while i < len(bugs):
                        info.append("[BUG:] ")
                        info.append(str(i))
                        info.append(": ") 
                        info.append(bugs[i].node)
                        info.append("\t")
                        info.append(str(bugs[i].node.source_mapping))
                        info.append("\n")
                        i += 1
                    info.append("\n")
                    
                    res = self.generate_result(info)
                    results.append(res)

        return results