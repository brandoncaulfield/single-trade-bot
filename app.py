import logging
from helper import *
import os
from websocket import create_connection
import re
from datetime import datetime

####################################################
#                   USER INPUTS                    #
#                                                  #
####################################################
# Is it a test Scenario
test_mode = True

# Coin = asset pair to trade (must include currency e.g. XXBTZUSD)
coin = 'XETHZGBP'

# Price to buy at at start of run
# price_to_buy = 2200

# Take Profit (TP) percentage
take_profit = 6

# Stop Loss (SL) percentage
stop_loss = 3

# The USD value to spend on each asset
value_to_spend = 2000

# The currency to be used for all trades
trading_currency = 'ZGBP'

# In case of price fluctuations use this safe percentage to ensure order is made
safe_percentage = 99

# Switch for trailing SL and TP
trailing_sl_and_tp = False

# Below fields allow you to configure where you might want to sell
# E.g. the setup below will make sure your coin is bought at 
# "buying price" and will sell if price drops below purchase price
#  and buy again if price goes over purchase price.
# 
# hold_the_floor = True
# take_the_profit = False
# stop_the_loss = False
# 
# Be careful with the floor setting as you might find your coin keeps 
# this value and you could rack up a large amount of transaction fees

# his_watch_has_ended = False

# Buy
# Watch
# Sell
# Watch
# Repeat ->


####################################################
#                END OF USER INPUTS                #
#                  Edit with care                  #
####################################################


