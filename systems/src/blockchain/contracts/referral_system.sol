// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ReferralSystem {
    address public owner;
    mapping(address => address) public referrals;  // stores who referred whom
    mapping(address => uint256) public balances;

    constructor() {
        owner = msg.sender;
    }

    function refer(address referrer) public {
        require(referrals[msg.sender] == address(0), "Already referred");
        referrals[msg.sender] = referrer;
    }

    function reward(address recipient, uint256 amount) public {
        require(msg.sender == owner, "Only owner can reward");
        balances[recipient] += amount;
        // Pay referrer 10%
        address referrer = referrals[recipient];
        if (referrer != address(0)) {
            balances[referrer] += amount / 10;
        }
    }

    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance to withdraw");
        balances[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }
}
