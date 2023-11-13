// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;


contract ReentrancyGuard {

    struct Book { 
        bool title;
        bytes4 author;
    }

   /**
    * @dev We use a single lock for the whole contract.
    */
    bytes4 d;
    bool private reentrancyLock = false;
    Book book;
    uint256 private a;
    uint256 private c;
    uint[] private arr;
    bool private b;
    mapping(address => uint256) public balanceOf;

   /**
    * @dev Prevents a contract from calling itself, directly or indirectly.
    * If you mark a function `nonReentrant`, you should also
    * mark it `external`. Calling one `nonReentrant` function from
    * another is not supported. Instead, you can implement a
    * `private` function doing the actual work, and an `external`
    * wrapper marked as `nonReentrant`.
    */
    modifier nonReentrant() {
        require(!reentrancyLock);
        reentrancyLock = true;
        _;
        reentrancyLock = false;
    }

    function test() public nonReentrant returns(uint) {
        return 1 + 2;
    }

}