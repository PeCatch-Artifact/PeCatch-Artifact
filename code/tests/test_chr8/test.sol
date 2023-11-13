// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.15;

contract Test {

    uint256 a;
    uint256 b;

    function test1(uint256 amount) public pure {
        uint256 c = 10;
        require(c <= amount);
        uint256 res = amount - c;

        c = 20;
        res = amount - c;        
    }

    function test2(uint256 amount) public view {
        uint256 c = 10;
        bool tmp = amount >= c;
        require(tmp);
        uint256 res = amount - c;  

        if (b > a) {
            res = b - a;
        }      
        c = b - a;
    }

    function test3(uint256 amount) public view {
        uint256 c = 10;
        require(amount - c >= 0);
        uint256 res = amount - c;  

        if (b > a) {
            
        }
        res = b - a;   
    }

    function test4(uint256 amount) public view {
        uint256 c = 10;
        bool tmp = amount - c >= 0;
        require(tmp);
        uint256 res = amount - c;  

        if (b - a > 0) {
            res = b - a;
        }
        c = b - a;   
    }
}