def run():

    ''' Logging '''
    logging.basicConfig(filename='app.log', level=logging.INFO)

    config = get_config()

    if config['test_mode']:
        print('*** test mode ***')
        logging.info('*** test mode ***')

    print('Hey Ho! Lest Go!')
    logging.info('Hey Ho! Lest Go!')

    print(f'Started at: {datetime.now()}')
    logging.info(f'Started at: {datetime.now()}')


    while True:

        # Check the price
        current_price = get_current_price(coin)


        print(f'Current price: {current_price}')
        logging.info(f'Current price: {current_price}')


        if not do_we_own_the_coin(coin):

            # If price_to_buy is not configured (i.e. 0) at the start set it at the current price
            if config['price_to_buy'] == 0: 
                config['price_to_buy'] = current_price
            
            # Has the price hit our limit to buy
            if float(config['price_to_buy']) <= float(current_price):

                if config['test_mode']:

                    portfolio_data = {}  
                    trade_id = 1234
                    portfolio_data[coin] = {}
                    portfolio_data[coin]["bought_at"] = float(current_price)
                    portfolio_data[coin]["take_profit"] = determine_take_profit(float(current_price), take_profit)
                    portfolio_data[coin]["stop_loss"] = determine_stop_loss(float(current_price), stop_loss)
                    portfolio_data[coin]["vol"] = float(0.02342424)

                    # Add coin to portfolio
                    add_coin_to_portfolio(coin, portfolio_data)

                    update_order_log(portfolio_data)

                    print('Test order complete')
                    logging.info('Test order complete')

                else:
                    
                    volume_to_buy = determine_volume_to_buy(current_price, value_to_spend, trading_currency, safe_percentage)
                    print(f'Volume to buy: {volume_to_buy}')
                    logging.info(f'Volume to buy: {volume_to_buy}')
                    
                    try:
                        # Buy the coin
                        order_resp = place_order(coin, "buy", volume_to_buy)

                        if len(order_resp["error"]) == 0:

                            # Wait for order to propogate
                            time.sleep(10)

                            order_info = get_order_info(order_resp["result"]["txid"][0])

                            trade_data = get_trade_details(order_info['result'][order_resp["result"]["txid"][0]]["trades"][0])

                            update_order_log(trade_data)

                            portfolio_data = {}  
                            trade_id = order_info['result'][order_resp["result"]["txid"][0]]["trades"][0]
                            portfolio_data[coin] = {}
                            portfolio_data[coin]["bought_at"] = float(trade_data['result'][trade_id]["price"])
                            portfolio_data[coin]["take_profit"] = determine_take_profit(float(trade_data['result'][trade_id]["price"]), take_profit)
                            portfolio_data[coin]["stop_loss"] = determine_stop_loss(float(trade_data['result'][trade_id]["price"]), stop_loss)
                            portfolio_data[coin]["vol"] = float(trade_data['result'][trade_id]["vol"])
                            portfolio_data[coin]["test"] = True

                            # Add coin to portfolio
                            add_coin_to_portfolio(coin, portfolio_data)

                            print(f'We just made a *** REAL *** order: {trade_data}')
                            logging.info(f'We just made a REAL order: {trade_data}')

                            print(f'{coin} added to portfolio')
                            logging.info(f'{coin} added to portfolio')

                    except: 
                        # print(f'{order_resp}')
                        # logging.info(f'{order_resp}')
                        print(f'Order failed')
                        logging.info(f'Order failed')

            
        else:

            # Always make sure we have the portfolio data we need for the loop below 
            try:
                if not "portfolio_data" in locals():
                    portfolio_data = get_portfolio_data(coin)
            except:
                print("There is an issue with the portfolio data and we can't continue safely")
                logging.info("There is an issue with the portfolio data and we can't continue safely")

                break


        ''' Connect to Websocket publisher server here'''
        # Then in the While loop send messages as they come based on the Kraken websocket
        '''end'''


        # Connect to WebSocket API and subscribe to trade feed for XBT/USD and XRP/USD
        ws = create_connection("wss://ws.kraken.com/")

        #  ws.send('{"event":"subscribe", "subscription":{"name":"ownTrades", "token": "%s"}}' % token)

        ws.send('{"event":"subscribe", "subscription":{"name":"ohlc"}, "pair":["ETH/GBP"]}')


        #  From here we just keep checking when we need to sell
        while True:

            ohlc = ws.recv()

            data = re.sub(r'[^\w:,/.]', '', ohlc)

            data_array = data.split(",")

            # print(data_array)

            if 'ETH/GBP' in data_array:

                live_price = data_array[7]
                print(f'Close price: {live_price} {trading_currency} at {datetime.now()}')
                logging.info(f'Close price: {live_price} {trading_currency} at {datetime.now()}')
                
                
                # Check if moved below SMA 50 and 200 line


                # check TP
                if float(live_price) > float(portfolio_data[coin]['take_profit']):
                    if test_mode:
                        remove_coin_from_portfolio(coin)

                        order_log_data = {}
                        order_log_data[coin] = {"order_reason":"Take Profit", "price": float(live_price)}

                        update_order_log(order_log_data)

                        print(f'TP hit at price: {live_price}')
                        logging.info(f'TP hit at price: {live_price}')

                        # if his_watch_has_ended:
                        break

                    else:

                        print(f'TP hit at price: {live_price}')
                        logging.info(f'TP hit at price: {live_price}')

                        order_resp_sl = place_order(coin, 'sell', portfolio_data[coin]['vol'])

                        if len(order_resp_sl["error"]) == 0:
                            # Wait for order to propogate
                            time.sleep(10)

                            order_info = get_order_info(order_resp_sl["result"]["txid"][0])

                            trade_data = get_trade_details(order_info['result'][order_resp_sl["result"]["txid"][0]]["trades"][0])

                            trade_data['portfolio_data'] = portfolio_data

                            trade_data['order_reason'] = 'Take Profit'

                        update_order_log(trade_data)

                        print(f'TP logged successfully')
                        logging.info(f'TP logged successfully')

                        remove_coin_from_portfolio(coin)

                        print(f'{coin} removed from portfolio')
                        logging.info(f'{coin} removed from portfolio')

                        # if his_watch_has_ended:
                        break
                
                # Wha to do if we want a floor price set
                if config['hold_the_floor']:
                    
                    if float(live_price) < float(portfolio_data[coin]['bought_at']):

                        if test_mode:
                            remove_coin_from_portfolio(coin)

                            order_log_data = {}
                            order_log_data[coin] = {"order_reason":"Floor price hit", "price": float(live_price)}

                            update_order_log(order_log_data)

                            print(f'Floor price hit at price: {live_price}')
                            logging.info(f'Floor price hit at price: {live_price}')

                            # Adjust the "price to buy" in case the price has dropped lower than 
                            # the price we purchased at to try and recoup losses on the next run.
                            config['price_to_buy'] = live_price

                            # if his_watch_has_ended:
                            break
                        
                        else:

                            print(f'Floor price hit at price: {live_price}')
                            logging.info(f'Floor price hit at price: {live_price}')

                            order_resp_floor = place_order(coin, 'sell', portfolio_data[coin]['vol'])

                            if len(order_resp_floor["error"]) == 0:
                                # Wait for order to propogate
                                time.sleep(10)

                                order_info = get_order_info(order_resp_sl["result"]["txid"][0])

                                trade_data = get_trade_details(order_info['result'][order_resp_floor["result"]["txid"][0]]["trades"][0])

                                trade_data['portfolio_data'] = portfolio_data

                                trade_data['order_reason'] = 'Floor Price'

                                update_order_log(trade_data)

                                print(f'Floor price logged successfully')
                                logging.info(f'Floor price logged successfully')

                                remove_coin_from_portfolio(coin)

                                print(f'{coin} removed from portfolio')
                                logging.info(f'{coin} removed from portfolio')

                                # Adjust the "price to buy" in case the price has dropped lower than 
                                # the price we purchased at to try and recoup losses on the next run.
                                config['price_to_buy'] = live_price

                                # if his_watch_has_ended:
                                break
                    

                # check SL
                if float(live_price) < float(portfolio_data[coin]['stop_loss']):
                    if test_mode:
                        remove_coin_from_portfolio(coin)

                        order_log_data = {}
                        order_log_data[coin] = {"order_reason":"Stop Loss", "price": float(live_price)}

                        update_order_log(order_log_data)

                        print(f'SL hit at price: {live_price}')
                        logging.info(f'SL hit at price: {live_price}')

                        # Adjust the "price to buy" in case the price has dropped lower than 
                        # the price we purchased at to try and recoup losses on the next run.
                        config['price_to_buy'] = live_price

                        # if his_watch_has_ended:
                        break
                    

                    else:

                        print(f'SL hit at price: {live_price}')
                        logging.info(f'SL hit at price: {live_price}')

                        order_resp_sl = place_order(coin, 'sell', portfolio_data[coin]['vol'])

                        if len(order_resp_sl["error"]) == 0:
                            # Wait for order to propogate
                            time.sleep(10)

                            order_info = get_order_info(order_resp_sl["result"]["txid"][0])

                            trade_data = get_trade_details(order_info['result'][order_resp_sl["result"]["txid"][0]]["trades"][0])
                            trade_data['portfolio_data'] = portfolio_data

                            trade_data['order_reason'] = 'Take Profit'

                            update_order_log(trade_data)

                            print(f'SL logged successfully')
                            logging.info(f'SL logged successfully')

                            remove_coin_from_portfolio(coin)

                            print(f'{coin} removed from portfolio')
                            logging.info(f'{coin} removed from portfolio')

                            # Adjust the "price to buy" in case the price has dropped lower than 
                            # the price we purchased at to try and recoup losses on the next run.
                            config['price_to_buy'] = live_price

                            # if his_watch_has_ended:
                            break
                
                
                print(f'Neither TP: {portfolio_data[coin]["take_profit"]} nor SL: {portfolio_data[coin]["stop_loss"]} nor Floor Price: {portfolio_data[coin]["bought_at"]} was hit')
                logging.info(f'Neither TP: {portfolio_data[coin]["take_profit"]} nor SL: {portfolio_data[coin]["stop_loss"]} nor Floor Price: {portfolio_data[coin]["bought_at"]} was hit')

    print('Sleep timer hit')
    logging.info('Sleep timer hit')
    time.sleep(30)


if __name__ == "__main__":
    run()