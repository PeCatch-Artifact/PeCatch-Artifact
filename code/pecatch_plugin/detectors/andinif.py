
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations.condition import Condition
from slither.core.expressions import TupleExpression
from slither.core.expressions.expression import Expression
from slither.core.expressions.identifier import Identifier
from slither.core.expressions.literal import Literal
from slither.core.expressions.member_access import MemberAccess
from slither.core.expressions.index_access import IndexAccess
from slither.core.expressions.unary_operation import UnaryOperation
from slither.core.expressions.type_conversion import TypeConversion
from slither.core.expressions.call_expression import CallExpression
from slither.core.cfg.node import Node, NodeType


def printExpression(e): 
    if not isinstance(e, Expression):
        return 
    
    for f in dir(e):
        print(f)


    print("Context:", e.context)
    print("expression_left:", e.expression_left)
    print("expression_right:", e.expression_right)
    print("expressions:", e.expressions)
    print("is_lvalue:", e.is_lvalue)
    print("references:", e.references)
    print("source_mapping:", e.source_mapping)
    print("type:", e.type)


def containAddOps(v):
    worklist = [v]
    added = [v]


    while len(worklist) > 0:
        e = worklist.pop(0)

        if isinstance(e, Identifier) or isinstance(e, Literal) or isinstance(e, MemberAccess) or isinstance(e, IndexAccess) \
            or isinstance(e, TypeConversion) or isinstance(e, CallExpression):
            pass
        elif isinstance(e, UnaryOperation):
            e0 = e.expression

        elif isinstance(e, TupleExpression):
            for ee in e.expressions:
                if ee not in added:
                    added.append(ee)
                    worklist.append(ee)
        elif isinstance(e, Expression): 
            if str(e.type) == "&&" :
                return True
            
            e1 = e.expression_left
            e2 = e.expression_right

            if e1 not in added:
                added.append(e1)
                worklist.append(e1)

            if e2 not in added:
                added.append(e2)
                worklist.append(e2)
        else:
            print(e)

    return False

def find_and_in_cond_ir(node):
    irs = []
    for ir in node.irs_ssa:
        if isinstance(ir, Condition):
            if containAddOps(ir.expression):
                irs.append(ir)
    return irs

def filterQuestionMark(irs, source_mapping):
    bugs = []
    filename = source_mapping.filename.absolute
    f = open(filename, encoding="utf8")
    content = f.readlines()

    for ir in irs:
        lines = ir.node.source_mapping.lines
        hasMark = False
        for l in lines:
            if "?" in content[l-1]:
                hasMark = True
        if not hasMark:
            bugs.append(ir)
    return bugs


class AndInIf(AbstractDetector):  
    """
    Documentation
    """

    ARGUMENT = "and-in-if" 
    HELP = "Help printed by slither"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = "Detecting cases where && is used in an if's condition"

    WIKI_TITLE = "NONE"
    WIKI_DESCRIPTION = "NONE"
    WIKI_EXPLOIT_SCENARIO = "NONE"
    WIKI_RECOMMENDATION = "NONE"

    def _detect(self):
        results = []
        for c in self.compilation_unit.contracts_derived:
            for f in c.functions:
                irs = []
                for idx, node in enumerate(f.nodes):
                    if node.type != NodeType.IF:
                        continue
                    # find conditions with &&
                    irs.extend(find_and_in_cond_ir(node))
                bugs = filterQuestionMark(irs, f.source_mapping)
                for b in bugs:
                    info = [ "[BUG:] ",
                        str(b.expression.source_mapping), 
                        " uses && in an if's condition\n"
                    ]
                    res = self.generate_result(info)
                    results.append(res)
        return results

