// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract OwnershipRegistry {
    struct Record {
        address owner;
        uint256 timestamp;
    }

    mapping(bytes32 => Record) public records;

    event Registered(bytes32 indexed uuidHash, address indexed owner, uint256 timestamp);

    function register(bytes32 uuidHash) external {
        require(records[uuidHash].owner == address(0), "Already registered");
        records[uuidHash] = Record(msg.sender, block.timestamp);
        emit Registered(uuidHash, msg.sender, block.timestamp);
    }

    function getOwner(bytes32 uuidHash) external view returns (address owner, uint256 timestamp) {
        Record memory r = records[uuidHash];
        return (r.owner, r.timestamp);
    }
}
