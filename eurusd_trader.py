import numpy as np
from time import sleep
from enum import Enum
import numpy as np
from scipy.signal import lfiltic, lfilter
from env import username, password

def ewma_linear_filter(array, window):
    alpha = 2 /(window + 1)
    b = [alpha]
    a = [1, alpha-1]
    zi = lfiltic(b, a, array[0:1], [0])
    return lfilter(b, a, array, zi=zi)[0]

def dict_values_list(lines_dict):
    return [val for key, val in lines_dict.items()]

from trader import Trader, StrategyUniversal, MA_Line, \
    smallest_period, middle_period, biggest_period

SYMBOL = "EURUSD"
VOLUME = 0.4
PERIOD = "M15"

eurusd_lines_M = {
    ("M1", smallest_period) : MA_Line(SYMBOL, "M1", smallest_period),
    ("M1", middle_period) : MA_Line(SYMBOL, "M1", middle_period),
    ("M1", biggest_period) : MA_Line(SYMBOL, "M1", biggest_period),
    ("M5", smallest_period) : MA_Line(SYMBOL, "M5", smallest_period),
    ("M5", middle_period) : MA_Line(SYMBOL, "M5", middle_period),
    ("M5", biggest_period) : MA_Line(SYMBOL, "M5", biggest_period),
    ("M15", smallest_period) : MA_Line(SYMBOL, "M15", smallest_period),
    ("M15", middle_period) : MA_Line(SYMBOL, "M15", middle_period),
    ("M15", biggest_period) : MA_Line(SYMBOL, "M15", biggest_period)
}

strat = strat = StrategyUniversal(PERIOD, smallest_period, middle_period, biggest_period)
trader = Trader(SYMBOL, VOLUME, strat)

while True:
    for key, line in eurusd_lines_M.items():
        line.UpdateValue(0.001)
        sleep(0.5)

    trader.Update(eurusd_lines_M)

    sleep(1)
    #print(trader.status, "current status")

# 9764.98 reference account
