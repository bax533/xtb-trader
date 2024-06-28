import numpy as np
from time import sleep
from enum import Enum
import numpy as np
from scipy.signal import lfiltic, lfilter
from env import username, password
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

from trader import Trader, StrategyM5, StrategyM1, MA_Line, \
    smallest_period, middle_period, biggest_period


de40_lines_H = {
    ("H1", smallest_period) : MA_Line("DE40", "H1", smallest_period),
    ("H1", middle_period) : MA_Line("DE40", "H1", middle_period),
    ("H1", biggest_period) : MA_Line("DE40", "H1", biggest_period),
    ("H4", smallest_period) : MA_Line("DE40", "H4", smallest_period),
    ("H4", middle_period) : MA_Line("DE40", "H4", middle_period),
    ("H4", biggest_period) : MA_Line("DE40", "H4", biggest_period)
}
de40_lines_M = {
    ("M1", smallest_period) : MA_Line("DE40", "M1", smallest_period),
    ("M1", middle_period) : MA_Line("DE40", "M1", middle_period),
    ("M1", biggest_period) : MA_Line("DE40", "M1", biggest_period),
    ("M5", smallest_period) : MA_Line("DE40", "M5", smallest_period),
    ("M5", middle_period) : MA_Line("DE40", "M5", middle_period),
    ("M5", biggest_period) : MA_Line("DE40", "M5", biggest_period),
    ("M15", smallest_period) : MA_Line("DE40", "M15", smallest_period),
    ("M15", middle_period) : MA_Line("DE40", "M15", middle_period),
    ("M15", biggest_period) : MA_Line("DE40", "M15", biggest_period)
}

strat = StrategyM5()
trader = Trader("DE40", 0.04, strat)

def DEBUG():
    import matplotlib
    import matplotlib.pyplot as plt

    num_of_candles = 40

    candles = API.get_Candles("M15", "DE40", qty_candles=num_of_candles)[1:]
    closing_values = [candle["open"] + candle["close"] for candle in candles]

    start_it=20

    emas_5 = ewma_linear_filter(np.array(closing_values), smallest_period)[start_it:]
    emas_8 = ewma_linear_filter(np.array(closing_values), middle_period)[start_it:]
    emas_15 = ewma_linear_filter(np.array(closing_values), biggest_period)[start_it:]

    plt.plot([i for i in range(num_of_candles-start_it)], closing_values[start_it:], color='black')
    plt.plot([i for i in range(num_of_candles-start_it)], emas_5, color='cyan')
    plt.plot([i for i in range(num_of_candles-start_it)], emas_8, color='blue')
    plt.plot([i for i in range(num_of_candles-start_it)], emas_15, color='green')
    plt.plot([i for i in range(num_of_candles-start_it)], emas_20, color='red')

    for i in range(len(emas_5)):
        plt.scatter([i], [
            closing_values[start_it + i]
        ], color='magenta' if strat.ShouldShort_M_debug(emas_5[i], emas_8[i], emas_15[i], emas_20[i]) else \
            ('yellow' if strat.ShouldLong_M_debug(emas_5[i], emas_8[i], emas_15[i], emas_20[i]) else 'black'))

    plt.show()


while True:
    for key, line in de40_lines_M.items():
        line.UpdateValue()
        sleep(0.5)

    for key, line in de40_lines_M.items():
        line.UpdateNeighbours(dict_values_list(de40_lines_M))

    trader.Update(de40_lines_M)

    sleep(1)
    #print(trader.status, "current status")

# 9444.00 reference account

API.logout()
