
storage_list = ['SLOAD', 'SSTORE']
memory_list = ['MLOAD', 'MSTORE', 'MSTORE8', 'MSIZE', 'CODECOPY', 'EXTCODECOPY', 'RETURNDATACOPY']
calldata_list = ['CALLDATASIZE', 'CALLDATALOAD', 'CALLDATACOPY']

def detectNoSideEffect(opSeq, seq_map):
    if not opSeq:
        return None, None
    windowSize = 20
    redunSeq = []

    i = 0
    while i<len(opSeq)-windowSize:
        op_i = opSeq[i]
        if op_i['op'] == 'JUMPDEST':
            i+=1
            continue

        tmp = []
        dup_i = i
        same_index = []
        for j in range(i, i+windowSize):
            op_j = opSeq[j]
            op_name = op_j['op']
            if op_name in storage_list or op_name in memory_list or op_name in calldata_list:
                i = j
                break

            tmp.append((op_name, op_j['pc'], op_j['gas'] - opSeq[j + 1]['gas'], op_j['gasCost']))
            if len(tmp) > 1 and opSeq[j + 1]['stack'] == op_i['stack']:
                if len(tmp) == 2:
                    if tmp[0][0].startswith('PUSH') and tmp[1][0].startswith('JUMP'):
                        continue
                if len(tmp) == 3:
                    if tmp[0][0].startswith('PUSH') and tmp[1][0].startswith('JUMP') and tmp[2][0].startswith('JUMP'):
                        continue
                if tmp[-1][0] == 'JUMPI':
                    continue
                same_index.append(j)

        if same_index:
            max_index = max(same_index)
            redunSeq.append(tmp[:max_index-dup_i+1])
            i = max_index
        i+=1
    
    patternGas = 0
    for seq in redunSeq:
        tmp = ()
        tmp_gas = 0
        for tup in seq:
            tmp+=(tup[0],)
            isInCall = False
            if tup[2] < 0:
                for ti in tmp:
                    if ti in ["CALL","STATICCALL","DELEGATECALL"]:
                        isInCall = True
                        break
                if isInCall:
                    patternGas += tup[2]
                    tmp_gas+=tup[2]
                else:
                    patternGas += tup[3]
                    tmp_gas+=tup[3]
            else:
                patternGas += tup[2]
                tmp_gas+=tup[2]
                
        if tmp not in seq_map:
            seq_map[tmp] = [0,0]
        seq_map[tmp][0] += 1
        seq_map[tmp][1] += tmp_gas
    return redunSeq, patternGas

