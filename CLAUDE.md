# QueueChain - Claude Context for Project Replication

## Project Overview

QueueChain is a decentralized music streaming platform built with FastAPI and Web3.py that allows users to submit music URLs with ETH bids to create a priority queue. The system automatically advances the queue every 3 minutes through smart contract interactions on Polygon zkEVM.

## Core Architecture

### Technology Stack
- **Backend**: FastAPI (Python 3.8+) with async/await
- **Blockchain**: Web3.py for Ethereum smart contract interaction
- **Frontend**: Vanilla JavaScript with modern CSS3
- **Network**: Polygon zkEVM testnet (Cardona)
- **Design**: Glassmorphism UI with disco-inspired elements, electric blue accents, and shimmer animations

### Project Structure
```
QueueChain/
├── main.py                 # FastAPI application entry point
├── config.py              # RPC URL and contract address constants
├── contract.abi           # Smart contract ABI definition
├── templates/
│   └── index.html         # Single-page application frontend
├── static/
│   └── style.css          # External CSS with glassmorphism design, disco elements, and shimmer effects
└── docs/
    └── CLAUDE_CONTEXT.md  # This file
```

## Configuration Files

### config.py
```python
RPC_URL = "https://rpc.cardona.zkevm-rpc.com"
CONTRACT_ADDRESS = "0x1a7dbe663E5efb9f3aAF2EB56616794069d3F4eA"
```

### contract.abi
The smart contract ABI defines these key functions:
- `getCurrentSong()` - Returns current playing content
- `getSubmissionCount()` - Returns total queue items
- `getSubmissionByIndex(uint256)` - Returns submission data by index
- `submitData(string)` - Submits new content (payable)
- `popIfReady()` - Advances queue (3-minute cooldown)

## FastAPI Backend Implementation

### Core Dependencies
```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from web3 import Web3
from web3.exceptions import ContractLogicError
from eth_account import Account
import asyncio
import threading
import time
from config import RPC_URL, CONTRACT_ADDRESS
```

### Application Setup
```python
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Global state variables for private key management
current_private_key = None
current_account = None

# Web3 connection
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Contract instance
with open('contract.abi', 'r') as f:
    abi = f.read()
contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
```

### Data Models
```python
class BidSubmission(BaseModel):
    url: str        # Content URL
    value: int      # Bid amount in Wei

class PrivateKeyUpdate(BaseModel):
    private_key: str    # Ethereum private key (64 hex chars)
```

### Private Key Management System

**CRITICAL SECURITY PATTERN**: Private keys are stored only in memory, never persisted to disk.

```python
def get_account():
    """
    Creates or retrieves Web3 account from stored private key.
    
    Security Features:
    - Private key stored only in memory (never persisted)
    - Account recreated on-demand
    - Error handling prevents app crashes
    - Global state management for session persistence
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

@app.post("/update-private-key")
async def update_private_key(data: PrivateKeyUpdate):
    """
    Stores private key in memory and creates Web3 account.
    
    Validation:
    - Removes '0x' prefix if present
    - Ensures exactly 64 hexadecimal characters
    - Tests account creation before storing
    
    Security:
    - Private key stored only in memory (global variable)
    - Account reset on new key entry
    - Immediate validation prevents invalid keys
    """
    try:
        global current_private_key, current_account
        current_private_key = data.private_key.strip()
        current_account = None  # Reset account to force recreation
        
        # Validate private key format
        clean_key = current_private_key.replace('0x', '')
        if len(clean_key) != 64:
            return {"error": f"Private key must be 64 hex characters, got {len(clean_key)} characters"}
        
        # Test account creation immediately
        current_account = Account.from_key(current_private_key)
        print(f"Account created successfully: {current_account.address}")
        return {"success": True, "address": current_account.address}
            
    except Exception as e:
        print(f"Error with private key: {e}")
        return {"error": f"Invalid private key: {str(e)}"}
```

## Essential API Endpoints

