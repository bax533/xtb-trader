from trader import DebugTrader, TraderStatus, StrategyUniversal, StrategyUniversalWithLongterm, MA_Line, SIGNAL_Line

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--wandb', dest='wandb', type=bool, help='use wandb')
parser.add_argument('--print-price', dest='print_price', type=bool, help='print current calculated price and exit')
parser.add_argument('--price-divider', dest='price_divider', type=float, help='divide price received from API')
parser.add_argument('--plot', dest='plot', type=bool, help='plot results')
parser.add_argument('--symbol', dest='symbol', type=str, help='symbol to analyse')
parser.add_argument('--chart-period', dest='chart_period', type=str, help='symbol to analyse')
parser.add_argument('--pips-size', dest='pips_size', type=float, help='pips size')
parser.add_argument('--pips-value', dest='pips_value', type=float, help='pips value')
parser.add_argument('--volume', dest='volume', type=float, help='lot volume to analyse')
parser.add_argument('--num-of-candles', dest='num_of_candles', type=int, help='num of candles to analyse')
parser.add_argument('--take-profit-pips', dest='take_profit_pips', type=float, help='take profit pips')
parser.add_argument('--spread-pips', dest='spread_pips', type=float, help='spread_pips')
parser.add_argument('--print-candle', dest='print_candle', type=bool, help='print candle received from API')
parser.add_argument('--candle-behind', dest='candle_behind', type=bool, help='buy and sell with candle behind')

args = parser.parse_args()

if args.price_divider:
    print("PRICE DICIDER", args.price_divider)

if not args.symbol or not args.chart_period:
    print("PROVIDE SYMBOL AND CHART PERIOD ex. --symbol EURUSD --chart-period M30")
    exit()

import numpy as np
from time import sleep
from enum import Enum
import numpy as np
from scipy.signal import lfiltic, lfilter

from env import username, password

import time
import itertools
from itertools import product
import wandb

_WANDB = args.wandb
_PRINT_PRICE = args.print_price
_PLOT = args.plot

CHART_PERIODS = [args.chart_period]
SYMBOL = args.symbol


num_of_candles = args.num_of_candles if args.num_of_candles else 600
print("NUM OF CANDLES: ", num_of_candles)
take_profit_pips = args.take_profit_pips if args.take_profit_pips else -1.0
spread_pips = args.spread_pips if args.spread_pips else 0.0
print("spread_pips: ", spread_pips)
print_candle = args.print_candle if args.print_candle else False
candle_behind = args.candle_behind if args.candle_behind else False

print("TAKE PROFIT: ", take_profit_pips, "pips")
start_it = 205

price_divider = dict({
    "US100": 100.00000,
    "DE40": 10.00000,
    "EURUSD": 100.00000
})

if args.price_divider:
    price_divider[args.symbol] = args.price_divider
else:
    price_divider[args.symbol] = 1.0

_WANDB_PROJECT_NAME = "XTB_TP_SPREAD_LONGTERM_EMAS_" + SYMBOL + "_NO_CANDLES_" + str(num_of_candles-start_it)

if _WANDB:
    wandb.login()

import matplotlib
import matplotlib.pyplot as plt

from API import XTB

API = XTB(username, password)

def ewma_linear_filter(array, window):
    alpha = 2 /(window + 1)
    b = [alpha]
    a = [1, alpha-1]
    zi = lfiltic(b, a, array[0:1], [0])
    return lfilter(b, a, array, zi=zi)[0]

def dict_values_list(lines_dict):
    return [val for key, val in lines_dict.items()]

results = []

SMALL_PERIODS_BUY = [6, 7, 8, 9, 10, 11]
MIDDLE_PERIODS_BUY = [7, 8, 9, 10, 11, 12, 13, 14, 15]

SMALL_PERIODS_SELL = [2, 3, 4, 5, 6, 7, 8, 9]
MIDDLE_PERIODS_SELL = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]



