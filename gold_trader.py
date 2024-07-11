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

from trader import Trader, StrategyUniversal, MA_Line

smallest_period = 9
middle_period = 13
biggest_period = 13

SYMBOL = "GOLD"
VOLUME = 0.01
PERIOD = "M30"

eurusd_lines_M = {
    (PERIOD, smallest_period) : MA_Line(SYMBOL, PERIOD, smallest_period),
    (PERIOD, middle_period) : MA_Line(SYMBOL, PERIOD, middle_period),
    (PERIOD, biggest_period) : MA_Line(SYMBOL, PERIOD, biggest_period)
}

strat = StrategyUniversal(PERIOD, smallest_period, middle_period, biggest_period)
trader = Trader(SYMBOL, VOLUME, strat)

starting = True

while True:
    for key, line in eurusd_lines_M.items():
        line.UpdateValue(0.01)
        sleep(0.5)

    trader.Update(eurusd_lines_M)

    sleep(1)

    if starting:
        print(trader.status, "current status")
        starting = False
# 2969.23 reference account
