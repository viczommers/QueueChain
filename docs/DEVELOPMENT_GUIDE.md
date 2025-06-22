# QueueChain Development Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [FastAPI Backend Endpoints](#fastapi-backend-endpoints)
3. [Frontend Styling Guide](#frontend-styling-guide)
4. [Smart Contract Integration](#smart-contract-integration)
5. [Component Documentation](#component-documentation)
6. [Development Patterns](#development-patterns)

## Architecture Overview

QueueChain is a decentralized music streaming application built with:
- **Backend**: FastAPI with Web3.py for blockchain interaction
- **Frontend**: Vanilla JavaScript with modern CSS (Spotify-inspired design)
- **Blockchain**: Ethereum-compatible smart contract for queue management
- **Styling**: CSS Grid/Flexbox with glassmorphism effects

### Project Structure
```
QueueChain/
├── main.py                 # FastAPI application
├── config.py              # Configuration constants
├── contract.abi           # Smart contract ABI
├── templates/
│   └── index.html         # Frontend application
└── docs/
    └── DEVELOPMENT_GUIDE.md
```

## FastAPI Backend Endpoints

### Core Architecture Pattern

All endpoints follow this pattern:
```python
@app.get("/endpoint-name")
async def endpoint_function():
    try:
        # 1. Validate blockchain connection
        if not w3.is_connected():
            return {"error": "Blockchain connection failed"}
        
        # 2. Call smart contract functions
        result = contract_instance.functions.someFunction().call()
        
        # 3. Process and format data
        formatted_data = process_result(result)
        
        # 4. Return structured response
        return {"success": True, "data": formatted_data}
        
    except Exception as e:
        # 5. Handle errors gracefully
        print(f"Error in endpoint: {e}")
        return {"error": str(e)}
```

### Endpoint Documentation

#### 1. Root Endpoint
```python
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```
**Purpose**: Serves the main HTML application
**Returns**: HTML page
**Error Handling**: FastAPI automatic template error handling

#### 2. Current URL Endpoint
```python
@app.get("/current-url")
async def get_current_url():
```
**Purpose**: Retrieves currently playing content URL from blockchain
**Smart Contract Call**: `contract_instance.functions.getCurrentSong().call()[0]`
**Response Format**:
```json
{
  "url": "https://youtube.com/watch?v=...",  // or null
}
```
**Error Response**:
```json
{
  "error": "Blockchain connection failed"
}
```

#### 3. Queue Metadata Endpoint
```python
@app.get("/queue-metadata")
async def get_queue_metadata():
```
**Purpose**: Comprehensive queue information for UI dropdown
**Smart Contract Calls**:
- `getSubmissionCount()` - Total items in queue
- `getSubmissionByIndex(i)` - Content URL by index
- `getSubmitterByIndex(i)` - Wallet address by index  
- `getTimestampByIndex(i)` - Submission timestamp by index

**Response Format**:
```json
{
  "total_count": 5,
  "current_playing": {
    "url": "https://youtube.com/watch?v=...",
    "submitter": "0x6942071d55F00FB960f4B79283d13c157Bd0e9b9",
    "timestamp": 1750595560
  },
  "coming_up_next": {
    "url": "https://example.com/content",
    "submitter": "0xabc...",
    "timestamp": 1750595660
  },
  "recent_submissions": [
    {
      "index": 0,
      "url": "https://...",
      "submitter": "0x...",
      "timestamp": 1750595560
    }
  ]
}
```

#### 4. Account Info Endpoint
```python
@app.get("/account-info")
async def get_account_info():
```
**Purpose**: Returns current wallet connection status
**Logic**: Checks if `current_account` exists and returns address
**Response Format**:
```json
{
  "address": "0x1234...",
  "has_private_key": true
}
```

#### 5. Submit Bid Endpoint
```python
@app.post("/submit-bid")
async def submit_bid(data: BidSubmission):
```
**Purpose**: Submits new content to blockchain queue
**Input Model**:
```python
class BidSubmission(BaseModel):
    url: str
    value: int  # Wei amount
```

**Transaction Flow**:
```python
# 1. Validate account exists
account = get_account()
if not account:
    return {"error": "No account available"}

# 2. Build transaction
transaction = contract_instance.functions.submitData(data.url).build_transaction({
    'from': account.address,
    'value': data.value,
    'gas': 200000,
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(account.address)
})

# 3. Sign and send
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=current_private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# 4. Wait for confirmation
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
```

**Response Format**:
```json
{
  "success": true,
  "tx_hash": "0xabc123...",
  "block_number": 12345
}
```

#### 6. Update Private Key Endpoint
```python
@app.post("/update-private-key")
async def update_private_key(data: PrivateKeyUpdate):
```
**Purpose**: Stores private key in memory and creates Web3 account
**Validation**: Ensures private key is exactly 64 hex characters
**Security**: Private key stored only in memory, never persisted

### Background Tasks

#### 1. Pop If Ready Task
```python
def pop_if_ready():
    # Triggers contract's popIfReady() every 3 minutes
    # Handles "3 minutes have not passed yet" error gracefully
```

#### 2. Background Refresh Task
```python
def background_refresh_task():
    # Calls getCurrentSong() every 3.05 minutes
    # Logs current URL for monitoring
```

## Frontend Styling Guide

### Design System

#### Color Palette
```css
:root {
  /* Primary Colors */
  --spotify-green: #1db954;
  --spotify-green-light: #1ed760;
  
  /* Background Gradients */
  --bg-primary: linear-gradient(135deg, #0c0c0c 0%, #121212 25%, #1a1a1a 50%, #0d1117 100%);
  --bg-sidebar: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%);
  
  /* Glass Effects */
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);
  
  /* Text Colors */
  --text-primary: #ffffff;
  --text-secondary: #b3b3b3;
  --text-muted: #888;
}
```

#### Typography
```css
/* Headings use gradient text */
.gradient-text {
  background: linear-gradient(45deg, #1db954, #1ed760);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Body text hierarchy */
.text-primary { color: #ffffff; }
.text-secondary { color: #b3b3b3; }
.text-muted { color: #888; }
```

### Layout System

#### Container Structure
```css
.app-container {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 300px;
  background: var(--bg-sidebar);
}

.main-content {
  flex: 1;
  padding: 2rem;
}
```

#### Responsive Breakpoints
```css
@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    padding: 1rem;
  }
}
```

### Component Styling Patterns

#### Glassmorphism Cards
```css
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

#### Button System
```css
/* Primary Action Button */
.btn-primary {
  background: linear-gradient(45deg, #1db954, #1ed760);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(29, 185, 84, 0.3);
}

/* Secondary Button */
.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```

#### Form Controls
```css
.input-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  transition: all 0.3s ease;
}

.input-group input:focus {
  outline: none;
  border-color: #1db954;
  box-shadow: 0 0 0 2px rgba(29, 185, 84, 0.2);
}
```

### Queue Dropdown Component

#### Structure
```html
<div class="queue-info">
  <div class="queue-badge">
    <i class="fas fa-list"></i>
    <span id="queueCount">0</span> in queue
  </div>
  
  <div class="queue-dropdown">
    <!-- Dropdown content -->
  </div>
</div>
```

#### Hover Animation
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

#### Dropdown Sections
```css
.dropdown-section {
  margin-bottom: 1.5rem;
}

.dropdown-title {
  color: #1db954;
  font-weight: 600;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.queue-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

## Smart Contract Integration

### Web3 Connection Pattern
```python
# Initialize Web3 connection
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Load contract
with open('contract.abi', 'r') as f:
    abi = f.read()
contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
```

### Transaction Pattern
```python
# Always use build_transaction + sign + send_raw_transaction
# Never use .transact() as it requires eth_sendTransaction

transaction = contract_instance.functions.functionName(params).build_transaction({
    'from': account.address,
    'value': wei_amount,  # if payable
    'gas': 200000,
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(account.address)
})

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
```

### Error Handling
```python
try:
    # Contract call
    result = contract_instance.functions.someFunction().call()
except ContractLogicError as e:
    if "specific error message" in str(e):
        # Handle specific contract errors
        print("Specific error occurred")
    else:
        print(f"Contract logic error: {e}")
except Exception as e:
    print(f"General error: {e}")
```

## Component Documentation

### Queue Metadata Component

#### JavaScript Functions

**loadQueueMetadata()**
- Fetches `/queue-metadata` endpoint
- Updates all dropdown sections
- Handles empty states gracefully

**extractContentTitle(url)**
- Extracts readable titles from URLs
- Special handling for YouTube URLs
- Fallback to domain name or truncated URL

**formatTimestamp(timestamp)**
- Converts Unix timestamp to relative time
- Returns "2h ago", "3d ago", etc.
- Handles edge cases and invalid timestamps

#### Data Flow
```
1. User hovers over queue badge
2. CSS animation shows dropdown
3. JavaScript periodically calls loadQueueMetadata()
4. Backend fetches data from smart contract
5. Frontend updates dropdown content
6. User sees live queue information
```

## Development Patterns

### Error Handling Strategy
1. **Backend**: Always return JSON with error field
2. **Frontend**: Check for error field in responses
3. **User Feedback**: Show alerts for critical errors
4. **Logging**: Console.log for debugging, print() for backend

### State Management
- **Private Key**: Stored in memory only (`current_private_key`)
- **Account**: Created on-demand from private key
- **UI State**: DOM manipulation, no frontend framework

### Performance Considerations
- **Auto-refresh**: 60-second intervals for UI updates
- **Background tasks**: Separate threads for blockchain operations
- **Caching**: No caching implemented (real-time blockchain data)

### Security Practices
- Private keys never persisted to disk
- Input validation on all form fields
- Error messages don't expose sensitive information
- HTTPS recommended for production

## Reproducibility Checklist

To recreate this application:

1. **Environment Setup**
   - Python 3.8+ with FastAPI, Web3.py, eth-account
   - Smart contract deployed with ABI file
   - RPC endpoint configured in config.py

2. **Backend Implementation**
   - Follow endpoint patterns documented above
   - Implement background tasks for auto-refresh
   - Use transaction pattern for all blockchain writes

3. **Frontend Styling**
   - Use CSS custom properties for theming
   - Implement glassmorphism with backdrop-filter
   - Follow component structure for dropdowns

4. **Integration Testing**
   - Test all endpoints with valid/invalid data
   - Verify blockchain transaction flow
   - Test responsive design on mobile

This guide provides the complete blueprint for recreating or extending the QueueChain application while maintaining design consistency and code quality.