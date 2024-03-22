# The code and results for ICSE 2025 Artifact Evaluation

Paper: How My Gas Fees Are Wasted: Understanding
Real-world Gas Issues in Solidity Programs

This document is to help users reproduce the results we reported in our submission. 
It contains the following descriptions:

## Artifact Overview
- ```benchmark``` folder:
    the 9 repostories of the specific version on which we conduct our experiments
- ```code``` folder:
    source code of PeCatch
- ```results``` folder:
    - ```result.xlsx```:
        the results of PeCatch, Slither, GasSaver and python-solidity-optimizer
    - ```gas impact-bugs``` folder:
        patches of the 8 bugs used to calculate gas impact.
- ```chaindata-analyzer```:
    source code of empirical study on on-chain gas data
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

### Run checkers
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





