// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.15;

contract Test {
    function log2(uint256 value) internal pure returns (uint256) {
        uint256 result = 0;
        unchecked {
            if (value >> 128 > 0) {
                value >>= 128;
                result += 128;
            }
            if (value >> 64 > 0) {
                value >>= 64;
                result += 64;
            }
            if (value >> 32 > 0) {
                value >>= 32;
                result += 32;
            }
            if (value >> 16 > 0) {
                value >>= 16;
                result += 16;
            }
            if (value >> 8 > 0) {
                value >>= 8;
                result += 8;
            }
            if (value >> 4 > 0) {
                value >>= 4;
                result += 4;
            }
            if (value >> 2 > 0) {
                value >>= 2;
                result += 2;
            }
            if (value >> 1 > 0) {
                result += 1;
            }
        }
        return result;
    }

    // function processProof(bytes32[] memory proof, bytes32 leaf) internal pure returns (bytes32) {
    //     bytes32 computedHash = leaf;
    //     for (uint256 i = 0; i < proof.length; i++) {
    //     }
    //     return computedHash;
    // }

    // /**
    //  * @dev Calldata version of {processProof}
    //  *
    //  * _Available since v4.7._
    //  */
    // function processProofCalldata(bytes32[] calldata proof, bytes32 leaf) internal pure returns (bytes32) {
    //     bytes32 computedHash = leaf;
    //     for (uint256 i = 0; i < proof.length; i++) {
    //         bytes32 a = proof[i];
    //     }
    //     return computedHash;
    // }

}