### 1. Serve Frontend
```python
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```

### 2. Get Current Playing Content
```python
@app.get("/current-url")
async def get_current_url():
    try:
        if not w3.is_connected():
            return {"error": "Blockchain connection failed"}
        
        url = contract_instance.functions.getCurrentSong().call()[0]
        return {"url": url if url else None}
    
    except Exception as e:
        return {"error": str(e)}
```

### 3. Submit Content Bid
```python
@app.post("/submit-bid")
async def submit_bid(data: BidSubmission):
    """
    Critical blockchain transaction pattern for all write operations.
    
    Transaction Flow:
    1. Validate account exists
    2. Build transaction with contract function
    3. Sign transaction with private key
    4. Send raw transaction to network
    5. Wait for confirmation
    """
    try:
        account = get_account()
        if not account:
            return {"error": "No account available - please enter private key first"}
        
        # Build transaction (NEVER use .transact() - use build_transaction)
        transaction = contract_instance.functions.submitData(data.url).build_transaction({
            'from': account.address,
            'value': data.value,        # Wei amount for payable function
            'gas': 200000,              # Fixed gas limit
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address)
        })
        
        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=current_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for confirmation
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": True,
            "tx_hash": tx_hash.hex(),
            "block_number": tx_receipt.blockNumber
        }
        
    except Exception as e:
        return {"error": str(e)}
```

### 4. Queue Metadata
```python
@app.get("/queue-metadata")
async def get_queue_metadata():
    try:
        if not w3.is_connected():
            return {"error": "Blockchain connection failed"}
        
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
                print(f"Error getting current playing: {e}")
        
        # Get recent submissions (up to 5)
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
                print(f"Error getting submission {i}: {e}")
        
        return queue_data
    
    except Exception as e:
        return {"error": str(e)}
```

## Background Services

### Queue Auto-Advancement
```python
def pop_if_ready():
    """
    Triggers smart contract popIfReady with proper error handling.
    Contract only allows calling every 3 minutes.
    Includes queue empty check for efficiency.
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
    except Exception as e:
        print(f"Error calling popIfReady: {e}")

def background_pop_task():
    """Background thread that runs popIfReady every 3 minutes"""
    while True:
        pop_if_ready()
        time.sleep(180)  # 3 minutes

# Start background service
pop_thread = threading.Thread(target=background_pop_task, daemon=True)
pop_thread.start()
```

### Server Startup
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Frontend Implementation (templates/index.html)

### Real-time Update Architecture

The frontend implements a sophisticated real-time update system that automatically refreshes the iframe when new content arrives:

#### Update Detection System
- **Polling Mechanism**: Checks `/current-url` endpoint every 5 seconds
- **Change Detection**: Compares current URL with stored `currentPlayingUrl`
- **Smart Updates**: Only refreshes iframe when content actually changes
- **Dual Refresh**: Updates both player content and queue metadata simultaneously

#### Update Flow
1. `checkForUpdates()` polls backend every 5 seconds
2. Detects URL changes by comparing with cached value
3. Calls `loadCurrentSong()` to refresh iframe with new content
4. Simultaneously updates queue metadata via `loadQueueMetadata()`
5. Background service advances queue every 3 minutes via smart contract

#### Performance Optimization
- **Lightweight Polling**: Content check every 5 seconds (minimal payload)
- **Metadata Refresh**: Queue data every 30 seconds (heavier payload)
- **Change-Based Updates**: Only reloads iframe when URL actually changes
- **Error Handling**: Graceful degradation on network/API failures

### HTML Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Encode Play - Decentralized Music Player</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        /* CSS implementation goes here */
    </style>
