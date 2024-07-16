import numpy as np
from time import sleep
from enum import Enum
import numpy as np
from scipy.signal import lfiltic, lfilter
from env import username, password
from trader import Trader, StrategyUniversal, MA_Line, ewma_linear_filter


def TEST_GOLD_CORRECT_CANDLES_1():
    smallest_period = 9
    middle_period = 13
    biggest_period = 13

    SYMBOL = "GOLD"
    VOLUME = 0.05
    PERIOD = "M30"

    eurusd_lines_M_sell = {
        (PERIOD, smallest_period) : MA_Line(SYMBOL, PERIOD, smallest_period),
        (PERIOD, middle_period) : MA_Line(SYMBOL, PERIOD, middle_period),
        (PERIOD, biggest_period) : MA_Line(SYMBOL, PERIOD, biggest_period)
    }

    eurusd_lines_M_buy = {
        (PERIOD, smallest_period) : MA_Line(SYMBOL, PERIOD, smallest_period, True),
        (PERIOD, middle_period) : MA_Line(SYMBOL, PERIOD, middle_period, True),
        (PERIOD, biggest_period) : MA_Line(SYMBOL, PERIOD, biggest_period, True)
    }

    for key, line in eurusd_lines_M_sell.items():
        line.UpdateValue(0.01)
        sleep(0.5)
    for key, line in eurusd_lines_M_buy.items():
        line.UpdateValue(0.01)
        sleep(0.5)

    strat = StrategyUniversal(PERIOD, smallest_period, middle_period, biggest_period)
    trader = Trader(SYMBOL, VOLUME, strat, Debug=True)

