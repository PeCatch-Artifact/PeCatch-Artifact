// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;

library CheckpointsUpgradeable {
    struct History {
        Checkpoint[] _checkpoints;
    }

    struct Checkpoint {
        uint32 _blockNumber;
        uint224 _value;
    }
}

contract GovernorVotesQuorumFractionUpgradeable {
    using CheckpointsUpgradeable for CheckpointsUpgradeable.History;

    uint256 private _quorumNumerator; // DEPRECATED
    CheckpointsUpgradeable.History private _quorumNumeratorHistory;

    event QuorumNumeratorUpdated(uint256 oldQuorumNumerator, uint256 newQuorumNumerator);


    function quorumNumerator(uint256 blockNumber) public view virtual returns (uint256) {
        // If history is empty, fallback to old storage
        uint256 length = _quorumNumeratorHistory._checkpoints.length;
        if (length == 0) {
            return _quorumNumerator;
        }

        // Optimistic search, check the latest checkpoint
        CheckpointsUpgradeable.Checkpoint memory latest = _quorumNumeratorHistory._checkpoints[length - 1];
        if (latest._blockNumber <= blockNumber) {
            return latest._value;
        }

        return _quorumNumerator;
    }

}