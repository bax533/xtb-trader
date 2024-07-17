import numpy as np
from time import sleep
from enum import Enum
import numpy as np
from scipy.signal import lfiltic, lfilter
from env import username, password
from API import XTB

from trader import Trader, StrategyUniversal, MA_Line

def RunTrader(SYMBOL, PERIOD, VOLUME, smallest_period, middle_period, biggest_period,
    buy_candle_behind=False, Debug=False, Verbose=False):

    API = XTB(username, password)
    API.login()

    eurusd_lines_M_sell = {
        (PERIOD, smallest_period) : MA_Line(SYMBOL, PERIOD, smallest_period),
        (PERIOD, middle_period) : MA_Line(SYMBOL, PERIOD, middle_period),
        (PERIOD, biggest_period) : MA_Line(SYMBOL, PERIOD, biggest_period)
    }

    eurusd_lines_M_buy = {
        (PERIOD, smallest_period) : MA_Line(SYMBOL, PERIOD, smallest_period, buy_candle_behind),
        (PERIOD, middle_period) : MA_Line(SYMBOL, PERIOD, middle_period, buy_candle_behind),
        (PERIOD, biggest_period) : MA_Line(SYMBOL, PERIOD, biggest_period, buy_candle_behind)
    }

    strat = StrategyUniversal(PERIOD, smallest_period, middle_period, biggest_period)
    trader = Trader(SYMBOL, VOLUME, strat, Debug=Debug, Verbose=Verbose)

    starting = True

    while True:
        API.login()
        sleep(0.5)
        candles = API.get_Candles(PERIOD, SYMBOL, qty_candles=30)[1:]

        for key, line in eurusd_lines_M_sell.items():
            line.UpdateValue(candles, divider=100)
            sleep(0.5)
        for key, line in eurusd_lines_M_buy.items():
            line.UpdateValue(candles, divider=100)
            sleep(0.5)

        trader.Update(eurusd_lines_M_sell, eurusd_lines_M_buy)

        sleep(1)

        if starting:
            print(trader.status, "current status")
            starting = False