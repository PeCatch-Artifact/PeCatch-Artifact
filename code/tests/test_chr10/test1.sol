// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;

contract Test {

    struct Param {
        uint256 sigfigs;
    }

    // function test(Param memory param) public {
    //      while (param.sigfigs > 0) {
    //         param.sigfigs /= 10;
    //     }
    // }

    function test2(uint256[] memory ids, uint256[] calldata amounts, uint256 len) public {
            // uint256 a = 1;
            // uint256 id = 1;
            // uint256 amount = 1;
            // uint256 id2 = 1;
            // uint256 amount2 = 1;
            // uint256 id3 = 1;
            // uint256 amount3 = 1;
            // uint256 id4 = 1;
            // uint256 amount4 = 1;
            // uint256 id5 = 1;
            // uint256 amount5 = 1;
            // uint256 id6 = 1;
            // uint256 amount6 = 1;
            // uint256 id7;
            // uint256 id8 = 1;
            // uint256 amount8 = 1;

        for (uint256 i = 0; i < ids.length; i++) {
            uint256 a = 1;
            {
                uint256 id = ids[i];
                uint256 amount = amounts[i];
            }
            assembly {
                let xx:= 1
            }
            (uint256 id2,uint256 amount2)  = (ids[i],amounts[i]);
            (id2,amount2)  = (ids[i],amounts[i]);
            uint256 id3 = ids[i];
            uint256 amount3 = amounts[i];
            uint256 id4 = ids[i];
            uint256 amount4 = amounts[i];
            // uint256 id5 = ids[i];
            // uint256 amount5 = amounts[i];
            // uint256 id6 = ids[i];
            // uint256 amount6 = amounts[i];
            // uint256 id7 = 1;
            // uint256 amount7 = 1;
            // uint256 id8 = 1;
            // uint256 amount8 = 1;
            // // a = 1;
            // // {
            // id = ids[i];
            // amount = amounts[i];
            // // }
            // (id2,amount2)  = (ids[i],amounts[i]);
            // (id2,amount2)  = (ids[i],amounts[i]);
            // id3 = ids[i];
            // amount3 = amounts[i];
            // id4 = ids[i];
            // amount4 = amounts[i];
            // id5 = ids[i];
            // amount5 = amounts[i];
            // id6 = ids[i];
            // amount6 = amounts[i];
            // uint256 id7 = 1;
            // uint256 amount7 = 1;
            // uint256 id8 = 1;
            // uint256 amount8 = 1;
        }
    }

    // function _lowerBinaryLookup(
    //     uint32 key,
    //     uint256 low,
    //     uint256 high
    // ) private view returns (uint256) {
    //     while (low < high) {
    //         uint256 mid = (low + high) / 2;
    //         if (mid < key) {
    //             low = mid + 1;
    //         } else {
    //             high = mid;
    //         }
    //     }
    //     return high;
    // }
}