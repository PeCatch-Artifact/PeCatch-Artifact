from . cfg import *


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