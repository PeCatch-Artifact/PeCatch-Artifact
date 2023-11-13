// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;

contract Address {

    function isContract(address account) internal view returns (bool) {
        bytes32 codehash;
        bytes32 accountHash = 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470;
        assembly { codehash := extcodehash(account) }
        return (codehash != 0x0 && codehash != accountHash);

    }

    function test2(address account) internal view returns (bool) {
        bytes32 codehash;
        assembly { codehash := extcodehash(account) }
        return (codehash != 0x0 && codehash != 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470);
    }

    function test3(address account) internal view returns (bool) {
        bytes32 codehash;
        assembly { codehash := extcodehash(account) }
        codehash = 0xc5d2111111f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470;
        return (codehash != 0x0 && codehash != 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470);
    }

    function test4(address account) internal view returns (bool) {
        bytes32 codehash;
        bytes32 accountHash = 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470;
        assembly { codehash := extcodehash(account) }
        accountHash = 0xc5d2111111f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470;
        return (codehash != 0x0 && codehash != accountHash);

    }
}