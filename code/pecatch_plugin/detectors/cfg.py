from slither.core.declarations import Function

def assignIDs(f: "Function"):
    mapIIIDs = {}
    mapBBIDs = {}

    iiID = 0
    bbID = 0

    for node in f.nodes:
        mapBBIDs[node] = bbID
        bbID += 1
        for ir in node.irs_ssa:
            mapIIIDs[ir] = iiID
            iiID += 1

    return mapIIIDs, mapBBIDs

def printCFG(f: "Function", mapBBIDs):
    
    for node in f.nodes:
        print(mapBBIDs[node], '\t', node._node_type, '\t pre:', end = ' ')
        for father in node.fathers:
            print(mapBBIDs[father], end = ' ')
        print()
        for ir in node.irs_ssa:
            print(ir)
            #if not isinstance(ir, Phi):
            #    if isinstance(ir, Assignment):
            #        print(type(ir.lvalue), ir.lvalue)
                
                #for v in ir.read:
                #    if isinstance(v, StateIRVariable):
                #        print("read state")

        print('\t succ:', end = ' ')
        for son in node.sons:
            print(mapBBIDs[son], ' ', end = ' ')
        print()
        print()


def getPredInsts(ii):
    preds = set()
    node = ii.node

    if ii != node.irs_ssa[0]:
        index = 1
        while ii != node.irs_ssa[index]:
            index += 1
        
        preds.add(node.irs_ssa[index-1])

    else:
        worklist = []
        processed = set()
        for father in node.fathers:
            worklist.append(father)
            processed.add(father)

        while len(worklist) > 0: 
            fa = worklist.pop(0)

            if len(fa.irs_ssa) > 0:
                preds.add(fa.irs_ssa[-1])
            else:
                for fafa in fa.fathers:
                    if fafa not in processed:
                        processed.add(fafa)
                        worklist.append(fafa)
    
    return list(preds)
     
def getSuccInsts(ii):
    succs = set()
    node = ii.node

    if ii != node.irs_ssa[-1]:
        index = 0
        while ii != node.irs_ssa[index]:
            index += 1
        
        succs.add(node.irs_ssa[index+1])

    else:
        worklist = []
        processed = set()
        for son in node.sons:
            worklist.append(son)
            processed.add(son)

        while len(worklist) > 0: 
            so = worklist.pop(0)

            if len(so.irs_ssa) > 0:
                succs.add(so.irs_ssa[0])
            else:
                for soso in so.sons:
                    if soso not in processed:
                        processed.add(soso)
                        worklist.append(soso)
    
    return list(succs)


#treat each instruction as a BB
def generateIICFG(f: "Function"):
    predInsts = {}
    succInsts = {}

    for node in f.nodes:
        for ir in node.irs_ssa:
            predInsts[ir] = getPredInsts(ir)
            succInsts[ir] = getSuccInsts(ir)

    return predInsts, succInsts

def printIICFG(f: "Function", predInsts, succInsts, mapIIIDs):
    for node in f.nodes:
        for ir in node.irs_ssa:
            print(mapIIIDs[ir], '\t pre:', end = '')
            for ii in predInsts[ir]:
                print(mapIIIDs[ii], ' ', end = '')
            print()
            print(ir)

            print('\t succ:', end = '')
            for ii in succInsts[ir]:
                print(mapIIIDs[ii], ' ', end = '')
            print()
        print()


def computeDominators(f: "Function"):
    dominators = {}
    worklist = []
    predInsts, succInsts = generateIICFG(f)
    for node in f.nodes:
        for ir in node.irs_ssa:
            dominators[ir] = []
            worklist.append(ir)
    
    while len(worklist) > 0:
        ii = worklist.pop(0)
        if len(predInsts[ii]) == 1:
            beforeir = predInsts[ii][0]
            dominators[ii] = []
            dominators[ii].extend(dominators[beforeir])
            dominators[ii].append(beforeir)
        elif len(predInsts[ii]) > 1:
            afterDom = []
            afterDom.extend(dominators[predInsts[ii][0]])
            afterDom.append(predInsts[ii][0])
            for index in range(1, len(predInsts[ii])):
                fn = []
                fn.extend(dominators[predInsts[ii][index]])
                fn.append(predInsts[ii][index])
                afterDom = [value for value in afterDom if value in fn]
            dominators[ii] = afterDom
    
    return dominators