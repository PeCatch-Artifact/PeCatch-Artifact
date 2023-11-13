// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;

contract Test {

    struct Order {
        uint256 length;
        uint[] offer;
        uint256 a;
    }
    uint256[] intArr;
    uint256 constant cona = 1;

    function test1(uint[] memory arr) public {
        for (uint256 i = 0; i < arr.length; ++i) {
            arr[i]+=1;
            uint256 bb = cona;
        }

        for (uint256 i = arr.length; i > 0; --i) {
            arr[i] += 1;
        }

        uint256 j = 0;
        while(j < arr.length){
            j++;
        }

        uint256 k = 10;
        do{
            k--;
        }while(arr.length > k);
    }

    function test2(uint[] memory arr) public {
        uint l = arr.length;
        for (uint256 i = 0; i < l; ++i) {
            arr[i]+=1;
        }
    }

    function processMultiProofCalldata(
        bytes32[] calldata proof,
        bool[] calldata proofFlags,
        bytes32[] memory leaves
    ) internal pure returns (bytes32 merkleRoot) {
        // This function rebuild the root hash by traversing the tree up from the leaves. The root is rebuilt by
        // consuming and producing values on a queue. The queue starts with the `leaves` array, then goes onto the
        // `hashes` array. At the end of the process, the last hash in the `hashes` array should contain the root of
        // the merkle tree.
        uint256 leavesLen = leaves.length;
        uint256 totalHashes = proofFlags.length;

        // Check proof validity.
        require(leavesLen + proof.length - 1 == totalHashes, "MerkleProof: invalid multiproof");

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
        for (uint256 i = 0; i < proofFlags.length; i++) {
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

    function test3(Order memory o) public {
        for (uint256 i = 0; i < o.length; ++i) {
            o.length = 3;
        }
    }

    function test4(Order memory o) public {
        uint l = o.length;
        for (uint256 i = 0; i < l; ++i) {
        }
    }

    function test5() public {
        intArr[0] = 1;
        for (uint256 i = 0; i < intArr.length - 1; ++i) {
            intArr[i+1] = 1;
        }

        for (uint256 i = intArr.length - 1; i > 0; --i) {
            intArr[i+1] = 1;
        }

        for (uint256 i = 0; i < intArr.length; ++i) {
            intArr.push(1);
        }
    }

    function test6(Order memory o) public {
        uint256 t = 3;
        for (uint256 i = 0; i < o.offer.length * t; ++i) {
            uint256 l = intArr[i];
            uint256 a = o.a;
            uint256 b = o.offer[i];
            l = intArr[b];
        }

        for (uint256 i = 0; i < o.a; ++i) {
        }
    }

}