
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from config import RPC_URL, CONTRACT_ADDRESS

# You can set this manually or get it from user input
PRIVATE_KEY = ""

w3 = Web3(Web3.HTTPProvider(RPC_URL))
print(w3.is_connected())

account: LocalAccount = Account.from_key(PRIVATE_KEY)
print("my address: ", account.address)
print(type(account.address))
me = account.address
w3.eth.default_account = account.address

w3.eth
print(w3.eth.get_block('latest'))

with open('contract.abi', 'r') as f:
    abi = f.read()

print("--------------------------------")
contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
# contract_instance.functions.popIfReady().transact()
# transaction = contract_instance.functions.submitData("https://youtu.be/7DXlY8LhWnI").build_transaction({
#     'from': account.address,
#     'value': 1,
#     'gas': 200000,  # Adjust gas as needed
#     'gasPrice': w3.eth.gas_price,
#     'nonce': w3.eth.get_transaction_count(account.address)
# })

# # Sign and send the transaction
# signed_txn = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
# tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# print(f"Transaction hash: {tx_hash.hex()}")

# Wait for transaction receipt
# tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
# print(f"Transaction confirmed in block {tx_receipt.blockNumber}")
print(contract_instance.functions.getSubmissionCount().call())
# print(contract_instance.functions.getCurrentSong().call()[0])
# print(contract_instance.functions.getTimeUntilNextPop().call())
# print(contract_instance.functions.getTopSubmission().call())
# print(contract_instance.functions.getSubmitterByIndex(0).call())
# print(contract_instance.functions.getTimestampByIndex(0).call())
# print(contract_instance.functions.getDataByIndex(0).call())

#use this to show total items in the queue
contract_instance.functions.getSubmissionCount().call()
#use this to display coming up next
contract_instance.functions.getSubmissionByIndex(1)[0].call()

#use this to get metadata like wallet of submitter '0x6942071d55F00FB960f4B79283d13c157Bd0e9b9' and timestam in iso 1750595560
contract_instance.functions.getSubmitterByIndex(0).call()
contract_instance.functions.getTimestampByIndex(0).call()



# Dollar = w3.eth.contract(abi=abi, bytecode=bytecode)
# # block = w3.eth.get_block('latest')
# # gas_limit = block['gasLimit']
# # print(f"Block gas limit: {gas_limit}")
# # nonce = w3.eth.get_transaction_count(w3.eth.default_account)
# # chain_id = 31337
# # print(type(w3.eth.default_account))
# # print(w3.eth.default_account)
# tx_hash = Dollar.constructor(me).build_transaction({
# 			# "chainId": chain_id,
# 			# "gasPrice": w3.eth.gas_price,
# 			"from": me,
# 			"gas": 4_700_000,
#             # 'gasPrice': w3.to_wei('20', 'gwei')
#     })
# tx_hash = Dollar.constructor("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266").transact()
# print(tx_hash)

# Wait for the transaction receipt
# tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Get the deployed contract address
# contract_address = tx_receipt.contractAddress
# print(f'Contract mined! address: {contract_address} transactionHash: {tx_receipt.transactionHash.hex()}')

# If you want to interact with the deployed contract later:
# deployed_contract = w3.eth.contract(address=contract_address, abi=abi)

# signed_txn = w3.eth.account.sign_transaction(transaction,
#     private_key=private_key)
# print("Deploying Contract…")
# tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
# print("Waiting for transaction to finish...")
# tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
# print(f"Done! Contract deployed to {tx_receipt.contractAddress}")

# try:
#     gas_estimate = Dollar.constructor(deployer).estimate_gas()
#     adjusted_gas = int(gas_estimate * 1.2)
#     print(f"Gas estimate: {gas_estimate}, adjusted: {adjusted_gas}")
# except Exception as e:
#     print(f"Gas estimation failed: {e}")
#     adjusted_gas = gas_limit - 1000000  # Use most of block gas limit

# # Deploy contract
# print(f"Deploying from {deployer} with gas: {adjusted_gas}")
# tx_hash = Dollar.constructor(deployer).transact({'gas': adjusted_gas})
# #Ownable(0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266)
# tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
# storage_address = tx_receipt.contractAddress
# print(storage_address)
# print("--------------------------------")
# print(Dollar.bytecode)

