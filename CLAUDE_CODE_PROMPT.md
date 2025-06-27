# Claude Code Prompt: Generate QueueChain Static Decentralized Music Platform

## Project Request

Create a complete decentralized music streaming platform called **QueueChain** as a single static HTML file that directly interacts with smart contracts on Polygon zkEVM. Users submit music URLs with ETH bids to create a priority queue that automatically advances every 3 minutes through client-side blockchain interactions.

## Core Requirements

### Technology Stack
- **Architecture**: Single static HTML file with embedded CSS and JavaScript
- **Blockchain**: Web3.js for direct Ethereum smart contract interaction
- **Network**: Polygon zkEVM testnet (Cardona)
- **Design**: Glassmorphism dark theme with disco-inspired elements, electric blue accents, and shimmer animations
- **Security**: Browser memory-only private key management (never persist)
- **Deployment**: Static hosting (GitHub Pages, Netlify, Vercel, etc.)

### Smart Contract Integration
- **Network**: Polygon zkEVM testnet (Cardona)
- **RPC URL**: `https://rpc.cardona.zkevm-rpc.com`
- **Contract Address**: `0x1a7dbe663E5efb9f3aAF2EB56616794069d3F4eA`
- **Key Functions**: `getCurrentSong()`, `submitData(string)`, `popIfReady()`, `getSubmissionCount()`, `getSubmissionByIndex(uint256)`, `getSubmitterByIndex(uint256)`, `getTimestampByIndex(uint256)`

### File Structure Required
```
QueueChain/
├── index.html              # Complete static application (all-in-one file)
├── static/
│   └── logo.png            # Logo image (optional)
└── docs/
    └── README.md           # Documentation
```

## Detailed Implementation Specifications

### 1. Complete Static HTML Application (index.html)

Create a single HTML file containing:
- **Complete CSS styling** embedded in `<style>` tags
- **Complete JavaScript functionality** embedded in `<script>` tags
- **External dependencies** via CDN links only
- **Self-contained** with no server requirements

#### Required CDN Dependencies
```html
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/web3@1.10.0/dist/web3.min.js"></script>
```

#### HTML Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Encode Play - Decentralized Music Player</title>
    <!-- CDN links -->
    <style>
        /* Complete embedded CSS */
    </style>
</head>
<body>
    <div class="app-container">
        <div class="sidebar">
            <!-- Wallet configuration, inputs, buttons -->
        </div>
        <div class="main-content">
            <!-- Header, queue info, help info, player container -->
        </div>
    </div>
    <script>
        /* Complete embedded JavaScript */
    </script>
</body>
</html>
```

### 2. Client-Side Blockchain Integration

#### Web3.js Configuration
```javascript
// Blockchain configuration constants
const RPC_URL = "https://rpc.cardona.zkevm-rpc.com";
const CONTRACT_ADDRESS = "0x1a7dbe663E5efb9f3aAF2EB56616794069d3F4eA";
const CONTRACT_ABI = [
    // Complete ABI array with all required functions
    {"inputs":[],"name":"getCurrentSong","outputs":[{"internalType":"string","name":"data","type":"string"},{"internalType":"uint256","name":"timeRemaining","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"getSubmissionCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"index","type":"uint256"}],"name":"getSubmissionByIndex","outputs":[{"internalType":"string","name":"data","type":"string"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"address","name":"submitter","type":"address"},{"internalType":"uint256","name":"timestamp","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"index","type":"uint256"}],"name":"getSubmitterByIndex","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"index","type":"uint256"}],"name":"getTimestampByIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"string","name":"_data","type":"string"}],"name":"submitData","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[],"name":"popIfReady","outputs":[],"stateMutability":"nonpayable","type":"function"}
];

