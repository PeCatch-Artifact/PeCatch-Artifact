// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;

contract SimpleStorage {
    function test1(uint x, uint y) public pure returns (uint) {
        if ( x != 0 && y != 0) {
            return 100;
        } else {
            return 101;
        }
    }

    function test2(uint x, uint y) public pure returns (uint ret) {
        if ( x != 0 ) {
            if (y != 0) {
                return 100;
            }
        }

        return 101;
    }

    function test3(uint x, uint y) public pure returns (uint) {
        if ( x != 0 && y != 0 && x + y > 10) {
            return 100;
        }
        return 101;
    }

    function test4(uint x, uint y) public pure returns (uint) {
        while ( y != 0 && x + y < 10) {
            x++;
        }
        return 101;
    }

    function test5(uint x, uint y) public pure returns (uint) {
        if (x > 10 && x < 20) {
            y = 10;
        }else{
            y = 1;
        }
        y = x > 10 && x < 20 ? 10:1;
        return x > 10 && x < 20 ? 10:1;
    }
}