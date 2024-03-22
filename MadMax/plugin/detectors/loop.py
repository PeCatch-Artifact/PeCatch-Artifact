from slither.core.cfg.node import NodeType
from slither.slithir.operations.condition import Condition
from slither.slithir.operations.binary import Binary, BinaryType
from slither.slithir.operations.assignment import Assignment
from slither.slithir.operations.lvalue import OperationWithLValue
from slither.slithir.variables.constant import Constant

def findBackedges(enter):
    backedges = []
    dfs(enter, {}, backedges)
    return backedges

def dfs(n, status, backedges):
    if not n:
        return
    status[n] = 0 # in progress
    for s in n.sons:
        if s and s not in status: #unmarked
            dfs(s, status, backedges)
        if s in status and status[s] == 0:
            backedges.append((n,s))
    status[n] = 1 # done

def getLoopBody(backedge):
    header = backedge[1]
    n = backedge[0]
    body = [header]
    stack = [n]
    while stack:
        d = stack.pop(0)
        if d not in body:
            body.append(d)
            for p in d.fathers:
                stack.append(p)
    body = body[1:]
    body.reverse()
    body = [header] + body
    return body

def hasMultipleBackedge(body):
    backedges = []
    header = body[0]
    for f in header.fathers:
        if f not in body:
            continue
        if header in f.dominators:
            backedges.append(f)
    return len(backedges) > 1

def getLoopExitCondition(loop): #TODO: refine, find induction variable
    ifNode = loop[0]

    if ifNode.type != NodeType.IFLOOP:
        ifNode = loop[-1]
    conditionVar = None
    compareIr = None
    boundVar = []
    for ir in reversed(ifNode.irs_ssa):
        # print(ir)
        if isinstance(ir, Condition):
            conditionVar = ir.value
        if conditionVar and isinstance(ir, Binary):
            if ir.lvalue == conditionVar:
                compareIr = ir
                boundVar.extend(ir.read)
        if isinstance(ir, OperationWithLValue):
            if ir.lvalue in boundVar:
                boundVar.remove(ir.lvalue)
                boundVar.extend(ir.read)
    
    # for v in boundVar:
    #     print(v)
    # print("************")
    loopVar = None
    posLoopVars = getLoopInductionVar(loop)
    for pv in posLoopVars:
        # print(pv)
        if pv in boundVar:
            loopVar = pv.non_ssa_version
            break

    return compareIr, loopVar, boundVar

def getLoopInductionVar(loop):
    # print("^^^^^^^^^^^^^^^^")
    candidate = {}
    res = []
    for node in loop:
        for ir in node.irs_ssa:
            if isinstance(ir, Binary) and ir.type == BinaryType.ADDITION:
                # print(ir)
                if isinstance(ir.variable_left, Constant):
                    if ir.variable_right.non_ssa_version == ir.lvalue.non_ssa_version:
                        res.append(ir.lvalue)
                    candidate[ir.lvalue] = ir.variable_right
                elif isinstance(ir.variable_right, Constant):
                    if ir.variable_left.non_ssa_version == ir.lvalue.non_ssa_version:
                        res.append(ir.lvalue)
                    candidate[ir.lvalue] = ir.variable_left
            if isinstance(ir, Assignment):
                # print(ir)
                if ir.rvalue in candidate and candidate[ir.rvalue].non_ssa_version == ir.lvalue.non_ssa_version:
                    res.append(ir.lvalue)
    return res