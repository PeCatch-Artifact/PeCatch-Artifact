// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;

abstract contract ERC1155 {

    mapping(address => mapping(uint256 => uint256)) public balanceOf;
    address[] public owners;

     function balanceOfBatch1( uint256[] memory ids)
        public
        view
        virtual
        returns (uint256[] memory balances)
    {
        uint256 ownersLength = owners.length;

        require(ownersLength == ids.length, "LENGTH_MISMATCH");

        balances = new uint256[](owners.length);

        // Unchecked because the only math done is incrementing
        // the array index counter which cannot possibly overflow.
        unchecked {
            for (uint256 i = 0; i < ownersLength; i++) {
                balances[i] = balanceOf[owners[i]][ids[i]];
            }
        }
    }

 function balanceOfBatch2(uint256[] memory ids)
        public
        view
        virtual
        returns (uint256[] memory balances)
    {
        uint256 ownersLength = owners.length; 

        require(ownersLength == ids.length, "LENGTH_MISMATCH");

        balances = new uint256[](ownersLength);

        // Unchecked because the only math done is incrementing
        // the array index counter which cannot possibly overflow.
        unchecked {
            for (uint256 i = 0; i < ownersLength; i++) {
                balances[i] = balanceOf[owners[i]][ids[i]];
            }
        }
    }

}
