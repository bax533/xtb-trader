import numpy as np
from time import sleep
from enum import Enum
import numpy as np
from scipy.signal import lfiltic, lfilter
import matplotlib.pyplot as plt
from env import username, password
from trader.trader import Trader, TraderStatus
from strategies.StrategyUniversal import StrategyUniversal
from lines.MA_Line import MA_Line
from lines.MACD_Line import MACD_Line
from API.API import XTB
import matplotlib

API = XTB(username, password)


def TEST_DEBUG():
    smallest_period = 9
    middle_period = 13
    biggest_period = 13

    SYMBOL = "GOLD"
    VOLUME = 0.05
    PERIOD = "M30"
    smallest_period = 9
    middle_period = 13
    biggest_period = 13
    price_divider = 100.0

    strat = StrategyUniversal(PERIOD)
    trader = Trader(SYMBOL, VOLUME, strat, Debug=True)
    lines_sell = {
        "s" : MA_Line(smallest_period),
        "m" : MA_Line(middle_period),
        "b" : MA_Line(biggest_period)
        
    }
    lines_buy = {
        "s" : MA_Line(smallest_period),
        "m" : MA_Line(middle_period),
        "b" : MA_Line(biggest_period)
    }

    candles = API.get_Candles(PERIOD, SYMBOL, qty_candles=40)[1:]#start_time=1720477685000, end_time=1720524485000)[1:]
    start_it = 30

    xs = []
    ys = []
    s = []
    m = []

    for i in range(len(candles) - start_it):
        for key, line in lines_sell.items():
            line.UpdateValue(candles[i:i+start_it+1], price_divider)
            print()
        for key, line in lines_buy.items():
            line.UpdateValue(candles[i:i+start_it+1], price_divider)

        trader.Update(lines_sell, lines_buy)
        print(i, trader.status, 1)
        trader.Update(lines_sell, lines_buy)
        print(i, trader.status, 2)
        xs.append(i)
        ys.append((candles[i+start_it]["open"]+candles[i+start_it]["close"])/price_divider)
        s.append(lines_sell["s"].value)
        m.append(lines_sell["m"].value)


    plt.plot(xs, s, color='cyan')
    plt.plot(xs, m, color='blue')
    # plt.plot(xs, signals, color='red')
    plt.plot(xs, ys, color='black')
    plt.scatter(xs, ys, color='black')
    plt.show()

def TEST_DEBUG_MACD():
    FAST_EMA = 12
    SLOW_EMA = 26
    SIGNAL_EMA = 8

    SYMBOL = "GOLD"
    VOLUME = 0.05
    PERIOD = "M30"
    price_divider = 100.0

    strat = StrategyUniversal(PERIOD)
    trader = Trader(SYMBOL, VOLUME, strat, Debug=True)
    macd_lines = MACD_Lines(FAST_EMA, SLOW_EMA, SIGNAL_EMA)

    candles = API.get_Candles(PERIOD, SYMBOL, qty_candles=40)[1:]#start_time=1720477685000, end_time=1720524485000)[1:]
    start_it = 30

    xs = []
    ys = []
    s = []
    m = []

    for i in range(len(candles) - start_it):
        for key, line in lines_sell.items():
            line.UpdateValue(candles[i:i+start_it+1], price_divider)
            print()
        for key, line in lines_buy.items():
            line.UpdateValue(candles[i:i+start_it+1], price_divider)

        trader.Update(lines_sell, lines_buy)
        print(i, trader.status, 1)
        trader.Update(lines_sell, lines_buy)
        print(i, trader.status, 2)
        xs.append(i)
        ys.append((candles[i+start_it]["open"]+candles[i+start_it]["close"])/price_divider)
        s.append(lines_sell["s"].value)
        m.append(lines_sell["m"].value)


    plt.plot(xs, s, color='cyan')
    plt.plot(xs, m, color='blue')
    # plt.plot(xs, signals, color='red')
    plt.plot(xs, ys, color='black')
    plt.scatter(xs, ys, color='black')
    plt.show()

