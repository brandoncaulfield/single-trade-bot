import os
import json
from kraken import *
from datetime import date, datetime, timedelta
import logging
# import pandas as pd
import uuid


def is_coin_above_50_day_sma(coin, interval=1440):
    # ohlc_data = get_ohlc_data(coin, interval)
    # df = pd.DataFrame.from_dict(ohlc_data['result'])
    # df['sma50'] = 
    return True

def is_coin_above_100_day_sma(coin):
    return True

def is_coin_above_200_day_sma(coin):
    return True


def get_order_log():

    with open('order_log.json', 'r') as file:
        order_log = json.load(file)
    
    return order_log


def doesFileExists(filePathAndName):
    return os.path.exists(filePathAndName)


def get_current_price(coin):
    current_price = get_kraken_price(coin)
    return current_price["result"][coin]["c"][0]


def get_previouse_price(coin):
    with open('previous_price.json', 'r') as file:
        try:
            previous_price = json.load(file)
        except:
            previous_price = {}
    if len(previous_price) < 1:
        current_price = get_current_price(coin)
        if len(current_price["error"]) == 0:
            with open('previous_price.json', 'w') as file:
                previous_price[coin] = float(current_price)
                if len(previous_price) > 0:
                    json.dump(previous_price, file)
                    return previous_price
                # else:
                #     previous_price = {}
                #     json.dump(previous_price, file)

    else:
        return previous_price


def do_we_own_the_coin(coin):

    if not doesFileExists('./portfolio.json'):
        with open('portfolio.json', 'w') as file:
            json.dump({}, file)

    with open('portfolio.json', 'r') as file:
        portfolio = json.load(file)
    if coin in portfolio:
        return portfolio
    else:
        return False


def get_asset_balance(asset):
    
    account_data = get_account_balance()

    try:
        asset_amount = account_data['result'][asset]
        return asset_amount
    except:
        print(f'Could not find {asset} in account balance')
        logging.error(f'Could not find {asset} in account balance')
        return 0


def place_order(coin, order_type, volume):

    order_resp = add_kraken_order(coin, order_type, volume)
    if len(order_resp["error"]) == 0:
        return order_resp
    else:
        raise Exception(order_resp) 

def get_portfolio_data(coin):
    
    with open('portfolio.json', 'r') as file:
        portfolio_data = json.load(file)
    
    # return portfolio_data[coin]
    return portfolio_data
    


def add_coin_to_portfolio(coin, portfolio_data):

    if not doesFileExists('./portfolio.json'):
        with open('portfolio.json', 'w') as file:
            json.dump({}, file)
    
    with open('portfolio.json', 'r') as file:
        current_portfolio_data = json.load(file)
    
    # Add the new data to the current portfolio data
    current_portfolio_data[coin] = portfolio_data[coin]

    # Update the portfolio
    with open('portfolio.json', 'w') as file:
        try:
            json.dump(current_portfolio_data, file)
            print(f'{coin} added to portfolio at {str(datetime.now())} length:{len(current_portfolio_data)}')
            logging.info(f'{coin} added to portfolio at {str(datetime.now())} length:{len(current_portfolio_data)}')
        except:
            # If anything happens try protect the integrity of the json file
            json.dump({}, file)
            print(f'There was an issue adding {coin} to the portfolio :(')
            logging.error(f'There was an issue adding {coin} to the portfolio :(')

    # return coin + " added to portfolio"


def remove_coin_from_portfolio(coin):

    with open('portfolio.json', 'r') as file:
        portfolio_data = json.load(file)

    with open('portfolio.json', 'w') as file:
        try:
            del portfolio_data[coin]

            if len(portfolio_data) > 0:
                json.dump(portfolio_data, file)
                print(f'{coin} removed from portfolio at {str(datetime.now())} length:{len(portfolio_data)}')
                logging.info(f'{coin} removed from portfolio at {str(datetime.now())} length:{len(portfolio_data)}')
            else:
                json.dump({}, file)
        except:
            print(f"Issue while deleting {coin} from portfolio")
            logging.error(f"Issue while deleting {coin} from portfolio")


def determine_volume_to_buy(current_price, value_to_spend, currency, safe_percentage=False):

    account_balance = get_account_balance()

    # Handle scenario where we have less than the user specified parameter in 
    # our account, still make the purchase with whatever we have.
    # safe_percentage is there in case the price 
    # changes and the order fails due to insufficient funds
    if account_balance != 0:
        if float(account_balance['result'][currency]) <= float(value_to_spend):
            volume_to_buy = float(account_balance['result'][currency]) / float(current_price)

            if safe_percentage:
                reduced_volume_to_buy = (float(volume_to_buy) / 100) * float(safe_percentage)
                return reduced_volume_to_buy
            else:
                return volume_to_buy

        else:
            volume_to_buy = float(account_balance['result'][currency]) / float(current_price)

            if safe_percentage:
                reduced_volume_to_buy = (float(account_balance['result'][currency]) / value_to_spend) * float(safe_percentage)
                return reduced_volume_to_buy
            else:
                return volume_to_buy 


def determine_volume_to_sell(coin):

    with open('portfolio.json', 'r') as file:
        portfolio_data = json.load(file)
    
    return portfolio_data[coin]["vol"]



def determine_take_profit(current_price, take_profit):

    return float(current_price) + (float(current_price) / 100 * float(take_profit))


def determine_stop_loss(current_price, stop_loss):

    return float(current_price) - (float(current_price) / 100 * float(stop_loss))


def update_order_log(order):

    if not doesFileExists('./order_log.json'):
        with open('order_log.json', 'w') as file:
            json.dump({}, file)

    # We have to open it first before adding the data
    with open('order_log.json', 'r') as file:
        order_log = json.load(file)

    # We have ot open it again to write the data
    with open('order_log.json', 'w') as file:
        try:
            # Generate random log ID
            log_id = uuid.uuid1()
            order_log[int(log_id)] = order
            if len(order_log) > 0:
                json.dump(order_log, file)
            print("New entry added to Order Log!")
            logging.info(f"New entry {log_id} added to Order Log!")
        except:
            print("Something happened while tryin to update the trading log :(")
            logging.error("Something happened while tryin to update the trading log :( - id: {log_id}")
            json.dump(order_log, file)


def update_previous_price(coin, current_price):

    if not doesFileExists('./previous_price.json'):
        with open('previous_price.json', 'w') as file:
            json.dump({}, file)

    #  Get the old price
    previous_price = get_previouse_price(coin)

    with open('previous_price.json', 'w') as file:
        try:
            # Update the old price with the current price 
            previous_price[coin] = current_price
            print(f'updated previous price to: {previous_price} at {str(datetime.now())}')
            logging.info(f'updated previous price to: {previous_price} at {str(datetime.now())}')
            json.dump(previous_price, file)
        except:
            previous_price = {}
            json.dump(previous_price, file)
            logging.error(f'Issue updating previous price to current price: {current_price}')


if __name__ == "__main__":
    is_coin_above_50_day_sma("XXBTZUSD")