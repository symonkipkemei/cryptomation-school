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



#DEFINING USER INPUTS
#_________________________________________________________________
#select base pair
PAIR_WITH = "USDT"


#select the total quantity required
QUANTITY = 15


# list trade pairs to exclude
FIATS = ["EURUSDT", "GBPUSDT","JPYUSDT", "USDUSDT", "DOWN", "UP"]


#time lag to calculate the time difference in minutes
TIME_DIFFERENCE = 1


#threshold in percentage change to determine which coin to buy
CHANGE_IN_PRICE = 0.3

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

        # there are no coins recorded in our volatility dictionary
        if len(volatile_coins) < 1:
                print(f'No coins moved more than {CHANGE_IN_PRICE}% in the last {TIME_DIFFERENCE} minute(s)')

        return volatile_coins, len(volatile_coins), last_price

def convert_volume():
    volatile_coins,no_coins, last_price = wait_for_price()
    lots_size = {}
    volume = {}

    for coin in volatile_coins:
        try:
            lots_size = {}
            info = client.get_symbol_info(coin)
            step_size = info['filters'][1]['stepSize']
            lots_size[coin] = step_size.index("1")-1

            if lots_size[coin]< 0:
                lots_size[coin] = 0
        except:
            pass

        volume[coin] = float(QUANTITY / float(last_price[coin]['price']))

        if coin not in lots_size:
            volume[coin] = float('{:.1f}'.format(volume[coin]))

        else:
            if lots_size[coin] == 0:
                #remove the decimal point if lot size is o
                volume[coin] = round(volume[coin],lots_size[coin])
                volume[coin] = int(volume[coin])
            else:
                #round to the lots size decimal points
                volume[coin] = round(volume[coin],lots_size[coin])
    return volume, last_price

    
def trade():
    volume, last_price = volume()
    orders = {}
    for coin in volume:

        #only buy if there are no active trades on the coin
        if coin not in coins_bought or coins_bought[coin] == None:
            print(f"preparing to buy {volume[coin], {coin}}")

            if TESTNET:
                test_order = client.create_test_order(symbol=coin,
                side="BUY",
                type="MARKET",
                quantity=volume[coin]
                )

                # try to create a real order if the test orders did not raise an exception
                try:
                    buy_limit = client.create_order(
                        symbol=coin,
                        side='BUY',
                        type='MARKET',
                        quantity=volume[coin]
                    )

                # error handling here in case position cannot be placed
                except Exception as e:
                    print(e)
            
                # run the else block if the position has been placed and return order info
            else:
                orders[coin] = client.get_all_orders(symbol=coin, limit=1)
        else:
             print(f'Signal detected, but there is already an active trade on {coin}')



            
    

if __name__ == "__main__":
    convert_volume()

 

        