FAST_PERIODS_LONGTERM = [34, 55, 65, 75, 100]
SLOW_PERIODS_LONGTERM = [55, 65, 75, 100, 200]

# SIGNAL_PERIOD = 9

# if (not args.pips_size or not args.pips_value or not args.volume) and not args.print_price:
#     print("PROVIDE pips_size, pips_value and volume !!!")
#     exit()

VOLUME = args.volume if args.volume else 0.05
PIPS_SIZE = args.pips_size if args.pips_size else 1.0
PIPS_VALUE = args.pips_value if args.pips_value else 1.0 # USD
print(PIPS_VALUE, "PIPS_VALUE")

combinations_buy = list(product(SMALL_PERIODS_BUY, MIDDLE_PERIODS_BUY))
combinations_longterm = list(product(FAST_PERIODS_LONGTERM, SLOW_PERIODS_LONGTERM))

tp_pips_to_percent = dict({
    -1.0: -1.0,
    #      BITCOIN 0.03
    # 500: 2.0,
    # 750: 2.75,
    # 1000: 3.5,
    # 1500: 5,
    # 2000: 6.5,
    # 2500: 8,
    # 3000: 10,
    # 3500: 11.5,
    # 4000: 13,

    ##################
    # GOLD
    ##################
    # 2: 1.6,
    # 3: 2.5,
    # 4: 3.3,
    # 5: 4.1,
    # 6: 4.9,
    # 7: 5.7,
    # 8: 6.5,
    # 9: 7.3,
    # 10: 8.2,
    # 11: 9.0,
    # 12: 9.8,
    # 13: 10.6,
    # 14: 11.4,
    # 15: 12.3,
    # 16: 13.1,
    # 17: 13.9,
    # 18: 14.7,
    # 19: 15.5,
    # 20: 16.3,
    # 21: 17.1
})

