#!/usr/bin/env python3
import subprocess 
import os
import time


checkers = [
    "return-bomb" ,"costly-loop", "cache-array-length", "constable-states", "external-function" , "immutable-states", "var-read-using-this"
    ]


def get_slither_base_cmd(checkers):
    return ["slither", "--detect", ",".join(checkers)]

def set_solc_version(ver):
    subprocess.run(["solc-select", "use", ver, "--always-install"]).check_returncode()


def run_slither_process(extend_cmd, path, dir, version):
    set_solc_version(version)
    base_cmd =  get_slither_base_cmd(checkers)
    if extend_cmd:
        base_cmd.extend(extend_cmd)
    start_time = time.time()
    for r, d, f in os.walk(path+'/'+dir, topdown=True):
        if "mock" in r or "test" in r:
            continue
        for folder in d:
            if "mock" in folder or "test" in folder:
                 continue
            cmd = base_cmd.copy()
            cmd.extend([r+"/"+folder])
            p = subprocess.run(cmd, capture_output=True, encoding="utf8")
    end_time = time.time()
    duration = end_time - start_time
    print(path, "time:", duration)


def run():
    run_slither_process(None,"./benchmark/openzeppelin-contracts-master","contracts","0.8.9")
    run_slither_process(["--solc-args", "optimize"],"./benchmark/seaport-main","contracts","0.8.13")
    run_slither_process([
       "--solc-remaps", 
        "openzeppelin-contracts=lib/openzeppelin-contracts/contracts/ utility-contracts=lib/utility-contracts/src ERC721A=lib/ERC721A/contracts solmate=lib/solmate/src operator-filter-registry=lib/operator-filter-registry/src"],
        "./benchmark/seadrop-main","src","0.8.17")
    run_slither_process(None,"./benchmark/solidity-lib","contracts","0.7.0")
    run_slither_process(None,"./benchmark/solmate-main","src","0.8.0")
    run_slither_process(None,"./benchmark/v2-core-master","contracts","0.5.16")
    run_slither_process(["--solc-remaps",
        "@openzeppelin=node_modules/@openzeppelin @uniswap=node_modules/@uniswap base64-sol=node_modules/base64-sol"],
        "./benchmark/v2-periphery-master","contracts","0.6.6")
    run_slither_process(None,"./benchmark/v3-core-master","contracts","0.7.6")
    run_slither_process(["--solc-remaps", 
        "@openzeppelin=node_modules/@openzeppelin @uniswap=node_modules/@uniswap base64-sol=node_modules/base64-sol",
        "--solc-args",
        "optimize"],
        "./benchmark/v3-periphery-master","contracts","0.7.6")


if __name__ == "__main__":
    run()