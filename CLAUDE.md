# QueueChain - Claude Context for Static Implementation

## Project Overview

QueueChain is a decentralized music streaming platform built as a single static HTML file that directly interacts with smart contracts on Polygon zkEVM. Users submit music URLs with ETH bids to create a priority queue that automatically advances every 3 minutes through client-side blockchain interactions.

## Core Architecture

### Technology Stack
- **Frontend**: Single static HTML file with embedded CSS and JavaScript
- **Blockchain**: Web3.js for direct Ethereum smart contract interaction
- **Network**: Polygon zkEVM testnet (Cardona)
- **Design**: Glassmorphism UI with disco-inspired elements, electric blue accents, and shimmer animations
- **Deployment**: Static hosting (GitHub Pages, Netlify, Vercel, etc.)

### Project Structure
```
QueueChain/
├── index.html              # Complete static application (all-in-one file)
├── static/
│   └── logo.png            # Logo image (optional)
└── docs/
    └── CLAUDE.md           # This file
```

## Smart Contract Configuration

The application connects directly to the smart contract at:
- **RPC URL**: `https://rpc.cardona.zkevm-rpc.com`
- **Contract Address**: `0x1a7dbe663E5efb9f3aAF2EB56616794069d3F4eA`

### Smart Contract ABI Functions
- `getCurrentSong()` - Returns current playing content
- `getSubmissionCount()` - Returns total queue items
- `getSubmissionByIndex(uint256)` - Returns submission data by index
- `getSubmitterByIndex(uint256)` - Returns submitter address by index
- `getTimestampByIndex(uint256)` - Returns timestamp by index
- `submitData(string)` - Submits new content (payable)
- `popIfReady()` - Advances queue (3-minute cooldown)

## Static HTML Implementation

### Complete Single-File Architecture

The entire application is contained in a single `index.html` file with:
- **Embedded CSS**: Complete glassmorphism design system
- **Embedded JavaScript**: Full Web3 blockchain interaction
- **Self-contained**: No external dependencies except CDN libraries

### HTML Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Encode Play - Decentralized Music Player</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/web3@1.10.0/dist/web3.min.js"></script>
    <style>
        /* Complete CSS embedded here */
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Complete UI structure -->
    </div>
    <script>
        /* Complete JavaScript functionality */
    </script>
</body>
</html>
```

## Client-Side Blockchain Integration

### Web3.js Direct Connection
```javascript
// Blockchain configuration
const RPC_URL = "https://rpc.cardona.zkevm-rpc.com";
const CONTRACT_ADDRESS = "0x1a7dbe663E5efb9f3aAF2EB56616794069d3F4eA";
const CONTRACT_ABI = [/* Full ABI array */];

// Initialize Web3
let web3;
let contract;
let currentAccount = null;
let currentPlayingUrl = null;

// Initialize blockchain connection
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

### Private Key Management
**CRITICAL SECURITY PATTERN**: Private keys are stored only in browser memory, never persisted.

```javascript
// Validate and set private key
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

## Core Functions

### Load Current Content
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

### Submit Blockchain Bid
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

### Queue Metadata Loading
```javascript
async function loadQueueMetadata() {
    try {
        if (!contract) {
            throw new Error('Blockchain not initialized');
        }

        const totalCount = await contract.methods.getSubmissionCount().call();
        
        // Update queue count badge
        document.getElementById('queueCount').textContent = totalCount;
        document.getElementById('totalCount').textContent = totalCount;
        document.getElementById('activeItems').textContent = totalCount;
        
        // Get current playing info
        if (totalCount > 0) {
            try {
                const submission = await contract.methods.getSubmissionByIndex(0).call();
                const submitter = await contract.methods.getSubmitterByIndex(0).call();
                const timestamp = await contract.methods.getTimestampByIndex(0).call();
                
                document.getElementById('currentSection').style.display = 'block';
                extractContentTitle(submission[0], document.getElementById('currentTitle'));
                document.getElementById('currentSubmitter').textContent = `${submitter.slice(0, 6)}...${submitter.slice(-4)}`;
                document.getElementById('currentTime').textContent = formatTimestamp(timestamp);
            } catch (error) {
                console.error('Error getting current playing:', error);
                document.getElementById('currentSection').style.display = 'none';
            }
        } else {
            document.getElementById('currentSection').style.display = 'none';
        }
        
        // Get next up and recent submissions
        // ... (similar pattern for next and recent items)
        
    } catch (error) {
        console.error('Error loading queue metadata:', error);
    }
}
```

### YouTube Title Extraction
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

## Real-time Update System

### Automatic Content Detection
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

### Background Queue Advancement
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

## CSS Design System

### Glassmorphism Foundation
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

/* Loading spinner animation */
.loading i {
    font-size: 3rem;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Shimmer effects */
@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}
```

## Security Considerations

### Client-Side Security
- **Private keys stored only in browser memory**
- **Never persisted to localStorage or disk**
- **Cleared on page refresh/close**
- **Validated before use**
- **No server-side storage**

### Blockchain Security
- **Direct smart contract interaction**
- **Proper transaction building patterns**
- **Gas limit management**
- **Error handling for contract calls**
- **Input validation**

## Deployment Instructions

### Static Hosting Setup
```bash
# Create project directory
mkdir QueueChain && cd QueueChain

# Create the single HTML file
touch index.html

# Optional: Add logo
mkdir static && cp logo.png static/

# Deploy to any static host:
# - GitHub Pages: Push to gh-pages branch
# - Netlify: Drag and drop folder
# - Vercel: Connect repository
# - Surge: surge ./
# - Any web server: Upload index.html
```

### Required Files Checklist
- [ ] `index.html` - Complete static application
- [ ] `static/logo.png` - Logo image (optional)
- [ ] Smart contract ABI embedded in JavaScript
- [ ] Web3.js CDN connection working
- [ ] FontAwesome CDN connection working

## Testing Patterns

### Client-Side Testing
```javascript
// Test blockchain connection
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

### Manual Testing
- Private key input validation
- Form submission handling
- Auto-refresh functionality
- YouTube URL conversion and title fetching
- Responsive design on mobile
- Queue advancement timing
- Error handling scenarios

## Common Issues & Solutions

### Blockchain Connection
- **Issue**: RPC connection fails
- **Solution**: Check network connectivity, try different RPC endpoints

### Private Key Errors
- **Issue**: Invalid private key format
- **Solution**: Ensure 64 hex characters, remove 0x prefix

### Transaction Failures
- **Issue**: Transaction reverts
- **Solution**: Check gas limits, account balance, contract state

### Static Hosting Issues
- **Issue**: CORS errors with external APIs
- **Solution**: Some hosts handle CORS better than others, try different providers

### YouTube Title Fetching
- **Issue**: YouTube oEmbed API fails
- **Solution**: Graceful fallback to "YouTube Video" default

This implementation provides a complete, secure, client-side decentralized application that can be deployed anywhere static files are served. The single-file architecture makes it extremely portable and easy to deploy.