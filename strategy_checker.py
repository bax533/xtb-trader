from trader import DebugTrader, TraderStatus, StrategyUniversal, MA_Line

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

_WANDB = True
_PRINT_PRICE = False
_WANDB_PROJECT_NAME = "trading_DE40_parameter_check_SHORTING_LONGING_1000_candles"
_PLOT = False

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

SMALL_PERIODS = [i for i in range(1, 25)]
MIDDLE_PERIODS = [i for i in range(2, 30)]

CHART_PERIODS = ["M30"]
SYMBOL = "DE40"

VOLUME = 0.04
PIPS_SIZE = 1
PIPS_VALUE = 1 # USD
print(PIPS_VALUE, "PIPS_VALUE")

combinations = list(product(SMALL_PERIODS, MIDDLE_PERIODS))

num_of_candles = 1000
start_it = 35

for PERIOD in CHART_PERIODS:
    print("CHART PERIOD:", PERIOD)
    sleep(1)
    candles = API.get_Candles(PERIOD, SYMBOL, qty_candles=num_of_candles)[1:]
    sleep(1)
    for CONFIG in combinations:

        smallest_period = CONFIG[0]
        middle_period = CONFIG[1]

        for b in range(6):
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

            start = time.time()

            for i in range(start_it, end_it):
                it = i - start_it

                xs.append(i)
                for key, line in us100_lines_M.items():
                    line.UpdateValueDebug(candles[i:i+start_it], 10.00000)

                if _PLOT:
                    emas_s.append(us100_lines_M[(PERIOD, smallest_period)].value/10.000000)
                    emas_m.append(us100_lines_M[(PERIOD, middle_period)].value/10.000000)
                    emas_b.append(us100_lines_M[(PERIOD, biggest_period)].value/10.000000)

                cur_price = (candles[i+start_it+1]["open"] + candles[i+start_it+1]["close"])/10.00000
                
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
                    wandb.log({"current_money": trader.profit, "current_price": cur_price})

            if _PLOT:
                print("PROFIT:", trader.profit)
                plt.plot(xs, emas_s, color='cyan')
                plt.plot(xs, emas_m, color='blue')
                plt.plot(xs, ys, color='black')
                plt.show()

            # 9444.00 reference account
            if _WANDB:
                wandb.log({"final_money": trader.profit, "chart_period": PERIOD, "smallest_period": smallest_period, "middle_period" : middle_period, "biggest_period": biggest_period})
                run.finish()
                wandb.finish()
            sleep(1)
API.logout()