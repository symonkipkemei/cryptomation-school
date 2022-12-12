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

api_key_live = os.getenv("BINANCE_TESTNET_API_KEY")
api_secret_live = os.getenv("BINANCE_TESTNET_SECRET_KEY")



if TESTNET:
    client = Client(api_key_test,api_secret_test)

    client.API_URL = "https://testnet.binance.vision/api"

else:
    client = Client(api_key_live,api_secret_live)





#DEFINING USER INPUTS
#_________________________________________________________________
#select base pair
PAIR_WITH = "USDT"


#select the total quantity required
QUNATITY = 15


# list trade pairs to exclude
FIATS = ["EURUSDT", "GBPUSDT","JPYUSDT", "USDUSDT", "DOWN", "UP"]


#time lag to calculate the time difference
TIME_DIFFERENCE = 5


#threshold in percentage change to determine which coin to buy
CHANGE_IN_PRICE = 3

# When to sell a coin that is not making profit
STOP_LOSS = 3

#when to take profit on a profitable coin
TAKE_PROFIT = 6



#LOAD BINANCE PORTFOLIO
#_________________________________________________________________

#coins bought by the bot since its start
coins_bought = {}

#path to the saved coins_bought file
coins_bought_file_path = "coins_bought.json"

#separate live from testnet files

if TESTNET:
    coins_bought_file_path= "testnet_" + coins_bought_file_path


# if saved coins_bought file already exists then load it

if os.path.isfile(coins_bought_file_path):
    with open(coins_bought_file_path) as file:
        coins_bought = json.load(file)



#GET CURRENT PRICE
#_________________________________________________________________


def get_price():
    initial_price = {}
    prices = client.get_all_tickers()

    for coin in prices:
        if PAIR_WITH in coin["symbol"] and all(item not in coin["symbol"] for item in FIATS):
            initial_price[coin["symbol"]] = {"price": coin["price"],"time":datetime.now()}

    return initial_price


price = get_price()
pprint(price)


#GET CURRENT PRICE
#_________________________________________________________________

def wait_for_price():

    volatile_coins = {}

    initial_price = get_price()

    while initial_price["BNBUSDT"]["time"] > datetime.now() - timedelta(minutes=TIME_DIFFERENCE):
        print(f"not enough time has passed yet >>>>>>>>>>")

        time.sleep(60 * TIME_DIFFERENCE)
    
    else:
        last_price = get_price()

        #calculate the difference between the first  and last price

        for coin in initial_price:
            threshold_check = (float(initial_price[coin]["price"]) - float(last_price[coin]["price"])) / float(last_price[coin]["price"]) * 100

            #volatile coins established

            if threshold_check > CHANGE_IN_PRICE:
                volatile_coins[coin] = threshold_check
                volatile_coins[coin] = round(volatile_coins[coin], 3)

                print(f"{coin} has gained {volatile_coins[coin]}% in the last {TIME_DIFFERENCE}minutes, calculating volume in {PAIR_WITH}")
                
        if len(volatile_coins) < 1:
                print(f'No coins moved more than {CHANGE_IN_PRICE}% in the last {TIME_DIFFERENCE} minute(s)')