// Global variables
let web3;
let contract;
let currentAccount = null;
let currentPlayingUrl = null;
```

#### Blockchain Initialization
```javascript
function initBlockchain() {
    try {
        web3 = new Web3(RPC_URL);
        contract = new web3.eth.Contract(CONTRACT_ABI, CONTRACT_ADDRESS);
        console.log('Blockchain connection initialized');
        return true;
    } catch (error) {
        console.error('Error initializing blockchain:', error);
        return false;
    }
}
```

### 3. Critical Private Key Management

**SECURITY REQUIREMENT**: Private keys stored only in browser memory, never persisted.

```javascript
function setPrivateKey(privateKey) {
    try {
        const cleanKey = privateKey.replace('0x', '');
        if (cleanKey.length !== 64) {
            throw new Error(`Private key must be 64 hex characters, got ${cleanKey.length} characters`);
        }
        
        currentAccount = web3.eth.accounts.privateKeyToAccount('0x' + cleanKey);
        console.log('Account created:', currentAccount.address);
        
        const addressDisplay = document.getElementById('addressDisplay');
        addressDisplay.style.display = 'block';
        addressDisplay.innerHTML = `<i class="fas fa-check-circle"></i> Connected: ${currentAccount.address.slice(0, 6)}...${currentAccount.address.slice(-4)}`;
        
        return true;
    } catch (error) {
        console.error('Error setting private key:', error);
        alert('Error: ' + error.message);
        return false;
    }
}
```

### 4. Core JavaScript Functions

#### Load Current Content
```javascript
async function loadCurrentSong() {
    try {
        if (!contract) {
            throw new Error('Blockchain not initialized');
        }

        const result = await contract.methods.getCurrentSong().call();
        const url = result[0];
        
        const container = document.getElementById('player-container');
        
        if (url && url !== '') {
            let embedUrl = url;
            if (url.includes('youtube.com/watch?v=')) {
                const videoId = url.split('v=')[1].split('&')[0];
                embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=0`;
            } else if (url.includes('youtu.be/')) {
                const videoId = url.split('youtu.be/')[1].split('?')[0];
                embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=0`;
            }
            container.innerHTML = `<iframe src="${embedUrl}" allowfullscreen allow="autoplay; encrypted-media"></iframe>`;
        } else {
            container.innerHTML = `<div class="status-message no-content"><i class="fas fa-music"></i><br>No content currently playing</div>`;
        }
    } catch (error) {
        console.error('Error loading current song:', error);
        document.getElementById('player-container').innerHTML = 
            `<div class="status-message error"><i class="fas fa-wifi"></i><br>Error loading content: ${error.message}</div>`;
    }
}
```

#### Submit Blockchain Bid
```javascript
async function submitBid() {
    const privateKey = document.getElementById('privateKey').value;
    const bidUrl = document.getElementById('bidUrl').value;
    const bidValue = document.getElementById('bidValue').value;
    
    if (!privateKey || !bidUrl || !bidValue || bidValue <= 0) {
        alert('Please fill all fields with valid values');
        return;
    }
    
    try {
        // Set private key first
        if (!setPrivateKey(privateKey)) {
            return;
        }
        
        if (!contract) {
            throw new Error('Blockchain not initialized');
        }
        
        // Build transaction
        const gasPrice = await web3.eth.getGasPrice();
        const nonce = await web3.eth.getTransactionCount(currentAccount.address);
        
        const transaction = {
            from: currentAccount.address,
            to: CONTRACT_ADDRESS,
            value: bidValue,
            gas: 200000,
            gasPrice: gasPrice,
            nonce: nonce,
            data: contract.methods.submitData(bidUrl).encodeABI()
        };
        
        // Sign and send transaction
        const signedTx = await web3.eth.accounts.signTransaction(transaction, currentAccount.privateKey);
        const receipt = await web3.eth.sendSignedTransaction(signedTx.rawTransaction);
        
        alert(`Bid submitted successfully!\\nTransaction: ${receipt.transactionHash}\\nBlock: ${receipt.blockNumber}`);
        
        // Clear form
        document.getElementById('bidUrl').value = '';
        document.getElementById('bidValue').value = '';
        
        // Refresh content
        setTimeout(() => {
            loadCurrentSong();
            loadQueueMetadata();
        }, 2000);
        
    } catch (error) {
        console.error('Error submitting bid:', error);
        alert('Error submitting bid: ' + error.message);
    }
}
```

#### YouTube Title Extraction
```javascript
function extractContentTitle(url, element) {
    if (!url) return 'Unknown Content';
    
    // Extract title from YouTube URLs
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
        // Set default immediately
        if (element) element.textContent = 'YouTube Video';
        
        // Fetch real title in background
        setTimeout(async () => {
            try {
                const response = await fetch(`https://www.youtube.com/oembed?url=${encodeURIComponent(url)}&format=json`);
                const data = await response.json();
                if (element) element.textContent = data.title || 'YouTube Video';
            } catch (error) {
                console.error('Error fetching YouTube title:', error);
                if (element) element.textContent = 'YouTube Video';
            }
        }, 0);
        
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
```

### 5. Real-time Update System

#### Auto-update Implementation
```javascript
// Store current URL to detect changes
let currentPlayingUrl = null;

async function checkForUpdates() {
    try {
        if (!contract) return;
        
        const result = await contract.methods.getCurrentSong().call();
        const url = result[0];
        
        if (url !== currentPlayingUrl) {
            console.log('Content changed, refreshing player');
            currentPlayingUrl = url;
            loadCurrentSong();
            loadQueueMetadata();
        }
    } catch (error) {
        console.error('Error checking for updates:', error);
    }
}

// Initialize everything when page loads
window.addEventListener('load', function() {
    if (initBlockchain()) {
        loadCurrentSong();
        loadQueueMetadata();
        
        // Check for content changes every 5 seconds
        setInterval(checkForUpdates, 5000);
        
        // Refresh queue metadata every 30 seconds
        setInterval(loadQueueMetadata, 30000);
        
        // Try to advance queue every 3 minutes (if account is set)
        setInterval(popIfReady, 180000);
    } else {
        document.getElementById('player-container').innerHTML = 
            `<div class="status-message error"><i class="fas fa-exclamation-triangle"></i><br>Failed to initialize blockchain connection</div>`;
    }
});
```

#### Background Queue Advancement
```javascript
async function popIfReady() {
    try {
        if (!currentAccount || !contract) {
            console.log('No account available for popIfReady');
            return;
        }
        
        // Check if queue is empty
        const submissionCount = await contract.methods.getSubmissionCount().call();
        if (submissionCount == 0) {
            console.log('Queue is empty - skipping popIfReady');
            return;
        }
        
        const gasPrice = await web3.eth.getGasPrice();
        const nonce = await web3.eth.getTransactionCount(currentAccount.address);
        
        const transaction = {
            from: currentAccount.address,
            to: CONTRACT_ADDRESS,
            gas: 200000,
            gasPrice: gasPrice,
            nonce: nonce,
            data: contract.methods.popIfReady().encodeABI()
        };
        
        const signedTx = await web3.eth.accounts.signTransaction(transaction, currentAccount.privateKey);
        const receipt = await web3.eth.sendSignedTransaction(signedTx.rawTransaction);
        console.log('popIfReady transaction sent:', receipt.transactionHash);
        
    } catch (error) {
        if (error.message.includes('3 minutes have not passed yet')) {
            console.log('popIfReady called too early - 3 minutes have not passed yet');
        } else {
            console.log('Error calling popIfReady:', error.message);
        }
    }
}
```

### 6. Embedded CSS Design System

#### Glassmorphism Foundation
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
```

#### Loading Animation
```css
.loading i {
    font-size: 3rem;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
```

#### Shimmer Effects
```css
@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
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
```

### 7. UI Components Required

#### Sidebar Structure
```html
<div class="sidebar">
    <div class="logo">
        <div class="logo-container">
            <img src="static/logo.png" alt="Logo" class="logo-image">
        </div>
        <h1>Encode Play</h1>
    </div>
    
    <div class="wallet-section">
        <div class="wallet-title">
            <i class="fas fa-wallet"></i>
            Wallet Configuration
        </div>
        
        <div class="input-group">
            <label for="privateKey">
                <i class="fas fa-key"></i> Private Key
            </label>
            <input type="password" id="privateKey" placeholder="Enter your private key">
        </div>

        <div class="input-group">
            <label for="bidUrl">
                <i class="fas fa-link"></i> Content URL (max 42 chars)
            </label>
            <input type="text" id="bidUrl" placeholder="https://youtu.be/content">
        </div>

        <div class="input-group">
            <label for="bidValue">
                <i class="fas fa-coins"></i> Bid Value (Wei)
            </label>
            <input type="number" id="bidValue" placeholder="1000000000000000000" min="0">
        </div>

        <div class="button-group">
            <button class="btn btn-primary" onclick="submitBid()">
                <i class="fas fa-play"></i>
                Submit Bid
            </button>
            <button class="btn btn-secondary" onclick="refreshContent()">
                <i class="fas fa-sync"></i>
                Refresh
            </button>
        </div>
        
        <div class="button-group" style="margin-top: 1rem;">
            <button class="btn btn-secondary" onclick="testConnection()">
                <i class="fas fa-heart-pulse"></i>
                Test Connection
            </button>
        </div>

        <div id="addressDisplay" class="account-display" style="display: none;"></div>
    </div>
</div>
```

#### Main Content Structure
```html
<div class="main-content">
    <div class="header">
        <h2>Now Playing</h2>
        <p>Decentralized music streaming powered by <a href="https://cardona-zkevm.polygonscan.com/address/0x1a7dbe663e5efb9f3aaf2eb56616794069d3f4ea" target="_blank" class="header-link">Polygon zkEVM Smart Contract</a></p>
        
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
                <!-- Help dropdown content -->
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
```

### 8. Mobile Responsive Design

#### Mobile Breakpoint (768px)
```css
@media (max-width: 768px) {
    .app-container {
        flex-direction: column;
    }

    .sidebar {
        width: 100%;
        padding: 1rem;
    }

    .main-content {
        padding: 1rem;
    }

    .button-group {
        flex-direction: column;
    }

    .btn {
        width: 100%;
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
}
```

### 9. Security Requirements

#### Client-Side Security
- **Private keys stored only in browser memory**
- **Never persisted to localStorage or disk**
- **Cleared on page refresh/close**
- **Validated before use (64 hex characters)**
- **No server-side storage or transmission**

#### Blockchain Security
- **Direct smart contract interaction only**
- **Proper transaction building patterns**
- **Gas limit management (200,000 for transactions)**
- **Error handling for contract calls**
- **Input validation before blockchain operations**

### 10. Testing and Connection Functions

#### Connection Testing
```javascript
async function testConnection() {
    try {
        const isConnected = await web3.eth.net.isListening();
        const blockNumber = await web3.eth.getBlockNumber();
        
        alert(`Connection Test:\\n\\nBlockchain: ${isConnected ? 'Connected' : 'Disconnected'}\\nLatest Block: ${blockNumber}\\nContract: ${CONTRACT_ADDRESS}`);
        
        // Also test contract calls
        loadCurrentSong();
        loadQueueMetadata();
        
    } catch (error) {
        console.error('Connection test failed:', error);
        alert(`Connection test failed: ${error.message}`);
    }
}
```

## Expected Deliverables

1. **index.html** - Complete static application containing:
   - Embedded CSS with glassmorphism design system
   - Embedded JavaScript with full Web3 functionality
   - Complete UI with sidebar, main content, dropdowns
   - Real-time updates and auto-refresh
   - Mobile responsive design
   - YouTube title extraction
   - Loading animations and error handling

2. **static/logo.png** - Optional logo image

3. Working application that can:
   - Connect directly to Polygon zkEVM blockchain
   - Handle private key management securely in browser memory
   - Submit content bids with ETH via Web3.js
   - Display current playing content with autoplay
   - Show live queue information with real YouTube titles
   - Auto-advance queue every 3 minutes
   - Work on any static hosting platform

## Testing Checklist

After implementation, verify:
- [ ] Single HTML file opens in browser without server
- [ ] Styling loads correctly with glassmorphism design
- [ ] Private key validation works (64 hex chars)
- [ ] Blockchain connection established via Web3.js
- [ ] Queue metadata loads from smart contract
- [ ] Bid submission creates transactions successfully
- [ ] Auto-update intervals work (5s content, 30s metadata, 3m queue advance)
- [ ] YouTube URLs convert to embeds with autoplay (unmuted)
- [ ] YouTube titles fetch and display correctly
- [ ] Responsive design works on mobile devices
- [ ] Error handling prevents crashes
- [ ] Loading spinner animates correctly
- [ ] All dropdowns work on hover
- [ ] Test connection button works

## Success Criteria

The application should be a fully functional static decentralized application where:
1. Users can connect Ethereum wallets via private key (browser memory only)
2. Users can submit music content URLs with ETH bids directly to blockchain
3. Content displays in embedded player with autoplay functionality
4. Queue automatically advances every 3 minutes via client-side calls
5. Real-time queue information displays with YouTube title fetching
6. Modern, responsive UI provides excellent user experience
7. All blockchain interactions work correctly via Web3.js
8. Security best practices followed (no private key persistence)
9. Can be deployed to any static hosting platform
10. Works entirely client-side with no backend dependencies

Generate the complete static HTML file with all functionality embedded. The result should be a production-ready decentralized application that can be hosted anywhere static files are served.