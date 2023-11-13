from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.core.dominators.utils import *
from slither.slithir.operations.binary import Binary, BinaryType
from slither.slithir.operations.solidity_call import SolidityCall
from slither.slithir.operations.condition import Condition
from slither.slithir.operations.assignment import Assignment
from slither.slithir.operations.index import Index
from slither.slithir.operations.member import Member
from slither.slithir.operations.lvalue import OperationWithLValue
from slither.slithir.variables.constant import Constant

from .cfg import *

def detect(f):
    bugs = []
    dominators = computeDominators(f)
    refDict = {}
    for node in f.nodes:
        for ir in node.irs_ssa:
            if isinstance(ir, OperationWithLValue):
                refDict[ir.lvalue] = ir
                
    for node in f.nodes:
        if node.scope.is_checked:
            for ir in node.irs_ssa:
                if isinstance(ir, Binary) and ir.type == BinaryType.SUBTRACTION:
                    for d in dominators[ir]:
                        if isinstance(d, SolidityCall) and "require(bool" in d.function.name:
                            for readVar in d.read:
                                if checkSame(readVar, ir, refDict) and ir not in bugs:
                                    bugs.append(ir)
                                    break
                        elif isinstance(d, Condition):
                            if isInIf(ir, d, dominators) and checkSame(d.value, ir, refDict) and ir not in bugs:
                                bugs.append(ir)
    return bugs


def isInIf(objIr, ifIr, dominators):
    for node in ifIr.node.sons:
        for ir in node.irs_ssa:
            if ir in dominators[objIr] or ir is objIr:
                return True
    return False

def checkSame(tmpVar, subIr, refDict):
    tmpIr = getTmpIr(tmpVar, refDict)
    if tmpIr:
        return isSameMinus(subIr, tmpIr, refDict)
    return None

def getTmpIr(var, refDict):    
    while var in refDict:
        tmpIr = refDict[var]
        if isinstance(tmpIr, Binary):
            if isinstance(tmpIr.variable_left, Constant) and (tmpIr.type == BinaryType.LESS_EQUAL or tmpIr.type == BinaryType.LESS) and tmpIr.variable_right in refDict:
                var = tmpIr.variable_right
            elif isinstance(tmpIr.variable_right, Constant) and (tmpIr.type == BinaryType.GREATER_EQUAL or tmpIr.type == BinaryType.GREATER) and tmpIr.variable_left in refDict:
                var = tmpIr.variable_left
            else:
                return tmpIr
        elif isinstance(tmpIr, Assignment):
            var = tmpIr.rvalue
        else:
            return None


def isSameMinus(subIr, compareIr, refDict):
    minuend = getRefVar(subIr.variable_left, refDict)
    subtractor = getRefVar(subIr.variable_right, refDict)
    compareLeft = getRefVar(compareIr.variable_left, refDict)
    compareRight = getRefVar(compareIr.variable_right, refDict)
    if compareIr.type == BinaryType.LESS_EQUAL or compareIr.type == BinaryType.LESS:
        return compareVar(compareLeft, subtractor) and compareVar(compareRight, minuend)
    elif compareIr.type == BinaryType.GREATER_EQUAL or compareIr.type == BinaryType.GREATER or compareIr.type == BinaryType.SUBTRACTION:
        return compareVar(compareLeft, minuend) and compareVar(compareRight, subtractor)
    return False  

def compareVar(v1, v2):
    if v1 == v2:
        return True
    if isinstance(v1, tuple) and isinstance(v2, tuple) and len(v1) == len(v2):
        for i in range(len(v1)):
            if v1[i] != v2[i]:
                return False
        return True
    return False

def getRefVar(var, refDict):
    if var in refDict:
        res = ()
        while var in refDict:
            if isinstance(refDict[var], Index) or isinstance(refDict[var], Member):
                res = (refDict[var].variable_right,) + res
                var = refDict[var].variable_left
            else:
                break
        res = (var,) + res
        return res
    return var


class SameAsIf(AbstractDetector):  # pylint: disable=too-few-public-methods
    """
    Documentation
    """

    ARGUMENT = "sameasif"  # slither will launch the detector with slither.py --mydetector
    HELP = "Help printed by slither"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "Detecting computation that is the same as a dominating if condition"

    WIKI_TITLE = "NONE"
    WIKI_DESCRIPTION = "NONE"
    WIKI_EXPLOIT_SCENARIO = "NONE"
    WIKI_RECOMMENDATION = "NONE"

    def _detect(self):

        if self.compilation_unit.compiler_version.version < "0.8.0":
            return []

        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                bugs = detect(f)
                if len(bugs) > 0:
                    info = [ str(f.name) + '() @ ' + str(f.source_mapping) + '\n' ]

                    i = 0
                    while i < len(bugs):
                        info.append("[BUG:] ")
                        info.append(str(i))
                        info.append(": ") 
                        info.append(str(bugs[i].node.source_mapping))
                        info.append("\n")
                        i += 1
                    info.append("\n")
                    
                    res = self.generate_result(info)
                    results.append(res)


        return results

