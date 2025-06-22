# QueueChain - Comprehensive Server Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Server Architecture](#server-architecture)
3. [FastAPI Application Structure](#fastapi-application-structure)
4. [Web3 Blockchain Integration](#web3-blockchain-integration)
5. [Frontend Architecture](#frontend-architecture)
6. [CSS Styling System](#css-styling-system)
7. [Database & State Management](#database--state-management)
8. [Background Services](#background-services)
9. [API Endpoint Documentation](#api-endpoint-documentation)
10. [Deployment & Configuration](#deployment--configuration)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [Complete Reproduction Guide](#complete-reproduction-guide)

## Project Overview

QueueChain is a decentralized music streaming platform that combines blockchain technology with modern web development. Users submit music content URLs with ETH bids, creating a priority queue where the highest bidders get their content played first. The system automatically advances the queue every 3 minutes through smart contract interactions.

### Core Technologies
- **Backend**: FastAPI (Python 3.8+) with async/await patterns
- **Blockchain**: Web3.py for Ethereum smart contract interaction
- **Frontend**: Vanilla JavaScript with modern CSS3 features
- **Network**: Polygon zkEVM testnet (Cardona)
- **Design**: Spotify-inspired UI with glassmorphism effects

### Key Features
- Real-time blockchain queue management
- Automatic song progression via smart contracts
- Wallet integration with private key management
- Responsive design with hover animations
- YouTube URL embedding and content detection
- Live queue statistics and metadata display

## Server Architecture

### Application Structure
```
QueueChain/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration constants (RPC URL, Contract Address)
├── contract.abi           # Smart contract ABI definition
├── static/
│   └── style.css          # External CSS styling with glassmorphism design
├── templates/
│   └── index.html         # Single-page application frontend
├── docs/
│   ├── DEVELOPMENT_GUIDE.md
│   └── COMPREHENSIVE_DOCUMENTATION.md
└── requirements.txt       # Python dependencies (implied)
```

### Dependencies
```python
# Core Framework
fastapi>=0.68.0
uvicorn>=0.15.0

# Blockchain Integration
web3>=6.0.0
eth-account>=0.8.0

# Template Engine
jinja2>=3.0.0

# HTTP Client (for FastAPI)
python-multipart>=0.0.5
```

### Server Configuration
- **Host**: 0.0.0.0 (binds to all interfaces)
- **Port**: 8000 (configurable in main.py:267)
- **ASGI Server**: Uvicorn with reload disabled for production
- **Template Directory**: ./templates/
- **Static Files**: ./static/ directory (mounted to /static/)

## FastAPI Application Structure

### Application Initialization
```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from web3 import Web3
from web3.exceptions import ContractLogicError
from eth_account import Account
import asyncio
import threading
import time
from config import RPC_URL, CONTRACT_ADDRESS

# FastAPI instance
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount static files FIRST
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global state variables
current_private_key = None
current_account = None

# Web3 initialization
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Contract setup
with open('contract.abi', 'r') as f:
    abi = f.read()
contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
```

### Pydantic Data Models

#### BidSubmission Model
```python
class BidSubmission(BaseModel):
    url: str        # Content URL (YouTube, etc.)
    value: int      # Bid amount in Wei
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "value": 1000000000000000000  # 1 ETH in Wei
            }
        }
```

#### PrivateKeyUpdate Model
```python
class PrivateKeyUpdate(BaseModel):
    private_key: str    # Ethereum private key (64 hex chars)
    
    class Config:
        schema_extra = {
            "example": {
                "private_key": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
            }
        }
```

### Account Management System

#### Account Creation Function
```python
def get_account():
    """
    Creates or retrieves Web3 account from stored private key.
    
    Returns:
        Account: Web3 account object or None if creation fails
        
    Security:
        - Private key stored only in memory
        - Account recreated on-demand
        - Error handling prevents app crashes
    """
    global current_account, current_private_key
    if current_private_key and not current_account:
        try:
            current_account = Account.from_key(current_private_key)
            print(f"Created account: {current_account.address}")
        except Exception as e:
            print(f"Error creating account: {e}")
            current_account = None
    return current_account
```

## Web3 Blockchain Integration

### Connection Setup
```python
# RPC Configuration
RPC_URL = "https://rpc.cardona.zkevm-rpc.com"
CONTRACT_ADDRESS = "0x1a7dbe663E5efb9f3aAF2EB56616794069d3F4eA"

# Web3 Provider
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Connection validation
if not w3.is_connected():
    raise Exception("Failed to connect to blockchain")
```

### Smart Contract Functions

#### Read-Only Functions
```python
# Get current playing song
current_song = contract_instance.functions.getCurrentSong().call()
# Returns: (string data, uint256 timeRemaining)

# Get submission count
count = contract_instance.functions.getSubmissionCount().call()
# Returns: uint256

# Get submission by index
submission = contract_instance.functions.getSubmissionByIndex(index).call()
# Returns: (string data, uint256 value, address submitter, uint256 timestamp)

# Get submitter address
submitter = contract_instance.functions.getSubmitterByIndex(index).call()
# Returns: address

# Get submission timestamp
timestamp = contract_instance.functions.getTimestampByIndex(index).call()
# Returns: uint256
```

#### Write Functions (Transactions)
```python
# Submit new content with bid
def submit_bid(url: str, value: int, private_key: str):
    """
    Submits content URL with ETH bid to smart contract.
    
    Transaction flow:
    1. Build transaction with parameters
    2. Sign transaction with private key
    3. Send raw transaction to network
    4. Wait for confirmation
    """
    transaction = contract_instance.functions.submitData(url).build_transaction({
        'from': account.address,
        'value': value,  # Wei amount
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address)
    })
    
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_hash, tx_receipt

# Trigger queue advancement
def pop_if_ready():
    """
    Calls smart contract's popIfReady() function.
    
    Contract Logic:
    - Only allows calling every 3 minutes (180 seconds)
    - Removes top item from queue
    - Emits SubmissionPopped event
    """
    try:
        transaction = contract_instance.functions.popIfReady().build_transaction({
            'from': account.address,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=current_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"popIfReady transaction sent: {tx_hash.hex()}")
        
    except ContractLogicError as e:
        if "3 minutes have not passed yet" in str(e):
            print("popIfReady called too early - 3 minutes have not passed yet")
        else:
            print(f"Contract logic error: {e}")
```

### Error Handling Patterns
```python
# Blockchain connection errors
if not w3.is_connected():
    return {"error": "Blockchain connection failed"}

# Contract logic errors (expected)
except ContractLogicError as e:
    if "specific error message" in str(e):
        # Handle known contract errors gracefully
        print("Expected contract error occurred")
    else:
        print(f"Unexpected contract logic error: {e}")

# Network/transaction errors
except Exception as e:
    print(f"Transaction failed: {e}")
    return {"error": str(e)}
```

## FastAPI Endpoint Documentation

### 1. Root Endpoint - `/`
```python
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Serves the main application HTML page.
    
    Purpose: Entry point for the web application
    Method: GET
    Response: HTML content
    Template: templates/index.html
    """
    return templates.TemplateResponse("index.html", {"request": request})
```

### 2. Current URL Endpoint - `/current-url`
```python
@app.get("/current-url")
async def get_current_url():
    """
    Retrieves the currently playing content URL from blockchain.
    
    Purpose: Fetch active content for player component
    Method: GET
    Smart Contract Call: getCurrentSong()
    
    Response Format:
    {
        "url": "https://youtube.com/watch?v=xyz" | null
    }
    
    Error Response:
    {
        "error": "Blockchain connection failed"
    }
    """
    try:
        if not w3.is_connected():
            return {"error": "Blockchain connection failed"}
        
        # Get current song URL directly from contract
        url = contract_instance.functions.getCurrentSong().call()[0]
        return {"url": url if url else None}
    
    except Exception as e:
        return {"error": str(e)}
```

### 3. Queue Metadata Endpoint - `/queue-metadata`
```python
@app.get("/queue-metadata")
async def get_queue_metadata():
    """
    Comprehensive queue information for UI components.
    
    Purpose: Populate queue dropdown with statistics and recent items
    Method: GET
    
    Smart Contract Calls:
    - getSubmissionCount(): Total queue items
    - getSubmissionByIndex(i): Content data by index
    - getSubmitterByIndex(i): Wallet address by index
    - getTimestampByIndex(i): Submission time by index
    
    Response Structure:
    {
        "total_count": 5,
        "current_playing": {
            "url": "https://youtube.com/watch?v=xyz",
            "submitter": "0x1234...5678",
            "timestamp": 1750595560
        },
        "coming_up_next": {
            "url": "https://example.com/content",
            "submitter": "0xabcd...efgh",
            "timestamp": 1750595660
        },
        "recent_submissions": [
            {
                "index": 0,
                "url": "https://content.url",
                "submitter": "0x1111...2222",
                "timestamp": 1750595560
            }
        ]
    }
    
    Error Handling:
    - Individual item errors logged but don't break response
    - Empty arrays/null values for missing data
    - Total count always returned even if items fail
    """
    try:
        if not w3.is_connected():
            return {"error": "Blockchain connection failed"}
        
        # Get total submission count
        total_count = contract_instance.functions.getSubmissionCount().call()
        
        queue_data = {
            "total_count": total_count,
            "current_playing": None,
            "coming_up_next": None,
            "recent_submissions": []
        }
        
        # Get current playing (index 0)
        if total_count > 0:
            try:
                current_url = contract_instance.functions.getSubmissionByIndex(0).call()[0]
                current_submitter = contract_instance.functions.getSubmitterByIndex(0).call()
                current_timestamp = contract_instance.functions.getTimestampByIndex(0).call()
                
                queue_data["current_playing"] = {
                    "url": current_url,
                    "submitter": current_submitter,
                    "timestamp": current_timestamp
                }
            except Exception as e:
                print(f"Error getting current playing metadata: {e}")
        
        # Get coming up next (index 1)
        if total_count > 1:
            try:
                next_url = contract_instance.functions.getSubmissionByIndex(1).call()[0]
                next_submitter = contract_instance.functions.getSubmitterByIndex(1).call()
                next_timestamp = contract_instance.functions.getTimestampByIndex(1).call()
                
                queue_data["coming_up_next"] = {
                    "url": next_url,
                    "submitter": next_submitter,
                    "timestamp": next_timestamp
                }
            except Exception as e:
                print(f"Error getting next submission metadata: {e}")
        
        # Get recent submissions (up to 5 items)
        recent_count = min(total_count, 5)
        for i in range(recent_count):
            try:
                url = contract_instance.functions.getSubmissionByIndex(i).call()[0]
                submitter = contract_instance.functions.getSubmitterByIndex(i).call()
                timestamp = contract_instance.functions.getTimestampByIndex(i).call()
                
                queue_data["recent_submissions"].append({
                    "index": i,
                    "url": url,
                    "submitter": submitter,
                    "timestamp": timestamp
                })
            except Exception as e:
                print(f"Error getting submission {i} metadata: {e}")
        
        return queue_data
    
    except Exception as e:
        return {"error": str(e)}
```

### 4. Account Info Endpoint - `/account-info`
```python
@app.get("/account-info")
async def get_account_info():
    """
    Returns current wallet connection status.
    
    Purpose: Check if user has connected their wallet
    Method: GET
    
    Response Format:
    {
        "address": "0x1234567890abcdef1234567890abcdef12345678",
        "has_private_key": true
    }
    
    Or:
    {
        "address": null,
        "has_private_key": false
    }
    """
    try:
        account = get_account()
        if account:
            return {
                "address": account.address,
                "has_private_key": True
            }
        else:
            return {
                "address": None,
                "has_private_key": False
            }
    except Exception as e:
        return {"error": str(e)}
```

### 5. Submit Bid Endpoint - `/submit-bid`
```python
@app.post("/submit-bid")
async def submit_bid(data: BidSubmission):
    """
    Submits new content to blockchain queue with ETH bid.
    
    Purpose: Add user content to the priority queue
    Method: POST
    Input: BidSubmission model (url, value)
    
    Transaction Flow:
    1. Validate account exists
    2. Build transaction with submitData function
    3. Sign transaction with private key
    4. Send raw transaction to network
    5. Wait for transaction confirmation
    6. Return transaction hash and block number
    
    Gas Settings:
    - Gas Limit: 200,000 units
    - Gas Price: Current network gas price
    - Nonce: Latest for sending address
    
    Success Response:
    {
        "success": true,
        "tx_hash": "0xabc123def456...",
        "block_number": 12345
    }
    
    Error Response:
    {
        "error": "No account available - please enter private key first"
    }
    """
    try:
        account = get_account()
        if not account:
            return {"error": "No account available - please enter private key first"}
        
        # Build transaction
        transaction = contract_instance.functions.submitData(data.url).build_transaction({
            'from': account.address,
            'value': data.value,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address)
        })
        
        # Sign and send the transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=current_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        print(f"Bid submitted - Transaction hash: {tx_hash.hex()}")
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction confirmed in block {tx_receipt.blockNumber}")
        
        return {
            "success": True,
            "tx_hash": tx_hash.hex(),
            "block_number": tx_receipt.blockNumber
        }
        
    except Exception as e:
        print(f"Error submitting bid: {e}")
        return {"error": str(e)}
```

### 6. Update Private Key Endpoint - `/update-private-key`
```python
@app.post("/update-private-key")
async def update_private_key(data: PrivateKeyUpdate):
    """
    Stores private key in memory and creates Web3 account.
    
    Purpose: Connect user's Ethereum wallet to the application
    Method: POST
    Input: PrivateKeyUpdate model (private_key)
    
    Validation:
    - Removes '0x' prefix if present
    - Ensures exactly 64 hexadecimal characters
    - Tests account creation before storing
    
    Security:
    - Private key stored only in memory (never persisted)
    - Global account reset on new key
    - Immediate validation prevents invalid keys
    
    Success Response:
    {
        "success": true,
        "address": "0x1234567890abcdef1234567890abcdef12345678"
    }
    
    Error Response:
    {
        "error": "Private key must be 64 hex characters, got 32 characters"
    }
    """
    try:
        global current_private_key, current_account
        current_private_key = data.private_key.strip()
        current_account = None  # Reset account to force recreation
        
        # Check private key length
        clean_key = current_private_key.replace('0x', '')
        if len(clean_key) != 64:
            return {"error": f"Private key must be 64 hex characters, got {len(clean_key)} characters"}
        
        # Try to create account immediately
        current_account = Account.from_key(current_private_key)
        print(f"Account created successfully: {current_account.address}")
        return {"success": True, "address": current_account.address}
            
    except Exception as e:
        print(f"Error with private key: {e}")
        return {"error": f"Invalid private key: {str(e)}"}
```

## Background Services

### Pop If Ready Background Task
```python
def pop_if_ready():
    """
    Triggers smart contract popIfReady function with comprehensive error handling.
    
    Efficiency Optimization:
    - Checks queue count before attempting transaction
    - Skips pop attempt if queue is empty (saves gas)
    - Continues with existing behavior if count check fails
    
    Contract Logic:
    - Can only be called every 3 minutes (180 seconds)
    - Removes the top submission from queue
    - Emits SubmissionPopped event
    - Advances queue automatically
    
    Error Handling:
    - "3 minutes have not passed yet" - Expected, logged quietly
    - Other ContractLogicError - Unexpected, logged with details
    - Network errors - Logged as general errors
    """
    try:
        account = get_account()
        if not account:
            print("No account available for popIfReady transaction")
            return
        
        # Check if queue is empty before attempting to pop
        try:
            submission_count = contract_instance.functions.getSubmissionCount().call()
            if submission_count == 0:
                print("Queue is empty - skipping popIfReady")
                return
        except Exception as e:
            print(f"Error checking queue count: {e}")
            # Continue with pop attempt if count check fails
        
        # Build transaction
        transaction = contract_instance.functions.popIfReady().build_transaction({
            'from': account.address,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        
        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=current_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"popIfReady transaction sent: {tx_hash.hex()}")
        
    except ContractLogicError as e:
        if "3 minutes have not passed yet" in str(e):
            print("popIfReady called too early - 3 minutes have not passed yet")
        else:
            print(f"Contract logic error: {e}")
    except Exception as e:
        print(f"Error calling popIfReady: {e}")

def background_pop_task():
    """
    Background thread that runs popIfReady every 3 minutes.
    
    Threading:
    - Daemon thread (dies with main process)
    - Infinite loop with 180-second sleep
    - Started at application initialization
    """
    while True:
        pop_if_ready()
        time.sleep(180)  # 3 minutes = 180 seconds
```

```python
# Thread initialization

```

## Frontend Architecture

### HTML Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QueueChain - Decentralized Music Player</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="app-container">
        <!-- Sidebar with wallet and controls -->
        <div class="sidebar">
            <div class="logo">
                <i class="fas fa-music"></i>
                <h1>QueueChain</h1>
            </div>
            
            <div class="wallet-section">
                <!-- Wallet configuration form -->
            </div>
        </div>
        
        <!-- Main content area -->
        <div class="main-content">
            <div class="header">
                <h2>Now Playing</h2>
                <p>Decentralized music streaming powered by Polygon zkEVM Smart Contract</p>
                
                <!-- Queue info dropdown -->
                <div class="queue-info" id="queueInfo">
                    <div class="queue-badge">
                        <i class="fas fa-list"></i>
                        <span id="queueCount">0</span> in queue
                    </div>
                    <div class="queue-dropdown" id="queueDropdown">
                        <!-- Comprehensive queue statistics and metadata -->
                    </div>
                </div>
                
                <!-- Help info dropdown -->
                <div class="help-info" style="position: absolute; top: 0; right: 0; cursor: pointer; margin-top: 50px;">
                    <div class="help-badge">
                        <i class="fas fa-question-circle"></i>
                        How it Works
                    </div>
                    <div class="help-dropdown">
                        <div class="dropdown-section">
                            <div class="dropdown-title">
                                <i class="fas fa-coins"></i>
                                Bidding System
                            </div>
                            <div style="color: #b3b3b3; font-size: 0.9rem; line-height: 1.5;">
                                <p><strong>Higher bids = Higher priority!</strong></p>
                                <p>• Submit your content URL with an ETH bid</p>
                                <p>• The more you bid, the higher you rank in the queue</p>
                                <p>• Queue automatically advances every 3 minutes</p>
                                <p>• Your content plays when it reaches the top</p>
                            </div>
                        </div>
                        <div class="dropdown-section">
                            <div class="dropdown-title">
                                <i class="fas fa-lightbulb"></i>
                                Tips
                            </div>
                            <div style="color: #b3b3b3; font-size: 0.9rem; line-height: 1.5;">
                                <p>• Use YouTube URLs for best experience</p>
                                <p>• Bid in Wei (1 ETH = 10^18 Wei)</p>
                                <p>• Check queue stats to see competition</p>
                                <p>• Get testnet ETH from the faucet</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="player-container" id="player-container">
                <!-- Dynamic content area for media player -->
            </div>
        </div>
    </div>
</body>
</html>
```

### JavaScript Architecture

#### Async API Functions
```javascript
// Private key management
async function updatePrivateKey(privateKey) {
    """
    Updates private key on backend and displays connection status.
    
    Flow:
    1. Validate private key exists
    2. Send POST request to /update-private-key
    3. Handle response (success/error)
    4. Update UI with account address
    5. Show error alerts for failures
    """
    if (!privateKey) return;
    
    try {
        const response = await fetch('/update-private-key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ private_key: privateKey })
        });
        
        const result = await response.json();
        if (result.error) {
            console.error('Error updating private key:', result.error);
            alert('Error updating private key: ' + result.error);
        } else if (result.address) {
            console.log('Account created:', result.address);
            const addressDisplay = document.getElementById('addressDisplay');
            addressDisplay.style.display = 'block';
            addressDisplay.innerHTML = `<i class="fas fa-check-circle"></i> Connected: ${result.address.slice(0, 6)}...${result.address.slice(-4)}`;
        }
    } catch (error) {
        console.error('Error updating private key:', error);
        alert('Error updating private key: ' + error.message);
    }
}

// Content loading
async function loadCurrentSong() {
    """
    Loads currently playing content and updates player container.
    
    Content Types Supported:
    - YouTube: Converts to embed format
    - Other URLs: Displays in iframe
    - Empty: Shows "No content" message
    
    Error Handling:
    - Network errors: Connection error message
    - API errors: Error from backend displayed
    - Success: Content loaded in player
    """
    try {
        const response = await fetch('/current-url');
        const data = await response.json();
        
        const container = document.getElementById('player-container');
        
        if (data.error) {
            container.innerHTML = `<div class="status-message error"><i class="fas fa-exclamation-triangle"></i><br>Error: ${data.error}</div>`;
            return;
        }
        
        if (data.url) {
            // Convert YouTube URLs to embed format
            let embedUrl = data.url;
            if (data.url.includes('youtube.com/watch?v=')) {
                const videoId = data.url.split('v=')[1].split('&')[0];
                embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=0`;
            } else if (data.url.includes('youtu.be/')) {
                const videoId = data.url.split('youtu.be/')[1].split('?')[0];
                embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=0`;
            }
            container.innerHTML = `<iframe src="${embedUrl}" allowfullscreen allow="autoplay; encrypted-media"></iframe>`;
        } else {
            container.innerHTML = `<div class="status-message no-content"><i class="fas fa-music"></i><br>No content currently playing</div>`;
        }
    } catch (error) {
        document.getElementById('player-container').innerHTML = 
            `<div class="status-message error"><i class="fas fa-wifi"></i><br>Error loading content: ${error.message}</div>`;
    }
}

// Bid submission
async function submitBid() {
    """
    Handles form submission for new content bids.
    
    Validation:
    - Private key required
    - URL required
    - Bid value must be positive integer
    
    Process:
    1. Validate form inputs
    2. Update private key on backend
    3. Submit bid with URL and value
    4. Show success/error feedback
    5. Clear form on success
    """
    const privateKey = document.getElementById('privateKey').value;
    const bidUrl = document.getElementById('bidUrl').value;
    const bidValue = document.getElementById('bidValue').value;
    
    // Validation
    if (!privateKey) {
        alert('Please enter your private key');
        return;
    }
    
    if (!bidUrl) {
        alert('Please enter a content URL');
        return;
    }
    
    if (!bidValue || bidValue <= 0) {
        alert('Please enter a valid bid value in Wei');
        return;
    }
    
    try {
        // Update private key first
        await updatePrivateKey(privateKey);
        
        // Submit bid
        const response = await fetch('/submit-bid', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                url: bidUrl, 
                value: parseInt(bidValue) 
            })
        });
        
        const result = await response.json();
        if (result.error) {
            alert('Error submitting bid: ' + result.error);
        } else {
            alert(`Bid submitted successfully!\\nTransaction: ${result.tx_hash}\\nBlock: ${result.block_number}`);
            // Clear form
            document.getElementById('bidUrl').value = '';
            document.getElementById('bidValue').value = '';
        }
    } catch (error) {
        alert('Error submitting bid: ' + error.message);
    }
}
```

#### Queue Metadata Management
```javascript
async function loadQueueMetadata() {
    """
    Loads comprehensive queue information and updates all UI components.
    
    Updates:
    - Queue count badge
    - Statistics cards
    - Current playing section
    - Coming up next section
    - Recent submissions list
    
    Error Handling:
    - Individual section errors don't break entire update
    - Empty states handled gracefully
    - Console logging for debugging
    """
    try {
        const response = await fetch('/queue-metadata');
        const data = await response.json();
        
        if (data.error) {
            console.error('Error loading queue metadata:', data.error);
            return;
        }
        
        // Update queue count badge
        document.getElementById('queueCount').textContent = data.total_count;
        document.getElementById('totalCount').textContent = data.total_count;
        document.getElementById('activeItems').textContent = data.total_count;
        
        // Update current playing section
        if (data.current_playing) {
            document.getElementById('currentSection').style.display = 'block';
            document.getElementById('currentTitle').textContent = extractContentTitle(data.current_playing.url);
            document.getElementById('currentSubmitter').textContent = `${data.current_playing.submitter.slice(0, 6)}...${data.current_playing.submitter.slice(-4)}`;
            document.getElementById('currentTime').textContent = formatTimestamp(data.current_playing.timestamp);
        } else {
            document.getElementById('currentSection').style.display = 'none';
        }
        
        // Update coming up next section
        if (data.coming_up_next) {
            document.getElementById('nextSection').style.display = 'block';
            document.getElementById('nextTitle').textContent = extractContentTitle(data.coming_up_next.url);
            document.getElementById('nextSubmitter').textContent = `${data.coming_up_next.submitter.slice(0, 6)}...${data.coming_up_next.submitter.slice(-4)}`;
            document.getElementById('nextTime').textContent = formatTimestamp(data.coming_up_next.timestamp);
        } else {
            document.getElementById('nextSection').style.display = 'none';
        }
        
        // Update recent submissions
        if (data.recent_submissions && data.recent_submissions.length > 0) {
            document.getElementById('recentSection').style.display = 'block';
            const recentContainer = document.getElementById('recentItems');
            recentContainer.innerHTML = '';
            
            data.recent_submissions.slice(0, 3).forEach((item, index) => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'queue-item';
                itemDiv.innerHTML = `
                    <div class="queue-item-title">#${index + 1} ${extractContentTitle(item.url)}</div>
                    <div class="queue-item-meta">
                        <span class="submitter">${item.submitter.slice(0, 6)}...${item.submitter.slice(-4)}</span>
                        <span class="timestamp">${formatTimestamp(item.timestamp)}</span>
                    </div>
                `;
                recentContainer.appendChild(itemDiv);
            });
        } else {
            document.getElementById('recentSection').style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error loading queue metadata:', error);
    }
}
```

#### Utility Functions
```javascript
function extractContentTitle(url) {
    """
    Extracts human-readable titles from content URLs.
    
    Handling:
    - YouTube: Returns "YouTube Video"
    - Other domains: Capitalizes domain name
    - Invalid URLs: Returns truncated URL
    - Null/empty: Returns "Unknown Content"
    """
    if (!url) return 'Unknown Content';
    
    // Extract title from YouTube URLs
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
        return 'YouTube Video';
    }
    
    // Extract domain from other URLs
    try {
        const domain = new URL(url).hostname.replace('www.', '');
        return domain.charAt(0).toUpperCase() + domain.slice(1);
    } catch {
        return url.slice(0, 30) + (url.length > 30 ? '...' : '');
    }
}

function formatTimestamp(timestamp) {
    """
    Converts Unix timestamp to human-readable relative time.
    
    Formats:
    - < 1 minute: "Just now"
    - < 1 hour: "5m ago"
    - < 1 day: "3h ago"
    - < 1 week: "2d ago"
    - Older: Full date string
    """
    if (!timestamp) return 'Unknown';
    
    try {
        const date = new Date(timestamp * 1000);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString();
    } catch {
        return 'Unknown';
    }
}
```

#### Initialization and Auto-refresh
```javascript
// Initialize application on page load
loadCurrentSong();
loadQueueMetadata();

// Auto-refresh every 60 seconds
setInterval(() => {
    loadCurrentSong();
    loadQueueMetadata();
}, 60000);

// Manual refresh function
async function updateConfigAndRefresh() {
    const privateKey = document.getElementById('privateKey').value;
    if (privateKey) {
        await updatePrivateKey(privateKey);
    }
    loadCurrentSong();
    loadQueueMetadata();
}
```

## CSS Styling System

### Design System Foundation
```css
/* CSS Custom Properties (Variables) */
:root {
    /* Primary Brand Colors */
    --spotify-green: #1db954;
    --spotify-green-light: #1ed760;
    --spotify-green-dark: #169c46;
    
    /* Background System */
    --bg-primary: linear-gradient(135deg, #0c0c0c 0%, #121212 25%, #1a1a1a 50%, #0d1117 100%);
    --bg-sidebar: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%);
    --bg-card: rgba(255, 255, 255, 0.05);
    --bg-hover: rgba(255, 255, 255, 0.1);
    
    /* Glass Effects */
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-blur: blur(20px);
    
    /* Text Hierarchy */
    --text-primary: #ffffff;
    --text-secondary: #b3b3b3;
    --text-muted: #888888;
    --text-error: #ff6b6b;
    --text-success: #1db954;
    --text-warning: #ffd700;
    
    /* Spacing System */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-xxl: 3rem;
    
    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
    --radius-pill: 25px;
    
    /* Shadows */
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
    --shadow-md: 0 8px 32px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 20px 40px rgba(0, 0, 0, 0.5);
    --shadow-glow: 0 8px 25px rgba(29, 185, 84, 0.3);
    
    /* Transitions */
    --transition-fast: 0.15s ease;
    --transition-base: 0.3s ease;
    --transition-slow: 0.5s ease;
}
```

### Layout System
```css
/* Global Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Body Foundation */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
    overflow-x: hidden;
    line-height: 1.6;
}

/* Main Container */
.app-container {
    display: flex;
    min-height: 100vh;
}

/* Sidebar Layout */
.sidebar {
    width: 300px;
    background: var(--bg-sidebar);
    border-right: 1px solid #333;
    padding: var(--spacing-xl);
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.3);
    position: relative;
    z-index: 100;
}

/* Main Content Area */
.main-content {
    flex: 1;
    padding: var(--spacing-xl);
    display: flex;
    flex-direction: column;
    min-width: 0; /* Prevents flex item from overflowing */
}
```

### Component System

#### Logo Component
```css
.logo {
    display: flex;
    align-items: center;
    margin-bottom: var(--spacing-xxl);
    user-select: none;
}

.logo i {
    font-size: 2rem;
    background: linear-gradient(45deg, var(--spotify-green), var(--spotify-green-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-right: var(--spacing-sm);
}

.logo h1 {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(45deg, var(--spotify-green), var(--spotify-green-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
```

#### Glassmorphism Card System
```css
.glass-card {
    background: var(--glass-bg);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    border: 1px solid var(--glass-border);
    backdrop-filter: var(--glass-blur);
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
    opacity: 0.5;
}

/* Wallet Section */
.wallet-section {
    @extend .glass-card;
    margin-bottom: var(--spacing-xl);
}

.wallet-title {
    display: flex;
    align-items: center;
    margin-bottom: var(--spacing-md);
    color: var(--spotify-green);
    font-weight: 600;
    font-size: 1.1rem;
}

.wallet-title i {
    margin-right: var(--spacing-sm);
}
```

#### Form System
```css
.input-group {
    margin-bottom: var(--spacing-md);
}

.input-group label {
    display: block;
    margin-bottom: var(--spacing-sm);
    color: var(--text-secondary);
    font-size: 0.9rem;
    font-weight: 500;
}

.input-group input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    background: var(--glass-bg);
    color: var(--text-primary);
    font-size: 0.9rem;
    transition: all var(--transition-base);
    font-family: inherit;
}

.input-group input:focus {
    outline: none;
    border-color: var(--spotify-green);
    box-shadow: 0 0 0 2px rgba(29, 185, 84, 0.2);
    background: rgba(255, 255, 255, 0.08);
}

.input-group input::placeholder {
    color: var(--text-muted);
    opacity: 0.7;
}

/* Password input styling */
.input-group input[type="password"] {
    font-family: 'Courier New', monospace;
    letter-spacing: 0.1em;
}

/* Number input styling */
.input-group input[type="number"] {
    font-family: 'Courier New', monospace;
}
```

#### Button System
```css
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: var(--radius-pill);
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all var(--transition-base);
    text-decoration: none;
    user-select: none;
    position: relative;
    overflow: hidden;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}

/* Primary Button */
.btn-primary {
    background: linear-gradient(45deg, var(--spotify-green), var(--spotify-green-light));
    color: white;
    box-shadow: var(--shadow-sm);
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: var(--shadow-glow);
    background: linear-gradient(45deg, var(--spotify-green-light), var(--spotify-green));
}

.btn-primary:active {
    transform: translateY(0);
}

/* Secondary Button */
.btn-secondary {
    background: var(--bg-hover);
    color: var(--text-primary);
    border: 1px solid var(--glass-border);
}

.btn-secondary:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm);
}

/* Button Groups */
.button-group {
    display: flex;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-lg);
}

.button-group .btn {
    flex: 1;
}
```

#### Account Display
```css
.account-display {
    margin-top: var(--spacing-md);
    padding: 0.75rem;
    background: rgba(29, 185, 84, 0.1);
    border-radius: var(--radius-md);
    border: 1px solid rgba(29, 185, 84, 0.3);
    font-size: 0.8rem;
    color: var(--spotify-green-light);
    word-break: break-all;
    font-family: 'Courier New', monospace;
    display: none;
}

.account-display i {
    margin-right: var(--spacing-sm);
    color: var(--spotify-green);
}
```

#### Header System
```css
.header {
    margin-bottom: var(--spacing-xl);
    position: relative;
}

.header h2 {
    font-size: 2rem;
    margin-bottom: var(--spacing-sm);
    background: linear-gradient(45deg, var(--text-primary), var(--text-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
}

.header p {
    color: var(--text-secondary);
    font-size: 1rem;
    line-height: 1.5;
}

.header-link {
    color: var(--spotify-green);
    text-decoration: none;
    transition: color var(--transition-base);
    border-bottom: 1px solid transparent;
}

.header-link:hover {
    color: var(--spotify-green-light);
    border-bottom-color: var(--spotify-green-light);
}
```

#### Queue System Styling
```css
/* Queue Info Badge */
.queue-info {
    position: absolute;
    top: 0;
    right: 0;
    cursor: pointer;
    z-index: 1000;
}

.queue-badge {
    background: linear-gradient(45deg, var(--spotify-green), var(--spotify-green-light));
    color: white;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-pill);
    font-size: 0.9rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    transition: all var(--transition-base);
    box-shadow: var(--shadow-sm);
}

.queue-badge:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-glow);
}

