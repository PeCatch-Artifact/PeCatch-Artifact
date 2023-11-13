// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;

//solmate#76
abstract contract Auth {

    event OwnerUpdated(address indexed newOwner);

    event AuthorityUpdated(Authority indexed newAuthority);

    address public owner;

    Authority public authority;

    constructor(address _owner, Authority _authority) {
        owner = _owner;
        authority = _authority;
    }

    function setOwener1(address newOwner) public virtual {
        owner = newOwner;

        emit OwnerUpdated(owner);
    }

    function setOwener2(address newOwner) public virtual {
        owner = newOwner;

        emit OwnerUpdated(newOwner);
    }

    function setAuthority1(Authority newAuthority) public virtual {
        authority = newAuthority;

        emit AuthorityUpdated(authority);
    }

    function setAuthority2(Authority newAuthority) public virtual {
        authority = newAuthority;

        emit AuthorityUpdated(newAuthority);
    }
}

interface Authority {
    function canCall(
        address user,
        address target,
        bytes4 functionSig
    ) external view returns (bool);
}


contract Ownable {
    address private _owner;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    /**
     * @dev Initializes the contract setting the deployer as the initial owner.
     */
    constructor () {       
        _owner = _msgSender();
        emit OwnershipTransferred(address(0), _owner);
    }

    function _msgSender() internal view virtual returns (address) {
        return msg.sender;
    }
}


contract Secondary {
    address private _primary;

    /**
     * @dev Emitted when the primary contract changes.
     */
    event PrimaryTransferred(
        address recipient
    );

    /**
     * @dev Sets the primary account to the one that is creating the Secondary contract.
     */
    constructor () {
        _primary = _msgSender();
        emit PrimaryTransferred(_primary);
    }

    function transferPrimary(address recipient) public {
        require(recipient != address(0), "Secondary: new primary is the zero address");
        _primary = recipient;
        emit PrimaryTransferred(_primary);
    }

    function _msgSender() internal view virtual returns (address) {
        return msg.sender;
    }
}

