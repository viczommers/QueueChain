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

class PrivateKeyUpdate(BaseModel):
    private_key: str

class BidSubmission(BaseModel):
    url: str
    value: int

# Store private key in memory only
current_private_key = None
current_account = None

def get_account():
    global current_account, current_private_key
    if current_private_key and not current_account:
        try:
            current_account = Account.from_key(current_private_key)
            print(f"Created account: {current_account.address}")
        except Exception as e:
            print(f"Error creating account: {e}")
            current_account = None
    return current_account

def pop_if_ready():
    """Trigger popIfReady contract function with error handling"""
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
    """Background task that runs every 3 minutes"""
    while True:
        pop_if_ready()
        time.sleep(1800)  # 3 minutes = 180 seconds

def background_refresh_task():
    """Background task that refreshes current URL every 3.05 minutes"""
    while True:
        try:
            # Call the current-url endpoint internally
            if w3.is_connected():
                url = contract_instance.functions.getCurrentSong().call()[0]
                print(f"Background refresh - Current URL: {url}")
            else:
                print("Background refresh - Blockchain connection failed")
        except Exception as e:
            print(f"Background refresh error: {e}")
        
        time.sleep(1830)  # 3.05 minutes = 183 seconds

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Web3 setup
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Contract setup
with open('contract.abi', 'r') as f:
    abi = f.read()
contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# Start background tasks
pop_thread = threading.Thread(target=background_pop_task, daemon=True)
pop_thread.start()
print("Background popIfReady task started")

refresh_thread = threading.Thread(target=background_refresh_task, daemon=True)
refresh_thread.start()
print("Background refresh task started")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/current-url")
async def get_current_url():
    try:
        if not w3.is_connected():
            return {"error": "Blockchain connection failed"}
        
        # Get current song URL directly from contract
        url = contract_instance.functions.getCurrentSong().call()[0]
        return {"url": url if url else None}
    
    except Exception as e:
        return {"error": str(e)}

@app.get("/queue-metadata")
async def get_queue_metadata():
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
        
        if total_count > 0:
            # Get current playing metadata (index 0)
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
        
        if total_count > 1:
            # Get coming up next (index 1)
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

@app.get("/account-info")
async def get_account_info():
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

@app.post("/submit-bid")
async def submit_bid(data: BidSubmission):
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

@app.post("/update-private-key")
async def update_private_key(data: PrivateKeyUpdate):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)