for PERIOD in CHART_PERIODS:
    print("CHART PERIOD:", PERIOD)
    sleep(1)
    candles = API.get_Candles(PERIOD, SYMBOL, qty_candles=num_of_candles, print_candle=print_candle)[1:]
    num_of_candles = len(candles)
    print(num_of_candles, "NUM OF CANDLES RECEIVED")
    sleep(1)
    for CONFIG_BUY in combinations_buy:
        smallest_period_buy = CONFIG_BUY[0]
        middle_period_buy = CONFIG_BUY[1]
        if smallest_period_buy >= middle_period_buy:
            continue

        smallest_period_sell = smallest_period_buy
        middle_period_sell = middle_period_buy

        for CONFIG_LONGTERM in combinations_longterm:
            fast_period_longterm = CONFIG_LONGTERM[0]
            slow_period_longterm = CONFIG_LONGTERM[1]

            if fast_period_longterm >= slow_period_longterm:
                continue

            for take_profit_pips, tp_percent in tp_pips_to_percent.items():

                RUN_NAME = str(SYMBOL)+'_'+str(PERIOD)+'_'+str(smallest_period_buy)+'_'+str(middle_period_buy) + \
                    "_LONGTERM_EMAS_" + str(fast_period_longterm) + "_" + str(slow_period_longterm)

                print(RUN_NAME, "CURRENT RUN")

                if _WANDB:
                    run = wandb.init(
                        # Set the project where this run will be logged
                        name=RUN_NAME,
                        project=_WANDB_PROJECT_NAME + "_" + PERIOD,
                        # Track hyperparameters and run metadata
                        config={
                            "CHART_PERIOD": PERIOD,
                            "symbol": SYMBOL,
                            "NUM_OF_CANDLES": num_of_candles
                        },
                    )

                lines_sell = {
                    "s" : MA_Line(SYMBOL, PERIOD, smallest_period_sell),
                    "m" : MA_Line(SYMBOL, PERIOD, middle_period_sell),
                    "b" : MA_Line(SYMBOL, PERIOD, middle_period_sell),
                    "longterm_s" : MA_Line(SYMBOL, PERIOD, fast_period_longterm),
                    "longterm_m" : MA_Line(SYMBOL, PERIOD, slow_period_longterm)
                }
                lines_buy = {
                    "s" : MA_Line(SYMBOL, PERIOD, smallest_period_buy),
                    "m" : MA_Line(SYMBOL, PERIOD, middle_period_buy),
                    "b" : MA_Line(SYMBOL, PERIOD, middle_period_buy),
                    "longterm_s" : MA_Line(SYMBOL, PERIOD, fast_period_longterm),
                    "longterm_m" : MA_Line(SYMBOL, PERIOD, slow_period_longterm)
                }

                strat = StrategyUniversalWithLongterm(PERIOD)
                trader = DebugTrader(SYMBOL, VOLUME, strat, PIPS_SIZE, PIPS_VALUE, DEBUG = False, take_profit_pips=take_profit_pips, spread_pips=spread_pips)

                end_it = num_of_candles - start_it - 1

                xs = []
                ys = []
                markers = []
                colors = []

                emas_s = []
                emas_m = []
                emas_b = []
                # signals = []

                start = time.time()

                for i in range(0, end_it):

                    xs.append(i)
                    for key, line in lines_sell.items():
                        line.UpdateValue(candles[i:i + start_it + (0 if candle_behind else 1)], price_divider[SYMBOL])
                    for key, line in lines_buy.items():
                        line.UpdateValue(candles[i:i + start_it + (0 if candle_behind else 1)], price_divider[SYMBOL])

                    cur_price = (candles[i+start_it]["open"] + candles[i+start_it]["close"])/price_divider[SYMBOL]
                    
                    if _PRINT_PRICE:
                        print(cur_price, "PRICE")
                        exit()
                    
                    if _PLOT:
                        ys.append(cur_price)
                    
                    trader.Update(lines_sell, lines_buy, cur_price)
                    trader.Update(lines_sell, lines_buy, cur_price)

                    if _PLOT:
                        colors.append(
                            'green' if trader.status == TraderStatus.LONG else
                            ('red' if trader.status == TraderStatus.SHORT else 'black')
                        )
                        markers.append(
                            '^' if trader.status == TraderStatus.LONG else
                            ('v' if trader.status == TraderStatus.SHORT else 'o')
                        )
                    
                    if _WANDB:
                        wandb.log({"current_money": trader.profit, "current_price": cur_price, "current_short_profit": trader.short_profit,
                            "current_long_profit": trader.long_profit, "num_of_trades": trader.num_of_trades,
                            "short_loses": trader.short_loses, "long_loses": trader.long_loses,
                            "short_trades": trader.short_trades, "long_trades": trader.long_trades})

                if _WANDB:
                    wandb.log({"final_money": trader.profit, "chart_period": PERIOD, "smallest_period_buy": smallest_period_buy, "middle_period_buy" : middle_period_buy, "smallest_period_sell": smallest_period_sell, "middle_period_sell" : middle_period_sell,
                        "final_short_profit": trader.short_profit, "final_long_profit": trader.long_profit, "final_num_of_trades": trader.num_of_trades,
                        "final_short_loses": trader.short_loses, "final_long_loses": trader.long_loses, "final_loses": trader.long_loses + trader.short_loses,
                            "final_short_trades": trader.short_trades, "final_long_trades": trader.long_trades, "tp_percent": tp_percent})
                    run.finish()
                    wandb.finish()
                print({"final_money": trader.profit, "chart_period": PERIOD, "smallest_period_buy": smallest_period_buy, "middle_period_buy" : middle_period_buy, "smallest_period_sell": smallest_period_sell, "middle_period_sell" : middle_period_sell,
                        "final_short_profit": trader.short_profit, "final_long_profit": trader.long_profit, "final_num_of_trades": trader.num_of_trades,
                        "final_short_loses": trader.short_loses, "final_long_loses": trader.long_loses, "final_loses": trader.long_loses + trader.short_loses,
                            "final_short_trades": trader.short_trades, "final_long_trades": trader.long_trades})
                sleep(0.5)
API.logout()