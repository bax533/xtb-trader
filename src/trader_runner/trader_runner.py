import numpy as np
from time import sleep
from enum import Enum
import numpy as np
from scipy.signal import lfiltic, lfilter
from env import username, password
from API.API import XTB

from trader.trader import Trader
from strategies.StrategyUniversal import StrategyUniversal

from lines.MA_Line import MA_Line

def RunTrader(SYMBOL, PERIOD, VOLUME, smallest_period, middle_period, biggest_period,
    buy_candle_behind=False, Debug=False, Verbose=False):

    API = XTB(username, password)
    API.login()

    eurusd_lines_M_sell = {
        "s" : MA_Line(smallest_period),
        "m" : MA_Line(middle_period),
        "b" : MA_Line(biggest_period)
    }

    eurusd_lines_M_buy = {
        "s" : MA_Line(smallest_period),
        "m" : MA_Line(middle_period),
        "b" : MA_Line(biggest_period)
    }

    strat = StrategyUniversal(PERIOD)
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