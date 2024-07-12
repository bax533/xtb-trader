import numpy as np
from time import sleep
from enum import Enum
import numpy as np
from scipy.signal import lfiltic, lfilter
from env import username, password

from API import XTB

API = XTB(username, password)

from trader import Trader, StrategyM5, StrategyM1, MA_Line

def ewma_linear_filter(array, window):
    alpha = 2 /(window + 1)
    b = [alpha]
    a = [1, alpha-1]
    zi = lfiltic(b, a, array[0:1], [0])
    return lfilter(b, a, array, zi=zi)[0]

def dict_values_list(lines_dict):
    return [val for key, val in lines_dict.items()]


us100_lines_H = {
    ("H1", smallest_period) : MA_Line("US100", "H1", smallest_period),
    ("H1", middle_period) : MA_Line("US100", "H1", middle_period),
    ("H1", biggest_period) : MA_Line("US100", "H1", biggest_period),
    ("H4", smallest_period) : MA_Line("US100", "H4", smallest_period),
    ("H4", middle_period) : MA_Line("US100", "H4", middle_period),
    ("H4", biggest_period) : MA_Line("US100", "H4", biggest_period)
}
us100_lines_M = {
    ("M1", smallest_period) : MA_Line("US100", "M1", smallest_period),
    ("M1", middle_period) : MA_Line("US100", "M1", middle_period),
    ("M1", biggest_period) : MA_Line("US100", "M1", biggest_period),
    ("M5", smallest_period) : MA_Line("US100", "M5", smallest_period),
    ("M5", middle_period) : MA_Line("US100", "M5", middle_period),
    ("M5", biggest_period) : MA_Line("US100", "M5", biggest_period),
    ("M15", smallest_period) : MA_Line("US100", "M15", smallest_period),
    ("M15", middle_period) : MA_Line("US100", "M15", middle_period),
    ("M15", biggest_period) : MA_Line("US100", "M15", biggest_period)
}

strat = StrategyM5()
trader = Trader("US100", 0.04, strat)

while True:
    for key, line in us100_lines_M.items():
        line.UpdateValue()
        sleep(0.75)

    for key, line in us100_lines_M.items():
        line.UpdateNeighbours(dict_values_list(us100_lines_M))

    trader.Update(us100_lines_M)

    sleep(1)
    #print(trader.status, "current status")

# 9444.00 reference account

API.logout()
