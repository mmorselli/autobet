from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction
from config import NETWORK

ALGOD_ADDRESS = f"https://{NETWORK}-api.algonode.cloud"
TOKEN = ""
ALGOD_CLIENT = algod.AlgodClient(TOKEN, ALGOD_ADDRESS)