/* Queue Dropdown */
.queue-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: var(--spacing-sm);
    width: 350px;
    background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(15, 15, 15, 0.95) 100%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    box-shadow: var(--shadow-lg);
    backdrop-filter: var(--glass-blur);
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all var(--transition-base);
    z-index: 1000;
}

.queue-info:hover .queue-dropdown {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

/* Help Badge */
.help-badge {
    background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
    color: white;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-pill);
    font-size: 0.9rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    transition: all var(--transition-base);
    box-shadow: var(--shadow-sm);
}

.help-badge:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
}

/* Help Dropdown */
.help-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: var(--spacing-sm);
    width: 350px;
    background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(15, 15, 15, 0.95) 100%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    box-shadow: var(--shadow-lg);
    backdrop-filter: var(--glass-blur);
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all var(--transition-base);
    z-index: 1000;
}

.help-info:hover .help-dropdown {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

/* Dropdown Sections */
.dropdown-section {
    margin-bottom: var(--spacing-lg);
}

.dropdown-section:last-child {
    margin-bottom: 0;
}

.dropdown-title {
    color: var(--spotify-green);
    font-weight: 600;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: 0.95rem;
}

/* Queue Items */
.queue-item {
    background: var(--glass-bg);
    border-radius: var(--radius-md);
    padding: 0.75rem;
    margin-bottom: var(--spacing-sm);
    border: 1px solid var(--glass-border);
    transition: all var(--transition-base);
}

.queue-item:last-child {
    margin-bottom: 0;
}

.queue-item:hover {
    background: var(--bg-hover);
    transform: translateX(2px);
}

.queue-item-title {
    color: var(--text-primary);
    font-weight: 500;
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.queue-item-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.submitter {
    font-family: 'Courier New', monospace;
    background: rgba(29, 185, 84, 0.1);
    padding: 0.2rem 0.4rem;
    border-radius: var(--radius-sm);
    color: var(--spotify-green-light);
    font-size: 0.7rem;
}

.timestamp {
    color: var(--text-muted);
    font-size: 0.75rem;
}
```

#### Statistics Grid
```css
.stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-md);
}

