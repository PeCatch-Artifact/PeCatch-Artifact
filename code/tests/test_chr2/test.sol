// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;

contract SimpleTest {
    function mul1(uint256 a, uint256 b) public pure returns (uint256) {
        if (a==0) {
            return 0;
        }

        uint256 c = a * b;
        return c;
    }

    function mul2(uint256 a, uint256 b) public pure returns (uint256 c) {
        if (a==0) {
            return 0;
        }

        c = a * b;
        return c;
    }

    function mul3(uint256 a, uint256 b) public pure returns (uint256 c1, uint256) {
        c1 = a * b;
        uint256 c2 = a * b + 1;

        return (c1, c2);
    }

    function mul4(uint256 a, uint256 b) public pure returns (uint256, uint256) {
        uint256 c1 = a * b;
        uint256 c2 = a * b + 1;

        return (c1, c2);
    }

    function mul5(uint256 a, uint256 b) public pure returns (uint256 c1, uint256) {
        c1 = a * b;

        return (c1, a * b + 1);
    }

    function mul6(uint256 a, uint256 b) public pure returns (uint256 c1, uint256, uint256) {
        c1 = a * b;
        
        return (c1, a * b + 1, a * b + 2);
    }

    function test() public returns (uint256, bool) {
        uint256 c = 1;
        (uint256 a, uint256 b) = (1, 3);
        (a,b) = (2,4);
        return (a, b==2);
    }

}