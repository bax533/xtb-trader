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

SMALL_PERIODS = [i for i in range(5, 31)]
MIDDLE_PERIODS = [i for i in range(5, 41)]

CHART_PERIODS = ["M15", "M30", "H1", "H4", "D1"]
SYMBOL = "BITCOIN"

for PERIOD in CHART_PERIODS:
    print("CHART PERIOD:", PERIOD)
    for CONFIG in product(SMALL_PERIODS, MIDDLE_PERIODS):

        smallest_period = CONFIG[0]
        middle_period = CONFIG[1]
        biggest_period = CONFIG[1]

        run = wandb.init(
            # Set the project where this run will be logged
            name=str(SYMBOL)+'_'+str(PERIOD)+'_'+str(smallest_period)+'_'+str(middle_period)+'_'+str(biggest_period),
            project="trading_profit_strategy_validation",
            # Track hyperparameters and run metadata
            config={
                "CHART_PERIOD": PERIOD,
                "smallest_period": smallest_period,
                "middle_period": middle_period,
                "biggest_period": biggest_period,
                "symbol": SYMBOL,
                "STARTING_BALANCE": 10000,
                "NUM_OF_CANDLES": 600
            },
        )

        us100_lines_M = {
            (PERIOD, smallest_period) : MA_Line(SYMBOL, PERIOD, smallest_period),
            (PERIOD, middle_period) : MA_Line(SYMBOL, PERIOD, middle_period),
            (PERIOD, biggest_period) : MA_Line(SYMBOL, PERIOD, biggest_period),
        }

        strat = StrategyUniversal(PERIOD, smallest_period, middle_period, biggest_period)
        trader = DebugTrader(SYMBOL, 0.05, strat)

        num_of_candles = 600
        start_it = 45
        end_it = num_of_candles - start_it - 1


        candles = API.get_Candles(PERIOD, SYMBOL, qty_candles=num_of_candles)[1:]
        sleep(0.75)

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
                line.UpdateValueDebug(candles[i:i+start_it])

            # emas_s.append(us100_lines_M[(PERIOD, smallest_period)].value/100.0)
            # emas_m.append(us100_lines_M[(PERIOD, middle_period)].value/100.0)
            # emas_b.append(us100_lines_M[(PERIOD, biggest_period)].value/100.0)

            cur_price = (candles[i+start_it+1]["open"] + candles[i+start_it+1]["close"])/100.0
            # ys.append(cur_price)
            
            trader.Update(us100_lines_M, cur_price)
            trader.Update(us100_lines_M, cur_price)

            # colors.append(
            #     'green' if trader.status == TraderStatus.LONG else
            #     ('red' if trader.status == TraderStatus.SHORT else 'black')
            # )
            # markers.append(
            #     '^' if trader.status == TraderStatus.LONG else
            #     ('v' if trader.status == TraderStatus.SHORT else 'o')
            # )

            # plt.scatter([xs[it]], [ys[it]], color=colors[it], marker=markers[it])
            wandb.log({"current_money": trader.money, "current_price": cur_price})


        # plt.plot(xs, emas_s, color='cyan')
        # plt.plot(xs, emas_m, color='blue')
        # plt.plot(xs, ys, color='black')

        # 9444.00 reference account
        wandb.log({"final_money": trader.money, "chart_period": PERIOD, "smallest_period": smallest_period, "middle_period" : middle_period, "biggest_period": biggest_period})

API.logout()