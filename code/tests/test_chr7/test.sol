// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.15;

contract ERC20 {
    event Transfer(address indexed from, address indexed to, uint256 value);
    
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    uint256 public a = 4;
    uint256 public b = 2;
    uint256 public c;

    constructor() {
        c = 3;
        b += 1;
        b = c + 1;
    }

    function transfer(address to, uint256 value) external returns (bool) {
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;
        emit Transfer(msg.sender, to, value);

        return true;

    }

    function transfer2(address to, uint256 value) external returns (bool) {
        balanceOf[msg.sender] -= value;
        unchecked {
            balanceOf[to] += value;   
        }
        emit Transfer(msg.sender, to, value);

        return true;

    }

    function _mint(address to, uint256 value) internal {
        totalSupply += value;
        balanceOf[to] += value;
        emit Transfer(address(0), to, value);
    }

    function _mint2(address to, uint256 value) internal {
        totalSupply += value;
        unchecked {
            balanceOf[to] += value;    
        }
        emit Transfer(address(0), to, value);
    }

    function test() public pure{
        uint256 l1 = 1;
        uint256 l2;
        uint256 l3;
        l1+=4;
        l2+=4;
        l3 = l1 + 1;
        uint256 ite = 10;

        for(uint256 i = 0;i<ite;i++){
            l3 = l2 + 1;
        }
    }
}