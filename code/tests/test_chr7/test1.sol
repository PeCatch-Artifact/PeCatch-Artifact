// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.15;

contract UncheckedLoopDemo {
    function smallTest0(uint256 times) public pure {
        uint256 pos = 0;
        uint256 index = 0;
        uint256[] memory hashes = new uint256[](times);

        for (uint256 i = 0; i < times; i++) {
            index++;
            hashes[pos++] = 1;
        }
    }

    function smallTest1(uint256 times) public pure {
        uint256 pos = 0;
        uint256 index = 0;
        uint256[] memory hashes = new uint256[](times);

        unchecked {
            for (uint256 i = 0; i < times; i++) {
                index++;
                hashes[pos++] = 1;
            }
        }  
    }

    function smallTest2(uint256 times) public pure {
        uint256 pos = 0;
        uint256 index = 0;
        uint256[] memory hashes = new uint256[](times);

        for (uint256 i = 0; i < times; i++) {
            unchecked {
                index++;
                hashes[pos++] = 1;
            }
        }
    }

    function processMultiProof(
        bytes32[] memory proof,
        bool[] memory proofFlags,
        bytes32[] memory leaves
    ) internal pure returns (bytes32 merkleRoot) {
        // This function rebuild the root hash by traversing the tree up from the leaves. The root is rebuilt by
        // consuming and producing values on a queue. The queue starts with the `leaves` array, then goes onto the
        // `hashes` array. At the end of the process, the last hash in the `hashes` array should contain the root of
        // the merkle tree.
        uint256 leavesLen = leaves.length;
        uint256 totalHashes = proofFlags.length;

        // Check proof validity.
        require(leavesLen + proof.length + 1 == totalHashes, "MerkleProof: invalid multiproof");

        // The xxxPos values are "pointers" to the next value to consume in each array. All accesses are done using
        // `xxx[xxxPos++]`, which return the current value and increment the pointer, thus mimicking a queue's "pop".
        bytes32[] memory hashes = new bytes32[](totalHashes);
        uint256 leafPos = 0;
        uint256 hashPos = 0;
        uint256 proofPos = 0;
        // At each step, we compute the next hash using two values:
        // - a value from the "main queue". If not all leaves have been consumed, we get the next leaf, otherwise we
        //   get the next hash.
        // - depending on the flag, either another value for the "main queue" (merging branches) or an element from the
        //   `proof` array.
        for (uint256 i = 0; i < totalHashes; i++) {
            bytes32 a = leafPos < leavesLen ? leaves[leafPos++] : hashes[hashPos++];
            bytes32 b = proofFlags[i] ? leafPos < leavesLen ? leaves[leafPos++] : hashes[hashPos++] : proof[proofPos++];
        }

        if (totalHashes > 0) {
            return hashes[totalHashes - 1];
        } else if (leavesLen > 0) {
            return leaves[0];
        } else {
            return proof[0];
        }
    }
}