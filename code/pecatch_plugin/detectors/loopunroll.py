from typing import List, Optional
from slither.core.cfg.node import Node, NodeType
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations.binary import Binary
from slither.slithir.operations.assignment import Assignment
from slither.slithir.variables.constant import Constant
from slither.slithir.variables.state_variable import StateIRVariable
from slither.core.declarations.solidity_variables import SolidityVariableComposed

from . cfg import *
from .loop import *


def detectSmallLoop(f: "Function"):
    backedges = findBackedges(f.entry_point)
    loops = {}
    for b in backedges:
        body = getLoopBody(b)
        if not hasMultipleBackedge(body):
            loops[b[1]] = body
    
    bugs = []

    for l in loops:
        s = loops[l][0]
        e = loops[l][-1]

        ifNode = None
        ifIr = None
        
        if s.type == NodeType.IFLOOP:
            ifNode = s
        elif e.type == NodeType.IFLOOP:
            ifNode = e

        if ifNode:
            for ir in ifNode._irs_ssa:
                if isinstance(ir, Binary):
                    ifVal = getConValofBinary(ir)
                    if ifVal is not None: 
                        initVal = getInitVal(f, ifNode, ir)
                        if initVal is not None:
                            if abs(ifVal - initVal) <= 6:
                                ifIr = ir
                                break

                    
            if ifIr:
                loopVar = ifIr.variable_left.non_ssa_version
        
                for n in loops[l]:
                    if n.type == NodeType.EXPRESSION:
                        for ir in n._irs_ssa:
                            if isinstance(ir, Binary):
                                if not isinstance(ir.variable_left, Constant) and not isinstance(ir.variable_left, SolidityVariableComposed) and ir.variable_left.non_ssa_version == loopVar:
                                    if getConValofBinary(ir) == 1:
                                        bugs.append((ifIr, ir))
                                        break

    return bugs

def getInitVal(f, ifNode, ifIr):
    for i in range(f.nodes.index(ifNode), -1, -1):
        node = f.nodes[i]
        irList = node.irs_ssa
        if len(irList) < 1 and node.type == NodeType.VARIABLE:
            if node.variable_declaration == ifIr.variable_left.non_ssa_version:
                return 0
        if f.nodes[i] == ifNode:
            upperBound = irList.index(ifIr)-1
        else:
            upperBound = len(irList)-1
        for j in range(upperBound, -1, -1):
            ir = irList[j]
            if isinstance(ir, Assignment) and ir.lvalue.non_ssa_version == ifIr.variable_left.non_ssa_version:
                    if isinstance(ir.rvalue, Constant):
                        return ir.rvalue.value                     
                    elif isinstance(ir.rvalue, StateIRVariable) and ir.rvalue.is_constant:
                        return int(str(ir.rvalue.expression))
    return None

def getConValofBinary(ir):
    if isinstance(ir.variable_right, Constant):
        return ir.variable_right.value                        
    elif isinstance(ir.variable_right, StateIRVariable) and ir.variable_right.is_constant:
        return int(str(ir.variable_right.expression))
    return None


class LoopUnroll(AbstractDetector):  
    """
    Documentation
    """

    ARGUMENT = "loop-unroll" 
    HELP = "Help printed by slither"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "Detects loops with a small constant number of iteration"

    WIKI_TITLE = "NONE"
    WIKI_DESCRIPTION = "NONE"
    WIKI_EXPLOIT_SCENARIO = "NONE"
    WIKI_RECOMMENDATION = "NONE"

    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions_and_modifiers:
                bugs = detectSmallLoop(f)
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
                        info.append("\n")
                        i += 1
                    info.append("\n")
                    
                    res = self.generate_result(info)
                    results.append(res)

        return results
