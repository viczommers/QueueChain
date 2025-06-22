# Claude Code Prompt: Generate QueueChain Decentralized Music Platform

## Project Request

Create a complete decentralized music streaming platform called **QueueChain** that allows users to submit music URLs with ETH bids to create a priority queue. The system should automatically advance the queue every 3 minutes through smart contract interactions.

## Core Requirements

### Technology Stack
- **Backend**: FastAPI (Python 3.8+) with async/await patterns
- **Blockchain**: Web3.py for Ethereum smart contract interaction on Polygon zkEVM
- **Frontend**: Single-page application with vanilla JavaScript and modern CSS
- **Design**: Spotify-inspired dark theme with glassmorphism effects
- **Security**: In-memory private key management (never persist to disk)

### Smart Contract Integration
- **Network**: Polygon zkEVM testnet (Cardona)
- **RPC URL**: `https://rpc.cardona.zkevm-rpc.com`
- **Contract Address**: `0x1a7dbe663E5efb9f3aAF2EB56616794069d3F4eA`
- **Key Functions**: `getCurrentSong()`, `submitData(string)`, `popIfReady()`, `getSubmissionCount()`, `getSubmissionByIndex(uint256)`

### File Structure Required
```
QueueChain/
├── main.py                 # FastAPI application
├── config.py              # Configuration constants
├── contract.abi           # Smart contract ABI
└── templates/
    └── index.html         # Frontend application
```

## Detailed Implementation Specifications

### 1. Configuration File (config.py)
Create a configuration file with:
```python
RPC_URL = "https://rpc.cardona.zkevm-rpc.com"
CONTRACT_ADDRESS = "0x1a7dbe663E5efb9f3aAF2EB56616794069d3F4eA"
```

### 2. Smart Contract ABI (contract.abi)
Create the ABI file with these essential functions:
- `getCurrentSong()` returns `(string data, uint256 timeRemaining)`
- `submitData(string _data)` payable function for submitting content
- `popIfReady()` function to advance queue (3-minute cooldown)
- `getSubmissionCount()` returns total items
- `getSubmissionByIndex(uint256 index)` returns submission details
- `getSubmitterByIndex(uint256 index)` returns submitter address
- `getTimestampByIndex(uint256 index)` returns submission timestamp

### 3. FastAPI Backend (main.py)

#### Required Dependencies
```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from web3 import Web3
from web3.exceptions import ContractLogicError
from eth_account import Account
import threading
import time
from config import RPC_URL, CONTRACT_ADDRESS
```

#### Data Models
Create Pydantic models:
- `BidSubmission`: url (str), value (int)
- `PrivateKeyUpdate`: private_key (str)

#### Critical Private Key Management
Implement secure private key handling:
- Global variables: `current_private_key = None`, `current_account = None`
- `get_account()` function that creates Web3 account from private key
- Store private keys ONLY in memory, never persist to disk
- Validate private key format (64 hex characters)
- Handle account creation errors gracefully

#### Required API Endpoints

