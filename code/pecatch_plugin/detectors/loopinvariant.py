from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.core.cfg.node import Node, NodeType
from slither.slithir.operations.phi import Phi
from slither.slithir.operations.binary import Binary
from slither.slithir.operations.member import Member
from slither.slithir.operations.index import Index
from slither.slithir.operations.length import Length
from slither.slithir.operations.unpack import Unpack
from slither.core.variables.variable import Variable
from slither.slithir.variables.state_variable import StateIRVariable
from slither.slithir.variables.temporary import TemporaryVariable
from slither.slithir.variables.tuple import TupleVariable
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.declarations.contract import Contract

from . cfg import *
from .loop import *
from .utils import *

def detecLoopInvariant(f):
    loops = []
    backedges = findBackedges(f.entry_point)
    for b in backedges:
        body = getLoopBody(b)
        loops.append(body)
    bugs = []
    for l in loops:
        bugs.extend(checkInvariant(l))
                
    return bugs

def isStackType(var):
    return isinstance(var, Variable) and not isinstance(var, Constant) and not var.is_constant and not var.is_immutable and isinstance(var.type, ElementaryType) and not var.type.is_dynamic

def checkInvariant(loop):
    ifNode = loop[0]
    loopVar = None
    if ifNode.type != NodeType.IFLOOP:
        ifNode = loop[-1]
    for ir in ifNode._irs_ssa:
        if isinstance(ir, Binary):
            loopVar = ir.variable_left.non_ssa_version
            break
        
    bugs = []
    refDict = {}
    can_var = {}
    remove_vars = []
    tuple_var = []
    for node in loop:
        for ir in node.irs_ssa:
            if isinstance(ir, Phi):
                continue
            if isinstance(ir, Index) or isinstance(ir, Member):
                refDict[ir.lvalue] = (ir.variable_left, ir.variable_right)
            elif isinstance(ir, Length):
                refDict[ir.lvalue] = (ir.value, "length")
            elif isinstance(ir, Unpack):
                if ir.tuple in tuple_var:
                    left_var = getRefVar(ir.lvalue, refDict)
                    remove_vars.append(left_var)
            else:
                for v in ir.read:
                    v_non_ssa = v
                    if hasNonSSAVersion(v):
                        v_non_ssa = v.non_ssa_version
                    if isStackType(v_non_ssa):
                        if v not in refDict and isinstance(v, StateIRVariable):
                            
                            if v.non_ssa_version not in can_var:
                                can_var[v.non_ssa_version] = []
                            can_var[v.non_ssa_version].append(ir)
                        elif v in refDict:
                            ref_var = getRefVar(v, refDict)
                            
                            is_can = True
                            if isinstance(ref_var, tuple):
                                if isinstance(ref_var[0], Contract) and (isinstance(ref_var[1], Constant) or ref_var[1].is_constant or ref_var[1].is_immutable):
                                    is_can = False
                                elif isinstance(ref_var[0],TemporaryVariable):
                                    is_can = False
                                else:
                                    for t in ref_var:
                                        if t == loopVar:
                                            is_can = False
                                            break
                                        
                            if is_can:
                                if ref_var not in can_var:
                                    can_var[ref_var] = []
                                can_var[ref_var].append(ir)

                if assignValue(ir):    
                    if isinstance(ir.lvalue, TupleVariable):
                        tuple_var.append(ir.lvalue)
                    else:      
                        left_var = getRefVar(ir.lvalue, refDict)
                        remove_vars.append(left_var)
    
    for var in remove_vars:
        if var in can_var:
            del can_var[var]
    
    keys = list(can_var.keys())
    for k in keys:
        if isinstance(k, tuple):
            for t in k:
                if t in remove_vars:
                    del can_var[k]
                    break
        else:
            if k in remove_vars:
                del can_var[k]
                break
    
    for key in can_var:
        bugs.append((key, can_var[key]))
    return bugs

def compareVar(var1, var2, refVal):
    if var1 == var2:
        return True
    if hasNonSSAVersion(var1) and hasNonSSAVersion(var2):
        if var1.non_ssa_version == var2.non_ssa_version:
            return True
    if var1 not in refVal:
        return False
    if var2 not in refVal:
        return False
    
    var1_right = refVal[var1][1]
    var2_right = refVal[var2][1]
    
    if hasNonSSAVersion(var1_right):
        var1_right = var1_right.non_ssa_version
    if hasNonSSAVersion(var2_right):
        var2_right = var2_right.non_ssa_version
    if var1_right != var2_right:
        return False
    
    var1_left = refVal[var1][0]
    var2_left = refVal[var2][0]
    var1_arr = []
    var2_arr = []

    while var1_left in refVal:
        var1_arr.append(refVal[var1_left][1])
        var1_left = refVal[var1_left][0]
    var1_arr.append(var1_left)

    while var2_left in refVal:
        var2_arr.append(refVal[var2_left][1])
        var2_left = refVal[var2_left][0]
    var2_arr.append(var2_left)

    if len(var1_arr) != len(var2_arr):
        return False
    
    for i in range(len(var2_arr)):
        v1 = var1_arr[i]
        v2 = var2_arr[i]

        if hasNonSSAVersion(v1):
            v1 = v1.non_ssa_version
        if hasNonSSAVersion(v2):
            v2 = v2.non_ssa_version
        
        if v1 != v2:
            return False
    
    return True


class LoopInvariant(AbstractDetector):  
    """
    Documentation
    """

    ARGUMENT = "loop-invariant" 
    HELP = "Help printed by slither"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "Detects loop invariant inside loop"

    WIKI_TITLE = "NONE"
    WIKI_DESCRIPTION = "NONE"
    WIKI_EXPLOIT_SCENARIO = "NONE"
    WIKI_RECOMMENDATION = "NONE"

    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions_and_modifiers:
                if not f.is_implemented:
                    continue
                bugs = detecLoopInvariant(f)
                if len(bugs) > 0:
                    info = [ str(f.name) + '() @ ' + str(f.source_mapping) + '\n' ]

                    i = 0
                    while i < len(bugs):
                        info.append("[BUG:] ")
                        info.append(str(i))
                        info.append(": ") 
                        if isinstance(bugs[i][0], tuple):
                            name = ''
                            for t in bugs[i][0]:
                                if isinstance(t, str):
                                    name += t + ' '
                                else:
                                    name += t.name + ' '
                            info.append(name)
                        else:
                            info.append(bugs[i][0])
                        info.append("\t")
                        lines = ''
                        for ir in bugs[i][1]:
                            lines += str(ir.node.source_mapping) + "\t"
                        info.append(lines)
                        info.append("\n")
                        i += 1
                    info.append("\n")
                    
                    res = self.generate_result(info)
                    results.append(res)

        return results