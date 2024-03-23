import os, time, json
import multiprocessing

def computeTotal(blockNum):
    print("block:", blockNum)
    startTime = time.time()
    tx_num_total = 0
    storage_gas,memory_gas,calldata_gas,stack_gas,total_gas = 0,0,0,0,0
    opcode_num = 0
    nosideeffect_gas, reSloadGas, storeSloadGas, nonzeroGas, boolGas, reStoreGas, meminvGas, andinifGas, allocInloopGas = 0,0,0,0,0,0,0,0,0
    opcode_map = {}
    constackop_map = {}
    nse_map = {}

    for i in range(blockNum, blockNum+500):
        if not os.path.isfile("./result/block/"+str(i)+".txt"):
            print(i, "out of range")
            break
        block_f = open("./result/block/"+str(i)+".txt")
        content = block_f.readlines()
        
        tindex = content.index("total:\n")
        tx_num_total+=int(content[tindex+1])
        opcode_num+=int(content[tindex+2])
        dis_arr = content[tindex+3].split("\t")
        storage_gas+=int(dis_arr[0])
        memory_gas+=int(dis_arr[1])
        calldata_gas+=int(dis_arr[2])
        stack_gas+=int(dis_arr[3])
        total_gas+=int(dis_arr[4])
        nosideeffect_gas+=int(content[tindex+4].split(": ")[1])
        reSloadGas+=int(content[tindex+5].split(": ")[1])
        storeSloadGas+=int(content[tindex+6].split(": ")[1])
        nonzeroGas+=int(content[tindex+7].split(": ")[1])
        boolGas+=int(content[tindex+8].split(": ")[1])
        reStoreGas+=int(content[tindex+9].split(": ")[1])
        meminvGas+=int(content[tindex+10].split(": ")[1])
        andinifGas+=int(content[tindex+11].split(": ")[1])
        allocInloopGas+=int(content[tindex+12].split(": ")[1])
        block_f.close()

        nse_f = open("./result/nosideeffect/"+str(i)+".txt")
        dic = ''
        for line in nse_f.readlines():
            dic=line #string
        tmp_map = eval(dic) 
        nse_f.close()
        for key in tmp_map:
            if key not in nse_map:
                nse_map[key] = tmp_map[key]
            else:
                nse_map[key][0]+=tmp_map[key][0]
                nse_map[key][1]+=tmp_map[key][1]
        
        opcode_f = open("./result/opcode/"+str(i)+".json")
        tmp_map = json.load(opcode_f)
        opcode_f.close()
        for key in tmp_map:
            if key not in opcode_map:
                opcode_map[key] = tmp_map[key]
            else:
                opcode_map[key][0]+=tmp_map[key][0]
                opcode_map[key][1]+=tmp_map[key][1]

        stackop_f = open("./result/constackop/"+str(i)+".json")
        tmp_map = json.load(stackop_f)
        stackop_f.close()
        for key in tmp_map:
            if key not in constackop_map:
                constackop_map[key] = tmp_map[key]
            else:
                constackop_map[key][0]+=tmp_map[key][0]
                constackop_map[key][1]+=tmp_map[key][1]

    res = ''
    res+="# of tx: "+str(tx_num_total)+"\n"
    res+=str(opcode_num)+"\n"
    res+=str(storage_gas)+"\t"+str(memory_gas)+"\t"+str(calldata_gas)+"\t"+str(stack_gas)+"\t"+str(total_gas)+"\n"
    
    opcode_f = open("./tmp/opcode/"+str(blockNum)+".json", "w")
    json.dump(dict(sorted(opcode_map.items(), key=lambda item: item[1][0], reverse=True)), opcode_f)
    opcode_f.close()

    stackop_f = open("./tmp/constackop/"+str(blockNum)+".json", "w")
    json.dump(dict(sorted(constackop_map.items(), key=lambda item: int(item[0]), reverse=True)), stackop_f)
    stackop_f.close()

    res+="no side effect: "+str(nosideeffect_gas)+"\n"
    res+="redundant sloads: "+str(reSloadGas)+"\n"
    res+="sstore sloads: "+str(storeSloadGas)+"\n"
    res+="zero->non-zero: "+str(nonzeroGas)+"\n"
    res+="0->1: "+str(boolGas)+"\n"
    res+="redundant sstore: "+str(reStoreGas)+"\n"
    res+="memory redundant read: "+str(meminvGas)+"\n"
    res+="&& in if: "+str(andinifGas)+"\n"
    res+="alloc in loop: "+str(allocInloopGas)+"\n"
    res_f = open("./tmp/block/"+str(blockNum)+".txt","w")
    res_f.write(res)
    res_f.close()
    
    nse_f = open("./tmp/nosideeffect/"+str(blockNum)+".txt", "w")
    nse_f.write(str(nse_map))
    nse_f.close()
    print("time cost:", time.time()-startTime)

