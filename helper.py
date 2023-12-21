import time
import json
import random
import requests
from datetime import datetime, timezone, timedelta
from algosdk import transaction, account, mnemonic
from algod import ALGOD_CLIENT
from config import SENDERSK, NETWORK
from algod import ALGOD_CLIENT


STARTINGPOINT = 3382166  # round at 2023-10-10T00:00:00Z
RECEIVER_ADDRESS = "LOTTOGALTT4Y3V6VLWG3NGTVZ2CKWAT4OYPOSRH2VHJ4O2ZIKWZCVTT4HA" if NETWORK == "mainnet" else "LOTTOG6RMXNE5L5JMW6BNQZTT3EGLUDQN3T5YPJ6MLYBG4S4UJ3DVNHZ2E"

def isBetween23and24UTC():
    now = datetime.now(timezone.utc)
    start = datetime.combine(now.date(), datetime.min.time(), timezone.utc) + timedelta(hours=23)
    end = datetime.combine(now.date(), datetime.min.time(), timezone.utc) + timedelta(hours=24)

    if end < start:
        return now >= start or now <= end
    else:
        return start <= now <= end


def getNextRoundAtDate(currentDateTs):
    startDate = datetime(2023, 10, 10, 0, 0, 0)
    diffInSecs = currentDateTs - startDate.timestamp()
    diffInDays = -(-diffInSecs // (24 * 60 * 60))  # Calcola il ceil
    nextIncrement = diffInDays * 2880
    return int(STARTINGPOINT + nextIncrement)  


def getNetxRound():
    currentDateTs = int(datetime.now().timestamp())
    result = getNextRoundAtDate(currentDateTs)
    return result


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

#queries the ASA to find out the number of decimal places
def AssetInfo(assetid):
    return ALGOD_CLIENT.asset_info(assetid)

# pay attention to the number of decimal places in the ASA
def ToMicro(amount,decimals):
    factor = 10 ** decimals
    return int(amount * factor)

# DEPRECATED: creates a string array of 6 uppercase hexadecimal numbers
def CreateBetsOld():
    bets = [format(random.randint(0, 255), '02X') for _ in range(6)]
    return bets

# creates a string array of NOT DUPLICATED 6 uppercase hexadecimal numbers
def CreateBets():
    bets = random.sample(range(256), 6)
    bets = [format(bet, '02X') for bet in bets]
    return bets

# create a standard LOTTOR note
def CreateNote(nextround,bets):
    note = {
        "round": nextround,
        "bets": bets
    }
    return 'LR,j'+json.dumps(note)

def get_reference_prices():
    baseurl = "api" if NETWORK == "mainnet" else "apitestnet"
    response = requests.get('https://'+baseurl+'.lottorace.cloud/enabledreferenceprices')
    data = response.json()
    return data

def get_parameters(assetid, data):
    element = "assetid" if NETWORK == "mainnet" else "testassetid"
    for item in data:
        if item[element] == assetid:
            return item
    return None


def user_select_coin(data):
    for index, item in enumerate(data, start=1):
        print(f"{index}. {item['name']}")
    
    print("\n0. exit")
    
    choice = int(input("\nplese select coin: "))
    if 1 <= choice <= len(data):
        if(NETWORK == "mainnet"):
            return data[choice - 1]['assetid']
        else:
            return data[choice - 1]['testassetid']
    else:
        return 0
    
def user_confirm():
    user_input = input("It's all ok? (y/n): ")
    return user_input.lower() == 'y'

def check_pk(sk):
    words = sk.split()
    return len(words) == 25

def getsuffix(number):
    suffix = 's' if number >1 else ''
    return suffix

def multi_bet(assetid,amount,nextround,iteration):

    if isBetween23and24UTC():
        print("\nIt's not time to bet yet (" + datetime.now(timezone.utc).strftime('%H:%M') + " UTC)")
        return

    SENDER_PRIVATE_KEY = mnemonic.to_private_key(SENDERSK)
    SENDER_ADDRESS = account.address_from_private_key(SENDER_PRIVATE_KEY)
    assetinfo = AssetInfo(assetid)
    start_time = time.time()

    for i in range(iteration):
        bets = CreateBets()
        note = CreateNote(nextround,bets)
        txid,note=SendSingleBet(assetid, assetinfo['params']['decimals'], SENDER_ADDRESS, RECEIVER_ADDRESS, amount, note, SENDER_PRIVATE_KEY)
        if(txid=="error"):
            print("error sending transaction:",note)
        else:   
            print(f"{i+1} bet "+str(amount)+" "+assetinfo['params']['unit-name']+" with TXID "+txid+" and bets: "+','.join(bets))
        time.sleep(1)

    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes = round(elapsed_time // 60)
    seconds = round(elapsed_time % 60)
    suffix = getsuffix(iteration)
    print(f"\n{iteration} transaction{suffix} sent in {minutes} minutes and {seconds} seconds")  

def DoMultiBet():

    if not check_pk(SENDERSK):
        print("\nedit config.py first")
        return
    
    print("SELECT COIN\n")

    reference = get_reference_prices()
    selectcoint = user_select_coin(reference)
    if(selectcoint == 0):
        return

    parameters = get_parameters(selectcoint,reference)
    nextround = getNetxRound()

    print("\nPlease, carefully check these parameters\n")
    print("network:",NETWORK)
    print("coin:",parameters['name'])
    print("assetid:",selectcoint)
    print("nextround:",nextround) 
    print("bet amount",parameters['amount']) 
    print("\n")

    uc = user_confirm()
    if not uc:
        print("\nbye")
        return

    iteration = int(input("\nHow many bets do you want to send?: "))

    suffix = getsuffix(iteration)
    print(f"\nyou're about to send {iteration} bet{suffix}\n")

    uc = user_confirm()
    if not uc:
        print("\nbye")
        return

    print("\n")

    multi_bet(selectcoint,parameters['amount'],nextround,iteration)