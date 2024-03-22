import os, time, json
import analyze,pattern
from web3 import Web3  
import multiprocessing
import stopit

node_url = "https://nd-422-757-666.p2pify.com/0a9d79d93fb2f4a4b1e04695da2b77a7" # replace with your web3 node url
w3 = Web3(Web3.HTTPProvider(node_url))

def handleTransaction(blockNum):
    print("block:", blockNum)
    startTime = time.time()

    block = w3.eth.get_block(blockNum, False)
    block_sta_path = "./result/block/" + str(blockNum) + ".txt"
    
    block_content = ''
    block_content+="timestamp: " + str(block.timestamp) + "\t# of tx: " + str(len(block.transactions)) + "\n\n"
    storage_gas,memory_gas,calldata_gas,stack_gas,total_gas = 0,0,0,0,0
    opcode_num = 0
    nosideeffect_gas, reSloadGas, storeSloadGas, nonzeroGas, boolGas, reStoreGas, meminvGas, andinifGas, allocInloopGas = 0,0,0,0,0,0,0,0,0
    opcode_map = {}
    constackop_map = {}
    nse_map = {}
    failed_num = 0

    for tx in block.transactions:
        block_content+=tx.hex() + ":\n"
        tx_traces = None
        hasStorage = True
        with stopit.ThreadingTimeout(60) as context_manager:
            tx_traces = w3.provider.make_request('debug_traceTransaction', [tx.hex(), {"disableStorage": False, "disableStack": False, "disableMemory": True, "disableReturnData": True}])

        if context_manager.state == context_manager.TIMED_OUT:
            tx_traces = w3.provider.make_request('debug_traceTransaction', [tx.hex(), {"disableStorage": True, "disableStack": False, "disableMemory": True, "disableReturnData": True}])
            hasStorage = False

        if tx_traces and "result" in tx_traces and tx_traces["result"]["structLogs"]:
            if tx_traces["result"]["failed"]:
                failed_num+=1
                block_content+="failed\n\n"
                continue

            logs = tx_traces["result"]["structLogs"]
            storage_gas_tmp,memory_gas_tmp,calldata_gas_tmp,stack_gas_tmp,total_gas_tmp,opcode_num_tmp = analyze.analyzeDistribution(logs, opcode_map, constackop_map)
            storage_gas+=storage_gas_tmp
            memory_gas+=memory_gas_tmp
            calldata_gas+=calldata_gas_tmp
            stack_gas+=stack_gas_tmp
            total_gas+=total_gas_tmp
            opcode_num+=opcode_num_tmp

            block_content+=str(opcode_num_tmp)+"\n"
            block_content+=str(storage_gas_tmp)+"\t"+str(memory_gas_tmp)+"\t"+str(calldata_gas_tmp)+"\t"+str(stack_gas_tmp)+"\t"+str(total_gas_tmp)+"\n"
            
            nse_seq_tmp,nosideeffect_gas_tmp = pattern.detectNoSideEffect(logs, nse_map)
            nosideeffect_gas+=nosideeffect_gas_tmp
            block_content+="no side effect: "+str(nosideeffect_gas_tmp)+"\n"
            
            redundantSload_tmp, reSloadGas_tmp, sstoreSload_tmp, storeSloadGas_tmp, expansionOp_tmp, nonzeroGas_tmp, zeroToOne_tmp, boolGas_tmp, sstore_same_tmp, reStoreGas_tmp, mem_invar_seq_tmp, meminvGas_tmp, andinif_seq_tmp, andinifGas_tmp, allocInloopGas_tmp = pattern.detectOthers(logs)
            
            if not hasStorage:
                redundantSload_tmp, reSloadGas_tmp, sstoreSload_tmp, storeSloadGas_tmp, expansionOp_tmp, nonzeroGas_tmp, zeroToOne_tmp, boolGas_tmp, sstore_same_tmp, reStoreGas_tmp = pattern.detectStorageWithStack(logs)
            
            reSloadGas+=reSloadGas_tmp
            block_content+="redundant sloads: "+str(reSloadGas_tmp)+"\n"
            
            storeSloadGas+=storeSloadGas_tmp
            block_content+="sstore sloads: "+str(storeSloadGas_tmp)+"\n"

            nonzeroGas+=nonzeroGas_tmp
            block_content+="zero->non-zero: "+str(nonzeroGas_tmp)+"\n"
            
            boolGas+=boolGas_tmp
            block_content+="0->1: "+str(boolGas_tmp)+"\n"
            
            reStoreGas+=reStoreGas_tmp
            block_content+="redundant sstore: "+str(reStoreGas_tmp)+"\n"
            
            meminvGas+=meminvGas_tmp
            block_content+="memory redundant read: "+str(meminvGas_tmp)+"\n"
            
            andinifGas+=andinifGas_tmp
            block_content+="&& in if: "+str(andinifGas_tmp)+"\n"
            
            allocInloopGas+=allocInloopGas_tmp
            block_content+="alloc in loop: "+str(allocInloopGas_tmp)+"\n"
            block_content+="\n"
    
    opcode_file = open("./result/opcode/"+str(blockNum)+".json", "w")
    json.dump(opcode_map, opcode_file)
    opcode_file.close()

    stackop_file = open("./result/constackop/"+str(blockNum)+".json", "w")
    json.dump(constackop_map, stackop_file)
    stackop_file.close()

    nse_file = open("./result/nosideeffect/"+str(blockNum)+".txt", "w")
    nse_file.write(str(nse_map))
    nse_file.close()

    block_content+="\ntotal:" + "\n"
    block_content+=str(len(block.transactions)-failed_num) + "\n"
    block_content+=str(opcode_num)+"\n"
    block_content+=str(storage_gas)+"\t"+str(memory_gas)+"\t"+str(calldata_gas)+"\t"+str(stack_gas)+"\t"+str(total_gas)+"\n"
    block_content+="no side effect: "+str(nosideeffect_gas)+"\n"
    block_content+="redundant sloads: "+str(reSloadGas)+"\n"
    block_content+="sstore sloads: "+str(storeSloadGas)+"\n"
    block_content+="zero->non-zero: "+str(nonzeroGas)+"\n"
    block_content+="0->1: "+str(boolGas)+"\n"
    block_content+="redundant sstore: "+str(reStoreGas)+"\n"
    block_content+="memory redundant read: "+str(meminvGas)+"\n"
    block_content+="&& in if: "+str(andinifGas)+"\n"
    block_content+="alloc in loop: "+str(allocInloopGas)+"\n"
    
    cur_blo_file = open(block_sta_path, "w")
    cur_blo_file.write(block_content)
    cur_blo_file.close()
    print("time cost:", time.time()-startTime)


if __name__ == "__main__":
    startTime = time.time()
    pool = multiprocessing.Pool()

    if not os.path.exists("./result/block"):
        os.makedirs("./result/block")
    if not os.path.exists("./result/nosideeffect"):
        os.makedirs("./result/nosideeffect")
    if not os.path.exists("./result/opcode"):
        os.makedirs("./result/opcode")
    if not os.path.exists("./result/constackop"):
        os.makedirs("./result/constackop")

    for i in range(19129889, 19201122):
        handled = True
        
        if not os.path.isfile("./result/block/"+str(i)+".txt"):
            handled = False
        if not os.path.isfile("./result/nosideeffect/"+str(i)+".txt"):
            handled = False
        if not os.path.isfile("./result/opcode/"+str(i)+".json"):
            handled = False
        if not os.path.isfile("./result/constackop/"+str(i)+".json"):
            handled = False
        if not handled:
            pool.apply_async(handleTransaction, args=(i,))

    pool.close()
    pool.join()
    print("total time cost:", time.time()-startTime)
