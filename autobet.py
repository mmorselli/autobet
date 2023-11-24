#######################################################################
# autobet 0.1 Beta
# This script is provided as is, without any responsibility

import json
import random
from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction

#######################################################################
# configure this part, make a test with a small amount or in testnet

# "testnet" or "mainnet"
NETWORK = "mainnet" 

# sender mnemonic, without commas (do not use your main wallet, but instead one with a small amount)
SENDERSK = ""

# MAIN-NET Asset ID: COOP=796425061 LOTTOR=1217302022 PEPE=1096015467 SMILE=300208676 ZONE=444035862
ASSETID = 1217302022

# get these values from https://www.lottorace.cloud
# attention, if they are incorrect the bet will be invalid and the amount will be added to the jackpot
BET = 4916
ROUND = 3514646

# LOTTOR MAIN WALLET
RECEIVER_ADDRESS = "LOTTOGALTT4Y3V6VLWG3NGTVZ2CKWAT4OYPOSRH2VHJ4O2ZIKWZCVTT4HA"

#######################################################################

ALGOD_ADDRESS = f"https://{NETWORK}-api.algonode.cloud"
TOKEN = ""
SENDER_PRIVATE_KEY = mnemonic.to_private_key(SENDERSK)
SENDER_ADDRESS = account.address_from_private_key(SENDER_PRIVATE_KEY)
ALGOD_CLIENT = algod.AlgodClient(TOKEN, ALGOD_ADDRESS)

#queries the ASA to find out the number of decimal places
def AssetInfo(assetid):
    return ALGOD_CLIENT.asset_info(assetid)

# pay attention to the number of decimal places in the ASA
def ToMicro(amount,decimals):
    factor = 10 ** decimals
    return int(amount * factor)

# creates a string array of 6 uppercase hexadecimal numbers
def CreateBets():
    bets = [format(random.randint(0, 255), '02X') for _ in range(6)]
    return bets

# create a standard LOTTOR note
def CreateNote(bets):
    note = {
        "round": ROUND,
        "bets": bets
    }
    return 'LR,j'+json.dumps(note)

# send a single bet to LOTTOR
def SendSingleBet(assetid, decimals, sender, receiver, amount, note, sender_sk):
    try:
        params = ALGOD_CLIENT.suggested_params()
        txn = transaction.AssetTransferTxn(
            sender=sender,
            sp=params,
            receiver=receiver,
            amt=ToMicro(amount,decimals),
            index=assetid,
            note=note.encode()
        )

        # Sign the transaction
        signed_txn = txn.sign(sender_sk)
        # Send the transaction
        txid = ALGOD_CLIENT.send_transaction(signed_txn)

    except Exception as e:
        return "error",json.dumps(str(e))

    return txid,note

bets = CreateBets()
note = CreateNote(bets)
assetinfo = AssetInfo(ASSETID)
txid,note=SendSingleBet(ASSETID, assetinfo['params']['decimals'], SENDER_ADDRESS, RECEIVER_ADDRESS, BET, note, SENDER_PRIVATE_KEY)
if(txid=="error"):
    print("error sending transaction:",note)
else:   
    print("bet "+str(BET)+" "+assetinfo['params']['unit-name']+" with TXID "+txid+" and bets: "+','.join(bets))

