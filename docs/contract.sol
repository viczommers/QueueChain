// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ValueSortedStorage {
    bool private locked;
    struct Submission {
        string data;
        uint256 value;
        address submitter;
        uint256 timestamp;
    }
    
    Submission[] private submissions;
    address public owner;
    uint256 public lastPopTime;
    uint256 public constant POP_INTERVAL = 3 minutes;
    uint256 public constant MAX_QUEUE_SIZE = 200;
    
    event SubmissionAdded(string data, uint256 value, address indexed submitter);
    event SubmissionPopped(string data, uint256 value, address indexed submitter);
    event PaymentReceived(address indexed payer, uint256 amount);
    
    modifier nonReentrant() {
        require(!locked, "Reentrant call");
        locked = true;
        _;
        locked = false;
    }
    
    constructor() {
        owner = msg.sender;
        lastPopTime = block.timestamp;
        
        // Add 3 default songs
        submissions.push(Submission({
            data: "https://youtu.be/qORYO0atB6g?t=45",
            value: 3 wei,
            submitter: owner,
            timestamp: block.timestamp
        }));
        
        submissions.push(Submission({
            data: "https://youtu.be/pCx5Std7mCo?t=39",
            value: 2 wei,
            submitter: owner,
            timestamp: block.timestamp
        }));
        submissions.push(Submission({
            data: "https://youtu.be/IslF_EyhMzg?t=25",
            value: 1 wei,
            submitter: owner,
            timestamp: block.timestamp
        }));
        
    }
    
    function submitData(string calldata _data) external payable nonReentrant {
        require(bytes(_data).length <= 42, "String must be 42 characters or less");
        require(msg.value > 0, "Must send some ether");
        require(submissions.length < MAX_QUEUE_SIZE, "Queue is full");
        
        Submission memory newSubmission = Submission({
            data: _data,
            value: msg.value,
            submitter: msg.sender,
            timestamp: block.timestamp
        });
        
        insertSorted(newSubmission);
        
        (bool success, ) = payable(owner).call{value: msg.value}("");
        require(success, "Transfer failed");
        
        emit SubmissionAdded(_data, msg.value, msg.sender);
        emit PaymentReceived(msg.sender, msg.value);
    }
    
    function insertSorted(Submission memory newSubmission) private {
        if (submissions.length == 0) {
            submissions.push(newSubmission);
            return;
        }
        
        uint256 insertIndex = submissions.length;
        for (uint256 i = 1; i < submissions.length; i++) {
            if (newSubmission.value > submissions[i].value) {
                insertIndex = i;
                break;
            }
        }
        
        if (insertIndex == submissions.length && submissions.length == MAX_QUEUE_SIZE) {
            return;
        }
        
        if (submissions.length < MAX_QUEUE_SIZE) {
            submissions.push();
        }
        
        for (uint256 j = submissions.length - 1; j > insertIndex; j--) {
            submissions[j] = submissions[j - 1];
        }
        submissions[insertIndex] = newSubmission;
    }
    
    function popIfReady() external {
        require(block.timestamp >= lastPopTime + POP_INTERVAL, "3 minutes have not passed yet");
        require(submissions.length > 0, "No submissions to pop");
        
        Submission memory poppedSubmission = submissions[0];
        
        for (uint256 i = 0; i < submissions.length - 1; i++) {
            submissions[i] = submissions[i + 1];
        }
        submissions.pop();
        
        lastPopTime = block.timestamp;
        
        emit SubmissionPopped(poppedSubmission.data, poppedSubmission.value, poppedSubmission.submitter);
    }
    
    function getSubmissions() external view returns (Submission[] memory) {
        return submissions;
    }
    function getSubmissionByIndex(uint256 index) external view returns (string memory data, uint256 value, address submitter, uint256 timestamp) {
        require(index < submissions.length, "Index out of bounds");
        Submission memory submission = submissions[index];
        return (submission.data, submission.value, submission.submitter, submission.timestamp);
    }
    
    function getDataByIndex(uint256 index) external view returns (string memory) {
        require(index < submissions.length, "Index out of bounds");
        return submissions[index].data;
    }
    
    function getTimestampByIndex(uint256 index) external view returns (uint256) {
        require(index < submissions.length, "Index out of bounds");
        return submissions[index].timestamp;
    }
    
    function getSubmitterByIndex(uint256 index) external view returns (address) {
        require(index < submissions.length, "Index out of bounds");
        return submissions[index].submitter;
    }
    
    function getSubmissionCount() external view returns (uint256) {
        return submissions.length;
    }
    
    function getTopSubmission() external view returns (string memory data, uint256 value, address submitter, uint256 timestamp) {
        require(submissions.length > 0, "No submissions available");
        Submission memory top = submissions[0];
        return (top.data, top.value, top.submitter, top.timestamp);
    }
    
    function getTimeUntilNextPop() external view returns (uint256) {
        if (block.timestamp >= lastPopTime + POP_INTERVAL) {
            return 0;
        }
        return (lastPopTime + POP_INTERVAL) - block.timestamp;
    }
    
    function getCurrentSong() external view returns (string memory data, uint256 timeRemaining) {
        require(submissions.length > 0, "No songs in queue");
        
        uint256 timeUntilPop;
        if (block.timestamp >= lastPopTime + POP_INTERVAL) {
            timeUntilPop = 0;
        } else {
            timeUntilPop = (lastPopTime + POP_INTERVAL) - block.timestamp;
        }
        
        return (submissions[0].data, timeUntilPop);
    }
}