def TEST_GOLD_CANDLE_CORRECTNESS_1():
    smallest_period = 9
    middle_period = 13
    biggest_period = 13

    SYMBOL = "GOLD"
    VOLUME = 0.05
    PERIOD = "M30"
    smallest_period = 9
    middle_period = 13
    biggest_period = 13
    price_divider = 100.0

    expect_values_sell_s = {
        0 : 2372.316980847976 ,
        1 : 2373.503584678381 ,
        2 : 2374.7808677427047 ,
        3 : 2375.3526941941636 ,
        4 : 2376.364155355331 ,
        5 : 2377.701324284265 ,
        6 : 2377.953059427412 ,
        7 : 2377.31444754193 ,
        8 : 2377.613558033544 ,
        9 : 2377.8248464268354 ,
        10 : 2377.9838771414684 ,
    }

    expect_values_sell_m = {
        0 : 2371.806185577455 ,
        1 : 2372.7267304949614 ,
        2 : 2373.750054709967 ,
        3 : 2374.3057611799723 ,
        4 : 2375.1777952971192 ,
        5 : 2376.3023959689594 ,
        6 : 2376.68205368768 ,
        7 : 2376.40747458944 ,
        8 : 2376.7506925052344 ,
        9 : 2377.024879290201 ,
        10 : 2377.2527536773155 ,
    }

    strat = StrategyUniversal(PERIOD, smallest_period, middle_period, biggest_period)
    trader = Trader(SYMBOL, VOLUME, strat, Debug=True)
    lines_sell = {
        (PERIOD, smallest_period) : MA_Line(SYMBOL, PERIOD, smallest_period),
        (PERIOD, middle_period) : MA_Line(SYMBOL, PERIOD, middle_period),
        (PERIOD, biggest_period) : MA_Line(SYMBOL, PERIOD, biggest_period)
    }
    lines_buy = {
        (PERIOD, smallest_period) : MA_Line(SYMBOL, PERIOD, smallest_period),
        (PERIOD, middle_period) : MA_Line(SYMBOL, PERIOD, middle_period),
        (PERIOD, biggest_period) : MA_Line(SYMBOL, PERIOD, biggest_period)
    }

    candles = API.get_Candles(PERIOD, SYMBOL, start_time=1720576625000, end_time=1720630625000)[1:]
    start_it = 20

    for i in range(len(candles) - start_it):

        for key, line in lines_sell.items():
            line.UpdateValueDebug(candles[:i+start_it], price_divider)

        for key, line in lines_buy.items():
            line.UpdateValueDebug(candles[:i+start_it], price_divider)

        trader.Update(lines_sell, lines_buy)

        assert(lines_sell[(PERIOD, smallest_period)].value == expect_values_sell_s[i])
        assert(lines_sell[(PERIOD, middle_period)].value == expect_values_sell_m[i])
        assert(trader.status == TraderStatus.LONG)

def TEST_GOLD_CANDLE_CORRECTNESS_AND_STATUS_CORRECTNESS_1():
    smallest_period = 9
    middle_period = 13
    biggest_period = 13

    SYMBOL = "GOLD"
    VOLUME = 0.05
    PERIOD = "M30"
    smallest_period = 9
    middle_period = 13
    biggest_period = 13
    price_divider = 100.0

    expect_values_update_1 = {
        0 : TraderStatus.LONG  ,
        1 : TraderStatus.LONG  ,
        2 : TraderStatus.LONG  ,
        3 : TraderStatus.LONG  ,
        4 : TraderStatus.LONG  ,
        5 : TraderStatus.IDLE  ,
        6 : TraderStatus.SHORT ,
        7 : TraderStatus.SHORT ,
        8 : TraderStatus.SHORT ,
        9 : TraderStatus.SHORT ,
        10 : TraderStatus.SHORT ,
        11 : TraderStatus.SHORT ,
    }

    expect_values_update_2 = {
        0 : TraderStatus.LONG  ,
        1 : TraderStatus.LONG  ,
        2 : TraderStatus.LONG  ,
        3 : TraderStatus.LONG  ,
        4 : TraderStatus.LONG  ,
        5 : TraderStatus.SHORT  ,
        6 : TraderStatus.SHORT ,
        7 : TraderStatus.SHORT ,
        8 : TraderStatus.SHORT ,
        9 : TraderStatus.SHORT ,
        10 : TraderStatus.SHORT ,
        11 : TraderStatus.SHORT ,
    }

    strat = StrategyUniversal(PERIOD, smallest_period, middle_period, biggest_period)
    trader = Trader(SYMBOL, VOLUME, strat, Debug=True)
    lines_sell = {
        (PERIOD, smallest_period) : MA_Line(SYMBOL, PERIOD, smallest_period),
        (PERIOD, middle_period) : MA_Line(SYMBOL, PERIOD, middle_period),
        (PERIOD, biggest_period) : MA_Line(SYMBOL, PERIOD, biggest_period)
    }
    lines_buy = {
        (PERIOD, smallest_period) : MA_Line(SYMBOL, PERIOD, smallest_period),
        (PERIOD, middle_period) : MA_Line(SYMBOL, PERIOD, middle_period),
        (PERIOD, biggest_period) : MA_Line(SYMBOL, PERIOD, biggest_period)
    }

    candles = API.get_Candles(PERIOD, SYMBOL, start_time=1720477685000, end_time=1720524485000)[1:]
    start_it = 15

    for i in range(len(candles) - start_it):
        for key, line in lines_sell.items():
            line.UpdateValueDebug(candles[:i+start_it], price_divider)
            print()
        for key, line in lines_buy.items():
            line.UpdateValueDebug(candles[:i+start_it], price_divider)

        trader.Update(lines_sell, lines_buy)
        assert(trader.status == expect_values_update_1[i])
        trader.Update(lines_sell, lines_buy)
        assert(trader.status == expect_values_update_2[i])


TEST_DEBUG()

# TEST_GOLD_CANDLE_CORRECTNESS_1()

# TEST_GOLD_CANDLE_CORRECTNESS_AND_STATUS_CORRECTNESS_1()

#####