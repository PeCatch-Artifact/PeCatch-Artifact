// SPDX-License-Identifier: MIT

pragma solidity >= 0.8.0;

contract SimpleStorage {
    uint256 public totalSupply;
    uint256 public totalConsume;
    mapping(address => uint256) public balanceOf;

    function transfer(address to, uint256 value) external returns (bool) {
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;

        return true;
    } 

    function _mint(address to, uint256 value) internal {
        totalSupply += value;
        balanceOf[to] += value;
    } 

    function _burn(address from, uint256 value) internal {
        balanceOf[from] -= value;
        totalSupply -= value;
        totalConsume += value;
    }

    function test1(uint x) public pure returns (uint) {
        uint a = 0;
        uint b = 0;
        uint c = 3;

        if (x > 100) {
            a = a + 100;
            b = b + 100;
        } else {
            a = a + c;
            b = b + c;
        } 
        return a + b;
    }

    function test2(uint x) public pure returns (uint) {
        uint a = 0;
        uint b = 0;
        uint c = 3;

        if (x > 100) {
            a = a + 100;
            b = b + c;
        } else {
            a = a + c;
            b = b + 100;
        } 
        return a + b;
    }

    function test3() public pure returns (uint) {
        uint a = 0;
        uint b = 0;
        uint c = 3;

        while (c != 0) {
            a += 100;
            b += 101;
            c -= 1;
        }

        return a + b; 
    }

    function test4() public pure returns (uint) {
        uint a = 0;
        uint b = 0;
        uint c = 3;

        while (c != 0) {
            a += 100;
            c -= 1;
        }

        b += 101;

        return a + b; 
    }



    function test2(uint x, uint y) public pure returns (uint ret) {
        if ( x != 0 ) {
            if (y != 0) {
                return 100;
            }
        }

        return 101;
    }
}