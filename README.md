# The Code and Results for ASPLOS 2025 Artifact Evaluation

Paper: How to Save My Gas Fees: Understanding and Detecting Real-World Gas Issues in Solidity Programs

This document is to help users reproduce the results we reported in our submission. 
It contains the following descriptions:

## Artifact Overview
- ```benchmark``` folder:
    the 9 repostories of the specific version on which we conduct our experiments
- ```code``` folder:
    source code of PeCatch
- ```results``` folder:
    - ```result.xlsx```:
        the results of PeCatch, Slither, GasSaver and python-solidity-optimizer and 14 opcode sequences of compiler issues
- ```chaindata-analyzer```:
    source code of analyzing EVM transaction traces
- ```MadMax```:
    source code of re-implementing MadMax with Slither
- ```scripts```:
    - slither-perf.py: evaluate slither detectors –– "return-bomb" ,"costly-loop", "cache-array-length", "constable-states", "external-function" , "immutable-states", "var-read-using-this" on benchmark programs

## Getting Started

### Install PeCatch
```bash
$ git clone https://github.com/PeCatch-Artifact/PeCatch-Artifact.git
$ cd PeCatch-Artifact/code
$ pip install -r requirements.txt
$ python setup.py develop
```

### Run Checkers
```
slither --detect <checker name> <directory path>/<contract path>
```
checker names: and-in-if, implicit-return, redundant-sload, bool, unchecked, mem-call, alloc-in-loop, loop-invariant

example of run and-in-if:
```
slither --detect and-in-if tests/test_chr1/test.sol
```

example of run multiple checkers:
```
slither --detect and-in-if,bool,unchecked tests/test_chr1/test.sol
```





