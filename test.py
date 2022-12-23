import os

from binance.client import Client

from datetime import datetime,timedelta
import time
from pprint import pprint

#repeatedly execute code
from itertools import count


#used to store trades and sell assets
import json




#CONFIGURING BINANCE CLIENT
#________________________________________________________________


TESTNET = False


# Get keys 

api_key_test = os.getenv("BINANCE_TESTNET_API_KEY")
api_secret_test = os.getenv("BINANCE_TESTNET_SECRET_KEY")

api_key_live = os.getenv("binance_api_key")
api_secret_live = os.getenv("binance_api_key_secret")



if TESTNET:
    client = Client(api_key_test,api_secret_test)

    client.API_URL = "https://testnet.binance.vision/api"

else:
    client = Client(api_key_live,api_secret_live)


orders = client.get_all_orders(symbol="DATAUSDT",limit=1)
pprint(orders)