</head>
<body>
    <div class="app-container">
        <div class="sidebar">
            <div class="logo">
                <!-- <i class="fas fa-music"></i> -->
                <div class="logo-container">
                    <img src="/static/logo.png" alt="Logo" class="logo-image">
                </div>
                <h1>Encode Play</h1>
            </div>
            
            <div class="wallet-section">
                <div class="wallet-title">
                    <i class="fas fa-wallet"></i>
                    Wallet Configuration
                </div>
                
                <div class="input-group">
                    <label for="privateKey">Private Key</label>
                    <input type="password" id="privateKey" placeholder="Enter your private key">
                </div>
                
                <div class="input-group">
                    <label for="bidUrl">Content URL (max 42 chars)</label>
                    <input type="text" id="bidUrl" placeholder="https://youtube.com/watch?v=...">
                </div>
                
                <div class="input-group">
                    <label for="bidValue">Bid Value (Wei)</label>
                    <input type="number" id="bidValue" placeholder="1000000000000000000">
                </div>
                
                <div class="button-group">
                    <button class="btn btn-primary" onclick="submitBid()">Submit Bid</button>
                    <button class="btn btn-secondary" onclick="updateConfigAndRefresh()">Refresh</button>
                </div>
                
                <div id="addressDisplay" class="account-display" style="display: none;"></div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="header">
                <h2>Now Playing</h2>
                <p>Decentralized music streaming powered by Polygon zkEVM Smart Contract</p>
                
                <div class="queue-info" id="queueInfo">
                    <div class="queue-badge">
                        <i class="fas fa-list"></i>
                        <span id="queueCount">0</span> in queue
                    </div>
                    
                    <div class="queue-dropdown" id="queueDropdown">
                        <!-- Queue dropdown content -->
                    </div>
                </div>
                
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
                <div class="loading">
                    <i class="fas fa-spinner"></i>
                    <div>Loading current content...</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        /* JavaScript implementation goes here */
    </script>
</body>
</html>
```

## Critical CSS Design System

### CSS Custom Properties Foundation
```css
:root {
    /* Electric blue color palette */
    --disco-blue: #00bfff;
    --disco-blue-light: #1e90ff;
    
    /* Dark theme backgrounds */
    --bg-primary: linear-gradient(135deg, #0c0c0c 0%, #121212 25%, #1a1a1a 50%, #0d1117 100%);
    --bg-sidebar: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%);
    
    /* Glassmorphism effects */
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    
    /* Text hierarchy */
    --text-primary: #ffffff;
    --text-secondary: #b3b3b3;
    --text-muted: #888;
}

/* Global reset and foundation */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
    overflow-x: hidden;
}

/* Main layout system */
.app-container {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 300px;
    background: var(--bg-sidebar);
    border-right: 1px solid #333;
    padding: 2rem;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.3);
}

.main-content {
    flex: 1;
    padding: 2rem;
    display: flex;
    flex-direction: column;
}
```

### Essential Component Styles
```css
/* Glassmorphism cards */
.wallet-section {
    background: var(--glass-bg);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(10px);
}

/* Form controls */
.input-group input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--glass-border);
    border-radius: 8px;
    background: var(--glass-bg);
    color: #fff;
    transition: all 0.3s ease;
}

.input-group input:focus {
    outline: none;
    border-color: var(--disco-blue);
    box-shadow: 0 0 0 2px rgba(0, 191, 255, 0.2);
}

/* Button system */
.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 25px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.btn-primary {
    background: linear-gradient(45deg, #2a7a4b, #3a8a5b);
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(42, 122, 75, 0.3);
}

.btn-primary::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), rgba(78, 205, 196, 0.1), rgba(69, 183, 209, 0.1), transparent);
    animation: shimmer 4s infinite;
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

