
def analyzeDistribution(opSeq, opcode_map, stackop_map):
    storage_gas,memory_gas,calldata_gas,stack_gas,total_gas = 0,0,0,0,0
    storage_list = ['SLOAD', 'SSTORE']
    memory_list = ['MLOAD', 'MSTORE', 'MSTORE8', 'MSIZE', 'CODECOPY', 'EXTCODECOPY', 'RETURNDATACOPY']
    calldata_list = ['CALLDATASIZE', 'CALLDATALOAD', 'CALLDATACOPY']
    call_list = ['CALL', 'CALLCODE', 'DELEGATECALL', 'STATICCALL']
    stackop = ()
    opcode_num = len(opSeq)
    tmp_stackop_gas = 0
    call_op = []
    gas_map = {}

    for i in range(0, opcode_num):
        item = opSeq[i]
        
        if i<opcode_num - 1:
            gas_map[i] = item['gas']-opSeq[i+1]['gas']
        else:
            gas_map[i] = item['gasCost']

        if item['op'] in call_list:
            call_op.append((i,item))
        elif call_op and opSeq[i]['stack'] and \
            ((call_op[-1][1]['op'].startswith("CALL") and opSeq[i]['stack'][:-1] == call_op[-1][1]['stack'][:-7]) or \
            (call_op[-1][1]['op'].endswith("CALL") and opSeq[i]['stack'][:-1] == call_op[-1][1]['stack'][:-6])):
            last_index = call_op[-1][0]
            call_gas = opSeq[last_index]['gas']-opSeq[last_index+1]['gas']
            if i > last_index+1:
                call_gas+=opSeq[i-1]['gas']-opSeq[i]['gas']-opSeq[i-1]['gasCost']
                gas_map[i-1] = opSeq[i-1]['gasCost']
            gas_map[last_index] = call_gas
            call_op.pop()


    for i in range(0, opcode_num):
        item = opSeq[i]
        if item['op'] not in opcode_map:
            opcode_map[item['op']] = [0,0]
        opcode_map[item['op']][0] += 1
        opcode_map[item['op']][1] += gas_map[i]

        isStackOp = False
        if item['op'] in storage_list:
            storage_gas+=gas_map[i]
        elif item['op'] in memory_list:
            memory_gas+=gas_map[i]
        elif item['op'] in calldata_list:
            calldata_gas+=gas_map[i]
        else:
            stack_gas+=gas_map[i]
            isStackOp = True
            stackop+=(item['op'],)
            tmp_stackop_gas+=gas_map[i] 
        
        if not isStackOp:
            cur_len = len(stackop)
            if cur_len not in stackop_map:
                stackop_map[cur_len] = [0,0]
            stackop_map[cur_len][0] += 1
            stackop_map[cur_len][1] += tmp_stackop_gas
            stackop = ()
            tmp_stackop_gas = 0

    if opSeq:
        total_gas = opSeq[0]['gas'] - opSeq[-1]['gas'] + opSeq[-1]['gasCost']
    return storage_gas,memory_gas,calldata_gas,stack_gas,total_gas,opcode_num,gas_map
