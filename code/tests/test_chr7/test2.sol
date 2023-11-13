// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.15;

library Vector {

    struct Bytes32Vector {
        int128 begin;
        int128 end;
        mapping(int128 => bytes32) data;
    }

    function pushBack(Bytes32Vector storage vector, bytes32 value) internal {
       vector.data[vector.end++] = value;
    }

    function testPlus() public pure {
        for(uint256 i=0;i<10;i++){
            uint128 b = 1;
        }

        uint128 t1 = 1;
        uint256 t2 = 1;
        uint16 t3 = 2;
        t1++;
        t2+=1;
        t3++;

        uint256 j = 0;
        do{
            j++;
        } while(j<10);

        while(j<100){
            j++;
        }
    }

    function test4(uint256[] memory data) public {
        for (uint256 i = 0; i < data.length; ++i) {
            uint256 b = 2;
        }
    }
}