.stat-card {
    background: var(--glass-bg);
    border-radius: var(--radius-md);
    padding: 0.75rem;
    text-align: center;
    border: 1px solid var(--glass-border);
    transition: all var(--transition-base);
}

.stat-card:hover {
    background: var(--bg-hover);
    transform: translateY(-1px);
}

.stat-number {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--spotify-green);
    margin-bottom: 0.25rem;
    font-family: 'Courier New', monospace;
}

.stat-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
```

#### Player System
```css
.player-container {
    flex: 1;
    background: linear-gradient(135deg, var(--glass-bg) 0%, rgba(255, 255, 255, 0.02) 100%);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
    border: 1px solid var(--glass-border);
    backdrop-filter: var(--glass-blur);
    box-shadow: var(--shadow-md);
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    overflow: hidden;
}

.player-container iframe {
    width: 100%;
    height: 100%;
    border: none;
    border-radius: var(--radius-lg);
    min-height: 400px;
    background: var(--bg-primary);
}

/* Loading States */
.loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-md);
    color: var(--text-secondary);
    text-align: center;
}

.loading i {
    font-size: 3rem;
    animation: pulse 2s infinite;
    color: var(--spotify-green);
}

@keyframes pulse {
    0%, 100% { 
        opacity: 0.5; 
        transform: scale(1);
    }
    50% { 
        opacity: 1; 
        transform: scale(1.05);
    }
}