def detectOthers(opSeq):
    redundantSload = []
    sstoreSload = []
    sloadMap = {}
    storeMap = {}

    zeroToOne = []
    valMap = {}
    sstore_same = []
    expansionOp = []

    read_mem_map = {}
    mem_invar_seq = []
    
    andinif_seq = []
    push_pc = []
    push_pc_map = {}
    last_push_pc = None

    tlen = len(opSeq)

    for i in range(tlen):
        item = opSeq[i]
        if item['op'] == "SLOAD" and 'storage' in item:
            slot = fillZero(item['stack'][-1])
            value = fillZero(item['storage'][slot])
            if slot in sloadMap and value == sloadMap[slot][0]:
                redundantSload.append([(sloadMap[slot][1], sloadMap[slot][2]), (item['pc'], item['gasCost'])])
            else:
                if slot in storeMap and value == storeMap[slot][0]:
                    sstoreSload.append([(storeMap[slot][1], storeMap[slot][2]), (item['pc'], item['gasCost'])])
                sloadMap[slot] = (value, item['pc'], item['gasCost'])
            
        elif item['op'] == "SSTORE" and 'storage' in item:
            slot = fillZero(item['stack'][-1])
            newValue = fillZero(item['stack'][-2])
            storeMap[slot] = (newValue, item['pc'], item['gasCost'])
            if slot in sloadMap:
                del sloadMap[slot]
            if slot in valMap:  
                if newValue == "0"*63+"1" and valMap[slot] == "0"*64:
                    zeroToOne.append((item['pc'], item['gasCost']))
                if newValue != "0"*64 and valMap[slot] == "0"*64:
                    expansionOp.append((item['pc'], item['gasCost']))
                if newValue == valMap[slot]:
                    sstore_same.append((item['pc'], item['gasCost']))
        
        elif item['op'] == "MLOAD" and i < tlen-1:
            offset = item['stack'][-1]
            value = opSeq[i+1]["stack"][-1]
            if offset in read_mem_map and value == read_mem_map[offset]:
                mem_invar_seq.append(((item['pc'], item['gasCost'])))
            else:
                read_mem_map[offset] = value
        if "storage" in item:
            valMap = item["storage"]
        
        # && in if
        if item['op'] == "DUP1":
            if i+5 < tlen-1:
                if opSeq[i+1]['op'] == 'ISZERO' and opSeq[i+2]['op'] == 'PUSH2' and opSeq[i+3]['op'] == 'JUMPI' \
                    and (opSeq[i+4]['op'] == 'JUMPDEST' or opSeq[i+4]['op'] == 'POP'):
                    andinif_seq.append([(item['op'], item['pc'], item['gasCost']),
                                    (opSeq[i+1]['op'], opSeq[i+1]['pc'], opSeq[i+1]['gasCost']),
                                    (opSeq[i+2]['op'], opSeq[i+2]['pc'], opSeq[i+2]['gasCost']),
                                    (opSeq[i+3]['op'], opSeq[i+1]['pc'], opSeq[i+3]['gasCost']),
                                    (opSeq[i+4]['op'], opSeq[i+1]['pc'], opSeq[i+4]['gasCost'])])

        # alloc in loop
        if i < tlen-1 and item['op'] == 'PUSH1':
            if 'stack' in opSeq[i+1] and opSeq[i+1]['stack'] and opSeq[i+1]['stack'][-1] == "0x0":
                if push_pc and item['pc'] in push_pc:
                    if item['pc'] not in push_pc_map:
                        push_pc_map[item['pc']] = {"stack":item['stack']}
                    else:
                        push_pc_map[item['pc']]["stack"] = item['stack']
                    last_push_pc = item['pc']
                elif not push_pc or item['pc'] not in push_pc:
                    push_pc.append(item['pc'])
        elif i<len(opSeq)-2 and item['op'] == 'SWAP1' and opSeq[i+1]['op'] == 'POP' and last_push_pc:
            if opSeq[i+2]['stack'][:-1] == push_pc_map[last_push_pc]['stack']:
                if "seq" not in push_pc_map[last_push_pc]:
                    push_pc_map[last_push_pc]["seq"] = (item['pc'], opSeq[i+1]['pc'])
                    push_pc_map[last_push_pc]["times"] = 1
                else:
                    push_pc_map[last_push_pc]["times"] += 1
    
    reSloadGas = 0
    for seq in redundantSload:
        reSloadGas += seq[1][1]
    
    storeSloadGas = 0
    for seq in sstoreSload:
        storeSloadGas += seq[1][1]

    nonzeroGas = 0
    for seq in expansionOp:
        nonzeroGas += seq[1]

    boolGas = 0
    for seq in zeroToOne:
        boolGas += seq[1]
    
    reStoreGas = 0
    for seq in sstore_same:
        reStoreGas += seq[1]
    
    meminvGas = 0
    for seq in mem_invar_seq:
        meminvGas += seq[1]

    andinifGas = 0
    for seq in andinif_seq:
        andinifGas += seq[0][2] + seq[1][2] + seq[2][2] + seq[3][2] + seq[4][2]
    
    allocInloopGas = 0
    for pc in push_pc_map:
        if "times" in push_pc_map[pc]:
            allocInloopGas += 3*push_pc_map[pc]["times"]
    return redundantSload, reSloadGas, sstoreSload, storeSloadGas, expansionOp, nonzeroGas, zeroToOne, boolGas, sstore_same, reStoreGas, mem_invar_seq, meminvGas, andinif_seq, andinifGas, allocInloopGas


def detectStorageWithStack(opSeq):
    redundantSload = []
    sstoreSload = []
    sloadMap = {}
    storeMap = {}
    
    valMap = {}
    sstore_same = []
    expansionOp = []
    zeroToOne = []

    for i in range(len(opSeq)):
        item = opSeq[i]
        if item['op'] == "SSTORE":
            slot = item['stack'][-1]
            newValue = item['stack'][-2]
            storeMap[slot] = (newValue, item['pc'], item['gasCost'])
            if slot in sloadMap:
                del sloadMap[slot]
            
            if slot in valMap:  
                if newValue != "0x0" and valMap[slot] == "0x0":
                    expansionOp.append((item['pc'], item['gasCost'], slot, newValue, valMap[slot]))
                if newValue == "0x1" and valMap[slot] == "0x0":
                    zeroToOne.append((item['pc'], item['gasCost'], slot, newValue, valMap[slot]))
                if newValue == valMap[slot]:
                    sstore_same.append((item['pc'], item['gasCost']))
            valMap[slot] = newValue
        
        elif item['op'] == "SLOAD":
            slot = item['stack'][-1]
            value = opSeq[i+1]['stack'][-1]
            if slot in sloadMap and value == sloadMap[slot][0]:
                redundantSload.append([(sloadMap[slot][1], sloadMap[slot][2]), (item['pc'], item['gasCost'])])
            else:
                if slot in storeMap and value == storeMap[slot][0]:
                    sstoreSload.append([(storeMap[slot][1], storeMap[slot][2]), (item['pc'], item['gasCost'])])
                sloadMap[slot] = (value, item['pc'], item['gasCost'])
            valMap[slot] = value
    
    reSloadGas = 0
    for seq in redundantSload:
        reSloadGas += seq[1][1]
    
    storeSloadGas = 0
    for seq in sstoreSload:
        storeSloadGas += seq[1][1]

    nonzeroGas = 0
    for seq in expansionOp:
        nonzeroGas += seq[1]

    boolGas = 0
    for seq in zeroToOne:
        boolGas += seq[1]
    
    reStoreGas = 0
    for seq in sstore_same:
        reStoreGas += seq[1]
    return redundantSload, reSloadGas, sstoreSload, storeSloadGas, expansionOp, nonzeroGas, zeroToOne, boolGas, sstore_same, reStoreGas

def fillZero(val):
    if val.startswith('0x'):
        if len(val[2:]) < 64:
            return "0" * (64-len(val[2:])) + val[2:]
        return val[2:]
    return val
