# The code and results for PLDI 2024 Artifact Evaluation

Paper: How to Save My Gas Fees: Understanding and Detecting Real-world Gas Issues in Solidity Programs

This document is to help users reproduce the results we reported in our submission. 
It contains the following descriptions:

## Artifact Overview
- ```benchmark``` folder:
    the 10 repostories of the specific version on which we conduct our experiments
- ```code``` folder:
    source code of PeCatch
- ```results``` folder:
    - ```result.xlsx```:
        the results of PeCatch, Slither, GasSaver and python-solidity-optimizer
    - ```gas impact-bugs``` folder:
        patches of the 8 bugs used to calculate gas impact.

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





