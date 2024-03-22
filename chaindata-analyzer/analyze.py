
def analyzeDistribution(opSeq, opcode_map, stackop_map):
    storage_gas,memory_gas,calldata_gas,stack_gas,total_gas = 0,0,0,0,0
    storage_list = ['SLOAD', 'SSTORE']
    memory_list = ['MLOAD', 'MSTORE', 'MSTORE8', 'MSIZE', 'CODECOPY', 'EXTCODECOPY', 'RETURNDATACOPY']
    calldata_list = ['CALLDATASIZE', 'CALLDATALOAD', 'CALLDATACOPY']
    stackop = ()
    opcode_num = len(opSeq)
    tmp_stackop_gas = 0

    for i in range(0, opcode_num):
        item = opSeq[i]
        if item['op'] not in opcode_map:
            opcode_map[item['op']] = [0,0]
        opcode_map[item['op']][0] += 1
        isStackOp = False
        if i < opcode_num - 1:
            if item['op'] in storage_list:
                if item['gas']>opSeq[i+1]['gas']:
                    storage_gas+=item['gas']-opSeq[i+1]['gas']
                else:
                    storage_gas+=item['gasCost']
                    stack_gas+=item['gas']-opSeq[i+1]['gas']-item['gasCost']
            elif item['op'] in memory_list:
                if item['gas']>opSeq[i+1]['gas']:
                    memory_gas+=item['gas']-opSeq[i+1]['gas']
                else:
                    memory_gas+=item['gasCost']
                    stack_gas+=item['gas']-opSeq[i+1]['gas']-item['gasCost']
            elif item['op'] in calldata_list:
                if item['gas']>opSeq[i+1]['gas']:
                    calldata_gas+=item['gas']-opSeq[i+1]['gas']
                else:
                    calldata_gas+=item['gasCost']
                    stack_gas+=item['gas']-opSeq[i+1]['gas']-item['gasCost']
            else:
                isStackOp = True
                stackop+=(item['op'],)
                tmp_stackop_gas+=item['gas']-opSeq[i+1]['gas']
                stack_gas+=item['gas']-opSeq[i+1]['gas']
            
            if item['gas']>opSeq[i+1]['gas']:
                opcode_map[item['op']][1] += min(item['gas']-opSeq[i+1]['gas'], item['gasCost'])
            else:
                opcode_map[item['op']][1] += item['gasCost']
        else:
            if item['op'] in storage_list:
                storage_gas+=item['gasCost']
            elif item['op'] in memory_list:
                memory_gas+=item['gasCost']
            elif item['op'] in calldata_list:
                calldata_gas+=item['gasCost']
            else:
                isStackOp = True
                stackop+=(item['op'],)
                tmp_stackop_gas+=item['gasCost']      
                stack_gas+=item['gasCost']         
            opcode_map[item['op']][1] += item['gasCost']

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
    return storage_gas,memory_gas,calldata_gas,stack_gas,total_gas,opcode_num
