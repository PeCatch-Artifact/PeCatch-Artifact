from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.core.solidity_types.elementary_type import ElementaryType

from . cfg import *


def checkSingleSlotBool(svars):
    boollist = []
    currentSlotLeft = 32
    slotLayout = []
    for v in svars:
        size = v.type.storage_size[0]
        if len(slotLayout) < 1:
            slotLayout.append([v])
            currentSlotLeft -= size
        else:
            if currentSlotLeft < size:
                slotLayout.append([v])
                currentSlotLeft = 32 - size
            else :
                slotLayout[-1].append(v)
                currentSlotLeft -= size

    for s in slotLayout:
        if len(s) == 1:
            if isinstance(s[0].type, ElementaryType) and s[0].type.name=="bool":
                boollist.append(s[0])

    return boollist

class Bool(AbstractDetector):  
    """
    Documentation
    """

    ARGUMENT = "bool" 
    HELP = "Help printed by slither"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "Detecting bool"

    WIKI_TITLE = "NONE"
    WIKI_DESCRIPTION = "NONE"
    WIKI_EXPLOIT_SCENARIO = "NONE"
    WIKI_RECOMMENDATION = "NONE"

    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            bugs = checkSingleSlotBool(c.state_variables)
            if len(bugs) > 0:
                info = [ str(c.name) + '() @ ' + str(c.source_mapping) + '\n' ]

                i = 0
                for v in bugs:
                    info.append("[BUG:] ")
                    info.append(str(i))
                    info.append("\t")
                    info.append(v)
                    info.append("\n")
                    i += 1
                info.append("\n")
                
                res = self.generate_result(info)
                results.append(res)

        return results