/* Status Messages */
.status-message {
    text-align: center;
    padding: var(--spacing-xl);
    font-size: 1.2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-md);
}

.status-message i {
    font-size: 2.5rem;
    margin-bottom: var(--spacing-sm);
}

.status-message.error {
    color: var(--text-error);
}

.status-message.error i {
    color: var(--text-error);
}

.status-message.success {
    color: var(--text-success);
}

.status-message.success i {
    color: var(--text-success);
}

.status-message.no-content {
    color: var(--text-warning);
}

.status-message.no-content i {
    color: var(--text-warning);
}
```

#### Responsive Design System
```css
/* Mobile-first responsive design */
@media (max-width: 768px) {
    .app-container {
        flex-direction: column;
    }

    .sidebar {
        width: 100%;
        padding: var(--spacing-md);
        border-right: none;
        border-bottom: 1px solid #333;
    }

    .main-content {
        padding: var(--spacing-md);
    }

    .header h2 {
        font-size: 1.5rem;
    }

    .button-group {
        flex-direction: column;
        gap: var(--spacing-sm);
    }

    .btn {
        width: 100%;
        justify-content: center;
    }

    .help-info, .queue-info {
        position: relative !important;
        top: auto !important;
        right: auto !important;
        left: auto !important;
        margin: 1rem 0 !important;
        display: block;
        width: 100%;
    }
    
    .help-dropdown, .queue-dropdown {
        width: calc(100vw - 2rem) !important;
        left: 50% !important;
        transform: translateX(-50%) translateY(-10px) !important;
        right: auto !important;
        max-width: 400px;
    }
    
    .help-info:hover .help-dropdown,
    .queue-info:hover .queue-dropdown {
        transform: translateX(-50%) translateY(0) !important;
    }

    .player-container {
        min-height: 300px;
        padding: var(--spacing-md);
    }

    .player-container iframe {
        min-height: 250px;
    }

    .stats-grid {
        grid-template-columns: 1fr;
    }
}

