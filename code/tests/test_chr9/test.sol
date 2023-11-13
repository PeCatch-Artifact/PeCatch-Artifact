// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.15;

interface Demo{

    function test5() external;
    
}

contract Test is Demo {

    struct Observation {
        // the block timestamp of the observation
        uint32 blockTimestamp;
        // the tick accumulator, i.e. tick * time elapsed since the pool was first initialized
        int56 tickCumulative;
        // the seconds per liquidity, i.e. seconds elapsed / max(1, liquidity) since the pool was first initialized
        uint160 secondsPerLiquidityCumulativeX128;
        // whether or not the observation is initialized
        bool initialized;
        uint256[] amounts;
    }

    event Sync(uint256[] amount);

    function test1(uint256[] memory amounts, Observation memory b) public {
        for (uint256 i = 0; i < amounts.length; ) {
            uint256 amount = amounts[i];

            // An array can't have a total length
            // larger than the max uint256 value.
            unchecked {
                ++i;
            }
        }
        emit Sync(amounts);
        test2(b.amounts);
        uint112 c = 1;
        b.initialized = true;
        b.amounts[0] = uint256(c);
        // (c, b.amounts[0]) = (4, 2);
    }

    function test2(uint256[] memory amounts) public {
        for (uint256 i = 0; i < amounts.length; ) {
            // amounts[i] += 1;
            uint256 amount = amounts[i];

            // An array can't have a total length
            // larger than the max uint256 value.
            unchecked {
                ++i;
            }
        }
    }

    function test3(uint256[] calldata amounts) public {
        for (uint256 i = 0; i < amounts.length; ) {
            uint256 amount = amounts[i];

            // An array can't have a total length
            // larger than the max uint256 value.
            unchecked {
                ++i;
            }
        }
    }

    function test5() public override{

    }
}

