// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.15;


abstract contract Initializable {
    uint8 private _initialized;
    bool private _initializing;
}

contract BoolDemo1 is Initializable {
    bool private _paused;

}