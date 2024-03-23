## EMPIRICAL STUDY ON ON-CHAIN GAS DATA

- transaction.py –– save gas data for each block

- analyze.py –– compute gas consumption on data store areas

- pattern.py –– compute gas impacts of patterns

- merge.py –– compute the final results

- ```result``` folder –– result data

### Run
```
python transaction.py
python merge.py
```
- result/block/i.txt –– gas usage on each data store area and gas usage of gas-inefficient patterns for block i
- result/nosideeffect/i.txt –– execution times and gas cost of sequences of stack opcodes not producing any side effects for block i
- result/opcode/i.json –– execution times and gas costs of opcodes for block i
- result/constackop/i.json –– execution times and gas costs of lengthy sequences of opcodes consisting solely of stack operations for block i

