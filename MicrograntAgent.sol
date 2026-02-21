//Code to be pasted in Remix IDE


// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MicroGrantVault {
    event GrantIssued(address indexed student, uint256 amount, string reason);

    // Function to allow the AI Agent to send funds with a reason
    function awardGrant(address payable student, string memory reason) public payable {
        require(msg.value > 0, "Grant must be > 0");
        student.transfer(msg.value);
        emit GrantIssued(student, msg.value, reason);
    }
}