def mergeAll():
    tx_num_total = 0
    storage_gas,memory_gas,calldata_gas,stack_gas,total_gas = 0,0,0,0,0
    opcode_num = 0
    nosideeffect_gas, reSloadGas, storeSloadGas, nonzeroGas, boolGas, reStoreGas, meminvGas, andinifGas, allocInloopGas = 0,0,0,0,0,0,0,0,0
    opcode_map = {}
    constackop_map = {}
    nse_map = {}

    for filename in os.listdir("./tmp/block"):
        block_f = open("./tmp/block/"+filename)
        content = block_f.readlines()

        tx_num_total+=int(content[0].split(": ")[1])
        opcode_num+=int(content[1])
        dis_arr = content[2].split("\t")
        storage_gas+=int(dis_arr[0])
        memory_gas+=int(dis_arr[1])
        calldata_gas+=int(dis_arr[2])
        stack_gas+=int(dis_arr[3])
        total_gas+=int(dis_arr[4])
        nosideeffect_gas+=int(content[3].split(": ")[1])
        reSloadGas+=int(content[4].split(": ")[1])
        storeSloadGas+=int(content[5].split(": ")[1])
        nonzeroGas+=int(content[6].split(": ")[1])
        boolGas+=int(content[7].split(": ")[1])
        reStoreGas+=int(content[8].split(": ")[1])
        meminvGas+=int(content[9].split(": ")[1])
        andinifGas+=int(content[10].split(": ")[1])
        allocInloopGas+=int(content[11].split(": ")[1])
        block_f.close()
    
    gasPrice = 3659.74*56.89*pow(10,-9)
    res = ''
    res+="# of tx: "+str(tx_num_total)+"\n"
    print("# of tx:", tx_num_total)
    res+=str(opcode_num)+"\n"
    print("# of opcode:", opcode_num)
    res+=str(storage_gas)+"\t"+str(memory_gas)+"\t"+str(calldata_gas)+"\t"+str(stack_gas)+"\t"+str(total_gas)+"\n"
    print("total gas:", total_gas, total_gas*gasPrice)
    print("stack:", stack_gas, stack_gas/total_gas, stack_gas*gasPrice)
    print("storage:", storage_gas, storage_gas/total_gas, storage_gas*gasPrice)
    print("memory:", memory_gas, memory_gas/total_gas, memory_gas*gasPrice)
    print("calldata:", calldata_gas, calldata_gas/total_gas, calldata_gas*gasPrice)

    print("**********************pattern**********************")
    print("no side effect:", nosideeffect_gas, nosideeffect_gas/total_gas, nosideeffect_gas*gasPrice)
    print("redundant sloads:", reSloadGas, reSloadGas/total_gas, reSloadGas*gasPrice)
    print("sstore sloads:", storeSloadGas, storeSloadGas/total_gas, storeSloadGas*gasPrice)
    print("storage zero->non-zero:", nonzeroGas, nonzeroGas/total_gas, nonzeroGas*gasPrice)
    print("storage 0->1:", boolGas, boolGas/total_gas, boolGas*gasPrice)
    print("redundant sstore:", reStoreGas, reStoreGas/total_gas, reStoreGas*gasPrice)
    print("memory redundant read:", meminvGas, meminvGas/total_gas, meminvGas*gasPrice)
    print("&& in if:", andinifGas, andinifGas/total_gas, andinifGas*gasPrice)
    print("alloc in loop:", allocInloopGas, allocInloopGas/total_gas, allocInloopGas*gasPrice)
    res+="no side effect: "+str(nosideeffect_gas)+"\n"
    res+="redundant sloads: "+str(reSloadGas)+"\n"
    res+="sstore sloads: "+str(storeSloadGas)+"\n"
    res+="zero->non-zero: "+str(nonzeroGas)+"\n"
    res+="0->1: "+str(boolGas)+"\n"
    res+="redundant sstore: "+str(reStoreGas)+"\n"
    res+="memory redundant read: "+str(meminvGas)+"\n"
    res+="&& in if: "+str(andinifGas)+"\n"
    res+="alloc in loop: "+str(allocInloopGas)+"\n"
    
    total_f = open("./result/total.txt","w")
    total_f.write(res)
    total_f.close()

    for filename in os.listdir("./tmp/nosideeffect"):
        nse_f = open("./tmp/nosideeffect/"+filename)
        dic = ''
        for line in nse_f.readlines():
            dic=line #string
        tmp_map = eval(dic) 
        nse_f.close()
        for key in tmp_map:
            if key not in nse_map:
                nse_map[key] = tmp_map[key]
            else:
                nse_map[key][0]+=tmp_map[key][0]
                nse_map[key][1]+=tmp_map[key][1]

    for filename in os.listdir("./tmp/opcode"):
        opcode_f = open("./tmp/opcode/"+filename)
        tmp_map = json.load(opcode_f)
        opcode_f.close()
        for key in tmp_map:
            if key not in opcode_map:
                opcode_map[key] = tmp_map[key]
            else:
                opcode_map[key][0]+=tmp_map[key][0]
                opcode_map[key][1]+=tmp_map[key][1]
    
    for filename in os.listdir("./tmp/constackop"):
        stackop_f = open("./tmp/constackop/"+filename)
        tmp_map = json.load(stackop_f)
        stackop_f.close()
        for key in tmp_map:
            if key not in constackop_map:
                constackop_map[key] = tmp_map[key]
            else:
                constackop_map[key][0]+=tmp_map[key][0]
                constackop_map[key][1]+=tmp_map[key][1]
    
    opcode_f = open("./result/total_opcode.json", "w")
    json.dump(dict(sorted(opcode_map.items(), key=lambda item: item[1][0], reverse=True)), opcode_f)
    opcode_f.close()

    stackop_f = open("./result/total_stackop.json", "w")
    json.dump(dict(sorted(constackop_map.items(), key=lambda item: int(item[0]), reverse=True)), stackop_f)
    stackop_f.close()
    
    sorted_opcode = dict(sorted(opcode_map.items(), key=lambda item: item[1][0], reverse=True)[:10])
    print("\ntop 10 opcode (sort by times):")
    for op in sorted_opcode:
        print(op, '{:.2%}'.format(sorted_opcode[op][0]/opcode_num), "times:", sorted_opcode[op][0], "gas:", sorted_opcode[op][1])
    sorted_opcode = dict(sorted(opcode_map.items(), key=lambda item: item[1][1], reverse=True)[:10])
    print("\ntop 10 opcode (sort by gas):")
    for op in sorted_opcode:
        print(op, '{:.2%}'.format(sorted_opcode[op][1]/total_gas), "gas:", sorted_opcode[op][1], "times:", sorted_opcode[op][0])

    nse_f = open("./result/total_nosideeffect.txt", "w")
    nse_f.write(str(nse_map))
    nse_f.close()

    print("\ntop 20 no side effect sequences:")
    sorted_nse = dict(sorted(nse_map.items(), key=lambda item: item[1], reverse=True)[:20])
    for seq in sorted_nse:
        print(seq, sorted_nse[seq][0], sorted_nse[seq][1], sorted_nse[seq][1]*gasPrice)