@keyframes rainbow-text {
    0%, 100% { 
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 25%, #45b7d1 50%, #00bfff 75%, #6a5acd 100%);
        -webkit-background-clip: text;
        background-clip: text;
    }
    50% { 
        background: linear-gradient(135deg, #6a5acd 0%, #00bfff 25%, #45b7d1 50%, #4ecdc4 75%, #ff6b6b 100%);
        -webkit-background-clip: text;
        background-clip: text;
    }
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(42, 122, 75, 0.4);
}

/* Player container */
.player-container {
    flex: 1;
    background: var(--glass-bg);
    border-radius: 16px;
    padding: 2rem;
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(20px);
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
}

.player-container iframe {
    width: 100%;
    height: 100%;
    border: none;
    border-radius: 12px;
    min-height: 400px;
}

/* Queue and Help Dropdown System */
.queue-badge {
    background: linear-gradient(45deg, #6b4c93, #4682b4);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(107, 76, 147, 0.3);
}

.help-badge {
    background: linear-gradient(45deg, #cd5c5c, #d2691e);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(205, 92, 92, 0.3);
}

.queue-badge::before,
.help-badge::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), rgba(155, 89, 182, 0.1), rgba(69, 183, 209, 0.1), transparent);
    animation: shimmer 4s infinite;
}

.queue-dropdown, .help-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 0.5rem;
    width: 350px;
    background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(15, 15, 15, 0.95) 100%);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(20px);
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s ease;
    z-index: 1000;
}

.queue-info:hover .queue-dropdown,
.help-info:hover .help-dropdown {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

/* Mobile responsive dropdowns */
@media (max-width: 768px) {
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
}
```

## Essential JavaScript Functions

### Private Key Management
```javascript
async function updatePrivateKey(privateKey) {
    if (!privateKey) return;
    
    try {
        const response = await fetch('/update-private-key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ private_key: privateKey })
        });
        
        const result = await response.json();
        if (result.error) {
            alert('Error: ' + result.error);
        } else if (result.address) {
            const addressDisplay = document.getElementById('addressDisplay');
            addressDisplay.style.display = 'block';
            addressDisplay.innerHTML = `Connected: ${result.address.slice(0, 6)}...${result.address.slice(-4)}`;
        }
    } catch (error) {
        alert('Error updating private key: ' + error.message);
    }
}
```

### Content Loading with Auto-Update
```javascript
async function loadCurrentSong() {
    /**
     * Loads and displays current content in iframe player.
     * 
     * Features:
     * - Automatically converts YouTube URLs to embed format with autoplay
     * - Updates iframe src to trigger content refresh
     * - Handles error states gracefully
     * - Called by real-time update system when content changes
     */
    try {
        const response = await fetch('/current-url');
        const data = await response.json();
        const container = document.getElementById('player-container');
        
        if (data.error) {
            container.innerHTML = `<div class="status-message error"><i class="fas fa-exclamation-triangle"></i><br>Error: ${data.error}</div>`;
            return;
        }
        
        if (data.url) {
            // Convert YouTube URLs to embed format with autoplay
            let embedUrl = data.url;
            if (data.url.includes('youtube.com/watch?v=')) {
                const videoId = data.url.split('v=')[1].split('&')[0];
                embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1`;
            } else if (data.url.includes('youtu.be/')) {
                const videoId = data.url.split('youtu.be/')[1].split('?')[0];
                embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1`;
            }
            
            // Update iframe - this triggers automatic content refresh
            container.innerHTML = `<iframe src="${embedUrl}" allowfullscreen allow="autoplay; encrypted-media"></iframe>`;
        } else {
            container.innerHTML = `<div class="status-message no-content"><i class="fas fa-music"></i><br>No content currently playing</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="status-message error"><i class="fas fa-wifi"></i><br>Error loading content: ${error.message}</div>`;
    }
}
```

### Bid Submission
```javascript
async function submitBid() {
    const privateKey = document.getElementById('privateKey').value;
    const bidUrl = document.getElementById('bidUrl').value;
    const bidValue = document.getElementById('bidValue').value;
    
    if (!privateKey || !bidUrl || !bidValue) {
        alert('Please fill all fields');
        return;
    }
    
    try {
        await updatePrivateKey(privateKey);
        
        const response = await fetch('/submit-bid', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                url: bidUrl, 
                value: parseInt(bidValue) 
            })
        });
        
        const result = await response.json();
        if (result.error) {
            alert('Error: ' + result.error);
        } else {
            alert(`Success! TX: ${result.tx_hash}`);
            document.getElementById('bidUrl').value = '';
            document.getElementById('bidValue').value = '';
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}
```

### Real-time Update System
```javascript
// Store current URL to detect changes
let currentPlayingUrl = null;

