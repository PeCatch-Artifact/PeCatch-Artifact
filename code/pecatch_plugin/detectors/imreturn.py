from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations.return_operation import Return
from slither.slithir.operations import OperationWithLValue
from slither.core.declarations import Function
from slither.core.cfg.node import NodeType
from slither.core.solidity_types.user_defined_type import UserDefinedType
from slither.core.declarations.structure import Structure
from slither.core.solidity_types.elementary_type import ElementaryType


def computeDef(f: "Function"):
    resDict = {}
    for node in f.nodes:
        for ir in node.irs_ssa:
            if isinstance(ir, OperationWithLValue) and ir.lvalue:
                resDict[ir.lvalue] = ir

    return resDict

def returnNewVariables(f, varArr):
    bugs = []
    for node in f.nodes:
        for ir in node.irs:
            if isinstance(ir, Return):
                # filter question mark
                if hasQuestionMark(ir):
                    continue
                for v in ir.values:
                    if v in varArr:
                        bugs.append(v)
    return bugs

def hasQuestionMark(ir):
    filename = ir.node.source_mapping.filename.absolute
    f = open(filename, encoding="utf8")
    content = f.readlines()
    
    for l in ir.node.source_mapping.lines:
        if "?" in content[l-1]:
            return True
    return False 

def definedInTuple(node, var):
    filename = node.source_mapping.filename.absolute
    f = open(filename, encoding="utf8")
    content = f.readlines()
    
    for l in node.source_mapping.lines:
        if var.name in content[l-1] and "(" in content[l-1] and ")" in content[l-1]:
            indexL = content[l-1].index("(")
            indexR = content[l-1].index(")")
            indexV = content[l-1].index(var.name)
            if indexV > indexL and indexV < indexR:
                return True
    return False 

def getNewVariables(f):
    newVar = []
    for node in f.nodes:
        if node.type == NodeType.VARIABLE:
            if isinstance(node.variable_declaration.type, ElementaryType):
                if not definedInTuple(node, node.variable_declaration):
                    newVar.append(node.variable_declaration)
            elif isinstance(node.variable_declaration.type, UserDefinedType) and isinstance(node.variable_declaration.type.type, Structure):
                newVar.append(node.variable_declaration)

    return newVar


class ImplicitReturn(AbstractDetector):  
    """
    Documentation
    """

    ARGUMENT = "implicit-return" 
    HELP = "Help printed by slither"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "Detecting cases where a return is not declared explicitly"

    WIKI_TITLE = "NONE"
    WIKI_DESCRIPTION = "NONE"
    WIKI_EXPLOIT_SCENARIO = "NONE"
    WIKI_RECOMMENDATION = "NONE"


    def _detect(self):
        results = []

        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                varArr = getNewVariables(f)
                bugs = returnNewVariables(f, varArr)
                if len(bugs) > 0:
                    info = [ str(f.name) + '() @ ' + str(f.source_mapping) + '\n' ]

                    i = 0
                    while i < len(bugs):
                        info.append("[BUG:] ")
                        info.append(str(i))
                        info.append(": ") 
                        info.append(bugs[i].name + " (" + str(bugs[i].source_mapping) + ")")
                        info.append("\n")
                        i += 1
                    info.append("\n")

                    res = self.generate_result(info)
                    results.append(res)
                            
        return results