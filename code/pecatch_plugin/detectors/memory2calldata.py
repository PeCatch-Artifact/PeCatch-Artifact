from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations.phi import Phi
from slither.slithir.operations.internal_call import InternalCall
from slither.core.solidity_types.mapping_type import MappingType
from slither.core.solidity_types.array_type import ArrayType
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.user_defined_type import UserDefinedType
from slither.core.declarations.structure import Structure
from slither.slithir.variables.temporary import TemporaryVariable
from slither.slithir.variables.local_variable import LocalVariable
from slither.slithir.variables.tuple import TupleVariable
from slither.slithir.operations.unpack import Unpack

from .cfg import *
from.utils import *


def detect(f: "Function"):
    bugs = {}
    mpars = {}
    for i in range(len(f.parameters)):
        p = f.parameters[i]
        if p.location == "memory":
            if isinstance(p.type, UserDefinedType) and isinstance(p.type.type, Structure):
                mpars[p] = i
            elif isinstance(p.type, MappingType) or isinstance(p.type, ArrayType) \
                or (isinstance(p.type, ElementaryType) and p.type.is_dynamic):
                mpars[p] = i

    removeIndex = getChanged(f, mpars)

    for p,i in mpars.items():
        if i not in removeIndex:
            bugs[i] = p  
    return bugs

def getChanged(f, mpars):
    removeIndex = []
    refv = getRefDict(f)
    tuple_var = []
    for node in f.nodes:
        for ir in node.irs_ssa:
            if isinstance(ir, Phi):
                continue
            leftval = None
            if isinstance(ir, Unpack):
                if ir.lvalue in tuple_var:
                    leftval = ir.lvalue
            elif assignValue(ir):
                if isinstance(ir.lvalue, TupleVariable):
                    tuple_var.append(ir.lvalue)
                else:
                    leftval = ir.lvalue
            if leftval and not isinstance(leftval, TemporaryVariable):
                leftval = getRefVar(leftval, refv)
                if isinstance(leftval, tuple):
                    if leftval[0] in mpars:
                        index = mpars[leftval[0]]
                        if index in mpars:
                            if belongto(mpars[index], leftval):
                                removeIndex.append(index)
                        else:
                            removeIndex.append(index)
                elif leftval in mpars:
                    removeIndex.append(mpars[leftval])
    return removeIndex

def filter(functions, candidates):
    for f in functions:
        refv = getRefDict(f)
        for node in f.nodes:
            for ir in node.irs_ssa:
                if isinstance(ir, InternalCall) and ir.function in candidates:
                    mpars = {}
                    removeIndex = []
                    for t in candidates[ir.function]:
                        p = ir.arguments[t]
                        if isinstance(p, Constant) or not isinstance(p, LocalVariable) or p.location != "calldata":
                            removeIndex.append(t)
                            continue
                        p = getRefVar(p, refv)
                        if isinstance(p, tuple):
                            mpars[p[0]] = t
                            mpars[t] = p
                        else:
                            mpars[p] = t
                    removeIndex.extend(getChanged(f, mpars))
                    for i in removeIndex:
                        del candidates[ir.function][i]

def belongto(a, b):
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True


class Memory2Calldata(AbstractDetector):  
    """
    Documentation
    """

    ARGUMENT = "mem-call" 
    HELP = "Help printed by slither"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "Detects immutable function parameters in memory"

    WIKI_TITLE = "NONE"
    WIKI_DESCRIPTION = "NONE"
    WIKI_EXPLOIT_SCENARIO = "NONE"
    WIKI_RECOMMENDATION = "NONE"

    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            if not c.is_interface:
                bugs = {}
                candidates = {}
                for f in c.functions_declared:
                    if f.is_constructor or not f.is_implemented:
                        continue
                    if f.visibility == "external":
                        bugs[f] = detect(f)
                    elif f.visibility == "public":
                        candidates[f] = detect(f)
                filter(c.functions_declared, candidates)
                bugs.update(candidates)
                for f in bugs:
                    if len(bugs[f]) > 0:
                        info = [ str(f.name) + '() @ ' + str(f.source_mapping) + '\n' ]

                        i = 0
                        for k,v in bugs[f].items():
                            info.append("[BUG:] ")
                            info.append(str(i))
                            info.append(": ") 
                            info.append(v.name + " (" + str(v.source_mapping) + ")")
                            info.append("\n")
                            i += 1
                        info.append("\n")
                        
                        res = self.generate_result(info)
                        results.append(res)

        return results
