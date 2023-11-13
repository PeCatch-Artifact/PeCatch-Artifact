// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.15;

contract ERC777 {
    mapping(address => uint256) private _balances;
    uint256 private _totalSupply;

    function _mint(
        address account,
        uint256 amount
    ) internal virtual {
        require(account != address(0), "ERC777: mint to the zero address");

        // Update state variables
        _totalSupply += amount;
        _balances[account] += amount;
    }

    function _burn(
        address from,
        uint256 amount,
        bytes memory data,
        bytes memory operatorData
    ) internal virtual {
        // require(from != address(0), "ERC777: burn from the zero address");
        // Update state variables
        uint256 fromBalance = _balances[from];
        // require(fromBalance >= amount, "ERC777: burn amount exceeds balance");
        unchecked {
            _balances[from] = fromBalance - amount;
        }
        _totalSupply -= amount;
    }

    function _burn2(
        address from,
        uint256 amount,
        bytes memory data,
        bytes memory operatorData
    ) internal virtual {
        // require(from != address(0), "ERC777: burn from the zero address");
        // Update state variables
        uint256 fromBalance = _balances[from];
        uint256 ts = _totalSupply;
        // require(fromBalance >= amount, "ERC777: burn amount exceeds balance");
        _totalSupply = ts + amount;
        _balances[from] = fromBalance + amount;
    }

    function _move(
        address operator,
        address from,
        address to,
        uint256 amount,
        bytes memory userData,
        bytes memory operatorData
    ) private {
        uint256 fromBalance = _balances[from];
        require(fromBalance >= amount, "ERC777: transfer amount exceeds balance");
        unchecked {
            _balances[from] = fromBalance - amount;
        }
        _balances[to] += amount;
    }

}