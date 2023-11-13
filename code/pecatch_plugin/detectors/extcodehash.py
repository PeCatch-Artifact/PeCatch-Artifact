from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.core.declarations import Function
from slither.slithir.operations.solidity_call import SolidityCall
from slither.slithir.operations.assignment import Assignment
from slither.slithir.operations.binary import Binary,BinaryType

from . cfg import *

       

def detectExtcodehash(f: "Function"):
    con = 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470
    bugs = []
    varList = []
    conList = []
    irDict = {}
    for node in f.nodes:
        for ir in node.irs_ssa:
            if isinstance(ir, SolidityCall):
                if "extcodehash" in ir.function.name:
                    varList.append(ir.lvalue)
            if isinstance(ir, Assignment):
                if len(ir.read) == 1 and ir.read[0] in varList and ir.lvalue not in varList:
                    varList.append(ir.lvalue)
                    irDict[ir.lvalue] = [ir]
                elif ir.lvalue in varList:
                    varList.remove(ir.lvalue)

                if len(ir.read) == 1 and ir.read[0] == con and ir.lvalue not in conList:
                    conList.append(ir.lvalue)
                elif ir.lvalue in conList:
                    conList.remove(ir.lvalue)

            if isinstance(ir, Binary):
                if ir.variable_left in varList and ir.variable_right == 0: 
                    if ir.type is BinaryType.EQUAL or ir.type is BinaryType.NOT_EQUAL:
                        irDict[ir.variable_left].append(ir)
                if ir.variable_right in varList and ir.variable_left == 0:
                    if ir.type is BinaryType.EQUAL or ir.type is BinaryType.NOT_EQUAL:
                        irDict[ir.variable_right].append(ir)

                if ir.variable_left in varList and (ir.variable_right == con or ir.variable_right in conList): 
                    if ir.type is BinaryType.EQUAL or ir.type is BinaryType.NOT_EQUAL:
                        irDict[ir.variable_left].append(ir)
                if ir.variable_right in varList and (ir.variable_left == con or ir.variable_left in conList): 
                    if ir.type is BinaryType.EQUAL or ir.type is BinaryType.NOT_EQUAL:
                        irDict[ir.variable_right].append(ir)
    
    for v in irDict:
        if len(irDict[v]) == 3:
            bugs.append(irDict[v])
    return bugs


class Extcodehash(AbstractDetector):  
    """
    Documentation
    """

    ARGUMENT = "extcodehash" 
    HELP = "Help printed by slither"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "Detecting excodehash"

    WIKI_TITLE = "NONE"
    WIKI_DESCRIPTION = "NONE"
    WIKI_EXPLOIT_SCENARIO = "NONE"
    WIKI_RECOMMENDATION = "NONE"

    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:

                bugs = detectExtcodehash(f)
                if len(bugs) > 0:
                    info = [ str(f.name) + '() @ ' + str(f.source_mapping) + '\n' ]

                    i = 0
                    while i < len(bugs):
                        info.append("[BUG:] ")
                        info.append(str(i))
                        info.append(": ") 
                        info.append(str(bugs[i][0].node.source_mapping))
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