**GET /** - Serve HTML template
**GET /current-url** - Return currently playing content URL from blockchain
**GET /queue-metadata** - Return comprehensive queue information including:
- Total submission count
- Current playing item (index 0)
- Coming up next (index 1)
- Recent submissions list (up to 5 items)

**POST /submit-bid** - Submit new content with ETH bid:
- Validate account exists
- Build transaction using `contract_instance.functions.submitData(url).build_transaction()`
- Include bid value, gas settings, and nonce
- Sign with private key and send raw transaction
- Wait for confirmation and return transaction hash

**POST /update-private-key** - Store private key and create account:
- Validate 64 hex character format
- Create Web3 account immediately for validation
- Return success with wallet address

**GET /account-info** - Return current wallet connection status

#### Background Services
Implement two daemon threads:

**Background Pop Task** (every 3 minutes):
- Call `popIfReady()` smart contract function
- Handle "3 minutes have not passed yet" errors gracefully
- Use proper transaction signing pattern

**Background Refresh Task** (every 3.05 minutes):
- Monitor current song for logging
- Offset timing to avoid conflicts

#### Blockchain Transaction Pattern
CRITICAL: Always use this pattern for blockchain writes:
```python
transaction = contract_instance.functions.functionName(params).build_transaction({
    'from': account.address,
    'value': wei_amount,  # if payable
    'gas': 200000,
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(account.address)
})
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=current_private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
```

### 4. Frontend Application (templates/index.html)

#### HTML Structure
Create a complete HTML page with:
- **Sidebar**: Wallet configuration, URL input, bid value input, submit/refresh buttons
- **Main Content**: Header with queue dropdown, player container for content display
- **Font Awesome icons**: Use CDN link for all icons
- **Responsive design**: Mobile-first approach

#### CSS Design System
Implement Spotify-inspired design:

**Color Palette**:
- Primary green: `#1db954` and `#1ed760`
- Dark backgrounds: Gradients from `#0c0c0c` to `#1a1a1a`
- Glass effects: `rgba(255, 255, 255, 0.05)` backgrounds
- Text hierarchy: `#ffffff`, `#b3b3b3`, `#888888`

**Layout System**:
- Flexbox app container with sidebar (300px) and main content (flex: 1)
- Glassmorphism cards with `backdrop-filter: blur(10px)`
- Rounded corners, subtle borders, and shadows

**Component Styles**:
- **Buttons**: Gradient backgrounds, hover animations with `translateY(-2px)`
- **Inputs**: Dark backgrounds with green focus states
- **Player Container**: Large flex container for embedded content
- **Queue Dropdown**: Hover-triggered dropdown with comprehensive queue info

#### JavaScript Functionality

**Core Functions**:
- `updatePrivateKey(privateKey)` - Send private key to backend
- `loadCurrentSong()` - Fetch and display current content
- `submitBid()` - Submit new content bid with validation
- `loadQueueMetadata()` - Update queue dropdown information

**Content Handling with Autoplay**:
- Convert YouTube URLs to embed format with autoplay and mute parameters
- Handle iframe loading for video content with autoplay permissions
- Show appropriate loading/error states
- Enable autoplay for seamless jukebox experience

**Auto-refresh System**:
- Initialize content loading on page load
- Set 60-second intervals for automatic updates
- Manual refresh function for user-triggered updates

**Queue Dropdown Features**:
- Hover-triggered dropdown with queue statistics
- Display current playing, coming up next, and recent submissions
- Format timestamps as relative time ("5m ago", "2h ago")
- Truncate wallet addresses to readable format

### 5. Security Requirements

#### Private Key Security
- NEVER persist private keys to disk or databases
- Store only in memory during session
- Clear on application restart
- Validate format before accepting
- Use password input type in frontend

#### Blockchain Security
- Always validate Web3 connection before operations
- Use appropriate gas limits (200,000 for transactions)
- Handle contract logic errors gracefully
- Never expose sensitive error information to users

#### Error Handling
- Wrap all blockchain calls in try-catch blocks
- Return structured JSON responses with error fields
- Log errors server-side but show user-friendly messages
- Handle network timeouts and connection failures

### 6. Specific Implementation Details

#### YouTube URL Handling with Autoplay
Convert YouTube URLs to embeddable format with autoplay enabled:
```javascript
if (url.includes('youtube.com/watch?v=')) {
    const videoId = url.split('v=')[1].split('&')[0];
    embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1`;
} else if (url.includes('youtu.be/')) {
    const videoId = url.split('youtu.be/')[1].split('?')[0];
    embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1`;
}
container.innerHTML = `<iframe src="${embedUrl}" allowfullscreen allow="autoplay; encrypted-media"></iframe>`;
```

**Important**: Videos must start muted (`mute=1`) due to browser autoplay policies. Users can unmute manually.

#### Queue Dropdown Animation
CSS hover animation:
```css
.queue-dropdown {
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s ease;
}
.queue-info:hover .queue-dropdown {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}
```

#### Responsive Design
Mobile breakpoint at 768px:
- Stack sidebar above main content
- Full-width inputs and buttons
- Adjusted dropdown positioning

### 7. Server Configuration
- Run on host `0.0.0.0`, port `8000`
- Use Uvicorn ASGI server
- Single worker for state consistency
- Daemon threads for background services

## Expected Deliverables

1. **main.py** - Complete FastAPI backend with all endpoints and background services
2. **config.py** - Configuration constants
3. **contract.abi** - Smart contract ABI definition
4. **templates/index.html** - Complete frontend application with embedded CSS and JavaScript
5. Working application that can:
   - Connect to Polygon zkEVM blockchain
   - Handle private key management securely
   - Submit content bids with ETH
   - Display current playing content
   - Show live queue information
   - Auto-advance queue every 3 minutes

## Testing Checklist

After implementation, verify:
- [ ] Server starts successfully on port 8000
- [ ] Homepage loads with proper styling
- [ ] Private key validation works (64 hex chars)
- [ ] Blockchain connection established
- [ ] Queue metadata loads from smart contract
- [ ] Bid submission creates transactions
- [ ] Background services start automatically
- [ ] YouTube URLs convert to embeds with autoplay
- [ ] Responsive design works on mobile
- [ ] Error handling prevents crashes

## Success Criteria

The application should be a fully functional decentralized music platform where:
1. Users can connect their Ethereum wallets via private key
2. Users can submit music content URLs with ETH bids
3. Content is displayed in an embedded player with autoplay
4. Queue automatically advances every 3 minutes
5. Real-time queue information is displayed
6. Modern, responsive UI provides excellent user experience
7. All blockchain interactions work correctly
8. Security best practices are followed

Generate all required files with complete implementations following these specifications exactly. The result should be a production-ready decentralized application.