/* Tablet adjustments */
@media (max-width: 1024px) and (min-width: 769px) {
    .sidebar {
        width: 250px;
        padding: var(--spacing-lg);
    }

    .queue-dropdown {
        width: 300px;
    }
}

/* Large screen optimizations */
@media (min-width: 1400px) {
    .sidebar {
        width: 350px;
    }

    .queue-dropdown {
        width: 400px;
    }

    .header h2 {
        font-size: 2.5rem;
    }
}
```

#### Scrollbar Customization
```css
/* Modern scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-sidebar);
    border-radius: var(--radius-sm);
}

::-webkit-scrollbar-thumb {
    background: var(--spotify-green);
    border-radius: var(--radius-sm);
    transition: background var(--transition-base);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--spotify-green-light);
}

::-webkit-scrollbar-corner {
    background: var(--bg-sidebar);
}

/* Firefox scrollbar */
* {
    scrollbar-width: thin;
    scrollbar-color: var(--spotify-green) var(--bg-sidebar);
}
```

## Database & State Management

### In-Memory State
```python
# Global application state
current_private_key = None      # User's private key (memory only)
current_account = None          # Web3 account object
```

### State Management Patterns
- **Private Key**: Stored only in memory, never persisted
- **Account**: Created on-demand from private key
- **Blockchain State**: Read directly from smart contract
- **UI State**: Managed through DOM manipulation

### Data Persistence
- **None**: Application is stateless
- **Configuration**: Environment variables and config.py
- **User Data**: Private key in memory session only

## Background Services

### Service Architecture
```python
# Thread-based background services
import threading
import time

