from trader import DebugTrader, TraderStatus, StrategyUniversal, MA_Line, SIGNAL_Line

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
parser.add_argument('--num-candles', dest='num_of_candles', type=int, help='num of candles to analyse')
args = parser.parse_args()

if args.price_divider:
    print(args.price_divider)

if not args.symbol or not args.chart_period:
    print("PROVIDE SYMBOL AND CHART PERIOD ex. --symbol EURUSD --chart-period M30")
    exit()

import numpy as np
from time import sleep
from enum import Enum
import numpy as np
from scipy.signal import lfiltic, lfilter

from env import username, password, demo_username, demo_password

username = demo_username
password = demo_password

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
start_it = 40

price_divider = dict({
    "US100": 100.00000,
    "DE40": 10.00000,
    "EURUSD": 100.00000
})

if args.price_divider:
    price_divider[args.symbol] = args.price_divider
else:
    price_divider[args.symbol] = 1.0

_WANDB_PROJECT_NAME = "strategy_check_" + SYMBOL + "NO_CANDLES_" + str(num_of_candles-start_it)

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

SMALL_PERIODS = [i for i in range(1, 15)]
MIDDLE_PERIODS = [i for i in range(2, 36)]
# SIGNAL_PERIOD = 9

# if (not args.pips_size or not args.pips_value or not args.volume) and not args.print_price:
#     print("PROVIDE pips_size, pips_value and volume !!!")
#     exit()

VOLUME = args.volume if args.volume else 0.05
PIPS_SIZE = args.pips_size if args.pips_size else 1.0
PIPS_VALUE = args.pips_value if args.pips_value else 1.0 # USD
print(PIPS_VALUE, "PIPS_VALUE")

combinations = list(product(SMALL_PERIODS, MIDDLE_PERIODS))


for PERIOD in CHART_PERIODS:
    print("CHART PERIOD:", PERIOD)
    sleep(1)
    candles = API.get_Candles(PERIOD, SYMBOL, qty_candles=num_of_candles)[1:]
    sleep(1)
    for CONFIG in combinations:

        smallest_period = CONFIG[0]
        middle_period = CONFIG[1]

        for b in range(1):
            biggest_period = CONFIG[1] + b

            if smallest_period >= middle_period:
                continue

            RUN_NAME = str(SYMBOL)+'_'+str(PERIOD)+'_'+str(smallest_period)+'_'+str(middle_period)+'_'+str(biggest_period)
            print(RUN_NAME, "CURRENT RUN")

            if _WANDB:
                run = wandb.init(
                    # Set the project where this run will be logged
                    name=RUN_NAME,
                    project=_WANDB_PROJECT_NAME + "_" + PERIOD,
                    # Track hyperparameters and run metadata
                    config={
                        "CHART_PERIOD": PERIOD,
                        "smallest_period": smallest_period,
                        "middle_period": middle_period,
                        "biggest_period": biggest_period,
                        "symbol": SYMBOL,
                        "NUM_OF_CANDLES": num_of_candles
                    },
                )

            us100_lines_M = {
                (PERIOD, smallest_period) : MA_Line(SYMBOL, PERIOD, smallest_period),
                (PERIOD, middle_period) : MA_Line(SYMBOL, PERIOD, middle_period),
                (PERIOD, biggest_period) : MA_Line(SYMBOL, PERIOD, biggest_period),
                # ("SIGNAL", 0) : SIGNAL_Line(SYMBOL, PERIOD, smallest_period, middle_period, SIGNAL_PERIOD)
            }

            strat = StrategyUniversal(PERIOD, smallest_period, middle_period, biggest_period)
            trader = DebugTrader(SYMBOL, VOLUME, strat, PIPS_SIZE, PIPS_VALUE)

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

            for i in range(start_it, end_it):
                it = i - start_it

                xs.append(i)
                for key, line in us100_lines_M.items():
                    line.UpdateValueDebug(candles[i:i+start_it], price_divider[SYMBOL])

                if _PLOT:
                    emas_s.append(us100_lines_M[(PERIOD, smallest_period)].value/price_divider[SYMBOL])
                    emas_m.append(us100_lines_M[(PERIOD, middle_period)].value/price_divider[SYMBOL])
                    emas_b.append(us100_lines_M[(PERIOD, biggest_period)].value/price_divider[SYMBOL])
                    # signals.append(us100_lines_M[("SIGNAL", 0)].value * 10000)

                cur_price = (candles[i+start_it+1]["open"] + candles[i+start_it+1]["close"])/price_divider[SYMBOL]
                
                if _PRINT_PRICE:
                    print(cur_price, "PRICE")
                    exit()
                
                if _PLOT:
                    ys.append(cur_price)
                
                trader.Update(us100_lines_M, cur_price)
                trader.Update(us100_lines_M, cur_price)

                if _PLOT:
                    colors.append(
                        'green' if trader.status == TraderStatus.LONG else
                        ('red' if trader.status == TraderStatus.SHORT else 'black')
                    )
                    markers.append(
                        '^' if trader.status == TraderStatus.LONG else
                        ('v' if trader.status == TraderStatus.SHORT else 'o')
                    )

                if _PLOT:
                    plt.scatter([xs[it]], [ys[it]], color=colors[it], marker=markers[it])
                
                if _WANDB:
                    wandb.log({"current_money": trader.profit, "current_price": cur_price, "current_short_profit": trader.short_profit, "current_long_profit": trader.long_profit, "num_of_trades": trader.num_of_trades})

            if _PLOT:
                print("PROFIT:", trader.profit)
                # print("SIGNALS", signals)
                plt.plot(xs, emas_s, color='cyan')
                plt.plot(xs, emas_m, color='blue')
                # plt.plot(xs, signals, color='red')
                plt.plot(xs, ys, color='black')
                plt.show()

            if _WANDB:
                wandb.log({"final_money": trader.profit, "chart_period": PERIOD, "smallest_period": smallest_period, "middle_period" : middle_period, "biggest_period": biggest_period, "final_short_profit": trader.short_profit, "final_long_profit": trader.long_profit, "final_trades": trader.num_of_trades})
                run.finish()
                wandb.finish()
            sleep(1)
API.logout()