async function checkForUpdates() {
    try {
        const response = await fetch('/current-url');
        const data = await response.json();
        
        // Check if URL has changed
        if (data.url !== currentPlayingUrl) {
            console.log('Content changed, refreshing player');
            currentPlayingUrl = data.url;
            
            // Refresh the player with new content
            loadCurrentSong();
            
            // Also refresh queue metadata when content changes
            loadQueueMetadata();
        }
    } catch (error) {
        console.error('Error checking for updates:', error);
    }
}

// Initialize on page load
loadCurrentSong();
loadQueueMetadata();

// Real-time content change detection every 5 seconds
setInterval(checkForUpdates, 5000);

// Refresh queue metadata every 30 seconds
setInterval(loadQueueMetadata, 30000);
```

## Security Considerations

### Private Key Handling
- **NEVER persist private keys to disk**
- Store only in memory during session
- Clear on application restart
- Validate format before storage
- Use secure input types in frontend

### Blockchain Security
- Always use `build_transaction()` pattern
- Never use `.transact()` method
- Validate all user inputs
- Handle contract errors gracefully
- Use appropriate gas limits

### Error Handling
```python
# Always wrap blockchain calls
try:
    result = contract_instance.functions.someFunction().call()
except ContractLogicError as e:
    # Handle expected contract errors
    if "specific error" in str(e):
        # Handle gracefully
        pass
except Exception as e:
    # Handle unexpected errors
    return {"error": str(e)}
```

## Deployment Instructions

### Development Setup
```bash
# Create project directory
mkdir QueueChain && cd QueueChain

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn web3 eth-account jinja2

# Create files
touch main.py config.py contract.abi
mkdir templates && touch templates/index.html

# Run server
python main.py
```

### Required Files Checklist
- [ ] `main.py` - Complete FastAPI backend
- [ ] `config.py` - RPC URL and contract address
- [ ] `contract.abi` - Smart contract ABI
- [ ] `templates/index.html` - Complete frontend
- [ ] Background services running
- [ ] Private key validation working
- [ ] Blockchain connection established

## Testing Patterns

### Backend Testing
```python
# Test private key validation
test_keys = [
    "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",  # Valid
    "invalid_key",  # Invalid
    ""  # Empty
]

# Test blockchain connection
assert w3.is_connected()

# Test contract instance
assert contract_instance.address == CONTRACT_ADDRESS
```

### Frontend Testing
- Private key input validation
- Form submission handling
- Auto-refresh functionality
- YouTube URL conversion
- Responsive design

## Common Issues & Solutions

### Blockchain Connection
- **Issue**: RPC connection fails
- **Solution**: Verify RPC URL and network connectivity

### Private Key Errors
- **Issue**: Invalid private key format
- **Solution**: Ensure 64 hex characters, handle 0x prefix

### Transaction Failures
- **Issue**: Transaction reverts
- **Solution**: Check gas limits, contract state, account balance

### Frontend Loading
- **Issue**: Content not displaying
- **Solution**: Check API endpoints, CORS settings, error handling

### Real-time Updates
- **Issue**: Iframe not updating with new content
- **Solution**: Check `checkForUpdates()` polling, verify `/current-url` endpoint
- **Issue**: Updates too slow/fast
- **Solution**: Adjust polling intervals (5s for content, 30s for metadata)
- **Issue**: Excessive API calls
- **Solution**: Ensure change detection logic only updates when URL differs

This context provides all essential patterns, security considerations, and implementation details needed to replicate the QueueChain project. Focus on the private key management system as it's critical for blockchain interactions and user security.