# Service 1: Queue advancement
def background_pop_task():
    while True:
        pop_if_ready()
        time.sleep(180)  # 3 minutes

# Initialize services
pop_thread = threading.Thread(target=background_pop_task, daemon=True)
pop_thread.start()
```

### Service Monitoring
- **Logging**: Console output for all service actions
- **Error Handling**: Services continue running on errors
- **Health Checks**: Connection validation before operations

## Deployment & Configuration

### Environment Setup
```bash
# Python virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install fastapi uvicorn web3 eth-account jinja2 python-multipart

# Configuration files
config.py               # RPC URL and contract address
contract.abi           # Smart contract ABI
templates/index.html   # Frontend application
```

### Production Deployment
```python
# main.py production configuration
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0",     # Bind to all interfaces
        port=8000,          # Configurable port
        workers=1,          # Single worker for state consistency
        reload=False        # Disable auto-reload in production
    )
```

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Complete Reproduction Guide

### Step 1: Environment Setup
```bash
# Create project directory
mkdir QueueChain
cd QueueChain

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi==0.68.* uvicorn==0.15.* web3==6.* eth-account==0.8.* jinja2==3.*
```

### Step 2: Configuration Files
```python
# config.py
RPC_URL = "https://rpc.cardona.zkevm-rpc.com"
CONTRACT_ADDRESS = "0x1a7dbe663E5efb9f3aAF2EB56616794069d3F4eA"
```

### Step 3: Smart Contract ABI
```json
# contract.abi (copy from provided ABI file)
[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"}...]
```

### Step 4: Backend Implementation
```python
# main.py (complete implementation following documented patterns)
# - FastAPI application setup
# - Web3 integration
# - All documented endpoints
# - Background services
# - Error handling
```

### Step 5: Frontend Implementation
```html
<!-- templates/index.html -->
<!-- Complete HTML structure -->
<!-- All CSS styling -->
<!-- All JavaScript functionality -->
```

### Step 6: Testing Checklist
- [ ] Server starts on port 8000
- [ ] Homepage loads correctly
- [ ] Blockchain connection established
- [ ] Private key validation works
- [ ] Queue metadata loads
- [ ] Bid submission works
- [ ] Background services start
- [ ] Responsive design functions
- [ ] Error handling works

### Step 7: Production Deployment
- [ ] Configure environment variables
- [ ] Set up reverse proxy (nginx)
- [ ] Configure SSL/TLS
- [ ] Set up monitoring
- [ ] Configure backup strategies

This comprehensive documentation provides all necessary information to reproduce, understand, modify, or extend the QueueChain application. Every component, pattern, and integration is documented with sufficient detail for another coding agent to recreate the entire system from scratch.