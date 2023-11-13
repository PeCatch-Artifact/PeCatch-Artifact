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
            virtualSupply += virtualSupplies[i];
        }
    }
}