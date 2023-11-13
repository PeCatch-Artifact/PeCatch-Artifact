// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;

contract UniswapV3Pair {
    // Number of fee options
    uint8 public constant NUM_FEE_OPTIONS = 6;

    // the amount of virtual supply active within the current tick, for each fee vote
    uint112[NUM_FEE_OPTIONS] public virtualSupplies;


    // sum the virtual supply across all fee votes to get the total
    function getVirtualSupply() public view returns (uint112 virtualSupply) {
        for (uint8 i = 0; i < NUM_FEE_OPTIONS; i++) {
            uint j = 10;
            while (j > 1) {
                if(j<8){
                    
                }
                j/=2;
                uint b=1;
                b*=2;
            }

            uint k = NUM_FEE_OPTIONS;
            do {
                uint b=1;
                k++;
                b*=2;
            }
            while(k<5 && i < 3);

            for(uint256 c; c < 3; c++) {
                uint dd;
                dd+=1;
            }
           virtualSupply += virtualSupplies[i];
        }
        virtualSupply = virtualSupplies[0] + virtualSupplies[1] + virtualSupplies[2] + virtualSupplies[3] + virtualSupplies[4] + virtualSupplies[5];
    }

}