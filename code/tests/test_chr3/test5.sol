// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;

contract Test {
    uint a = 0;
    uint[] arr = [1,2,3];
    mapping(uint=>uint) map;
    Config public config;
    uint constant c = 1;

    struct Config {
        uint256 a;
        uint256 b;
        uint256 c;
    }

    function add() public {
        a++;
    }

    function f0() public {
        uint b = a;
        // uint c = a;
        arr[1] = a;
        b++;
    }

    function f1() public {
        uint b = a;
        arr[a] = 0;
        b++;
    }

    function f2() public {
        uint b = a;
        arr[0] = a;
        b++;
    }

    function f3() public {
        uint b = 1;
        a = b;
        uint c = a+1;
    }

    function f4() public {
        map[0] = 1;
        // arr[a] = 0;
        uint b = map[0];
        // map[a] = 1;
        // map[a] = 2;
        // map[1] = b;
        uint c = map[b];
        (b,c) = (1,2);
        c = map[b];
        b += 1;
        c = map[b];
    }

    function f5() public {
        arr[0] = arr[0] + 1;
    }

    function f6() public {
        config.a = 1;
        config.b = 2;
        uint aa = config.a;
    }
    
}