def getConStackop(total_gas, opcode_num):
    constackop_map = {}

    for i in range(19129889, 19201122):
        stackop_f = open("./result/constackop/"+str(i)+".json")
        tmp_map = json.load(stackop_f)
        stackop_f.close()
        for key in tmp_map:
            if key not in constackop_map:
                constackop_map[key] = tmp_map[key]
            else:
                constackop_map[key][0]+=tmp_map[key][0]
                constackop_map[key][1]+=tmp_map[key][1]


    stackop_f = open("./result/constackop_part.json", "w")
    json.dump(dict(sorted(constackop_map.items(), key=lambda item: int(item[0]), reverse=True)), stackop_f)
    stackop_f.close()

    num_10,gas_10 = 0,0
    num_10_20,gas_10_20 = 0,0
    num_20_50,gas_20_50 = 0,0
    num_50_100,gas_50_100 = 0,0
    num_100_1000,gas_100_1000 = 0,0
    num_1000,gas_1000 = 0,0
    gasPrice = 3659.74*56.89*pow(10,-9)

    for key in constackop_map:
        if int(key) < 10:
            num_10+=constackop_map[key][0]*int(key)
            gas_10+=constackop_map[key][1]
        elif int(key)>=10 and int(key) < 20:
            num_10_20+=constackop_map[key][0]*int(key)
            gas_10_20+=constackop_map[key][1]
        elif int(key)>=20 and int(key) < 50:
            num_20_50+=constackop_map[key][0]*int(key)
            gas_20_50+=constackop_map[key][1]
        elif int(key)>=50 and int(key) < 100:
            num_50_100+=constackop_map[key][0]*int(key)
            gas_50_100+=constackop_map[key][1]
        elif int(key)>=100 and int(key) < 1000:
            num_100_1000+=constackop_map[key][0]*int(key)
            gas_100_1000+=constackop_map[key][1]
        elif int(key)>1000:
            num_1000+=constackop_map[key][0]*int(key)
            gas_1000+=constackop_map[key][1]
    
    print(num_10,num_10/opcode_num,gas_10,gas_10/total_gas,gas_10*gasPrice)
    print(num_10_20,num_10_20/opcode_num,gas_10_20,gas_10_20/total_gas,gas_10_20*gasPrice)
    print(num_20_50,num_20_50/opcode_num,gas_20_50,gas_20_50/total_gas,gas_20_50*gasPrice)
    print(num_50_100,num_50_100/opcode_num,gas_50_100,gas_50_100/total_gas,gas_50_100*gasPrice)
    print(num_100_1000,num_100_1000/opcode_num,gas_100_1000,gas_100_1000/total_gas,gas_100_1000*gasPrice)
    print(num_1000,num_1000/opcode_num,gas_1000,gas_1000/total_gas,gas_1000*gasPrice)


if __name__ == "__main__":
    if not os.path.exists("./tmp/block"):
        os.makedirs("./tmp/block")
    if not os.path.exists("./tmp/nosideeffect"):
        os.makedirs("./tmp/nosideeffect")
    if not os.path.exists("./tmp/opcode"):
        os.makedirs("./tmp/opcode")
    if not os.path.exists("./tmp/constackop"):
        os.makedirs("./tmp/constackop")
    startTime = time.time()
    pool = multiprocessing.Pool()

    for i in range(19129889,19201122, 500):
        handled = True
        if not os.path.isfile("tmp/block/"+str(i)+".txt"):
            handled = False
        if not os.path.isfile("tmp/nosideeffect/"+str(i)+".txt"):
            handled = False
        if not os.path.isfile("tmp/opcode/"+str(i)+".json"):
            handled = False
        if not os.path.isfile("tmp/constackop/"+str(i)+".json"):
            handled = False
        if not handled:
            pool.apply_async(computeTotal, args=(i,))
    
    pool.close()
    pool.join()
    print("total time cost:", time.time()-startTime)

    mergeAll()
    getConStackop()
    