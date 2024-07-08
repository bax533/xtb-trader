import numpy as np
from time import sleep
from datetime import datetime
from enum import Enum
import numpy as np
from scipy.signal import lfiltic, lfilter
from env import username, password
from API import XTB
from abc import ABC, abstractmethod


sleep_time_after_transaction = dict({
    "M30": 60*31,
    "M15": 60*15,
    "M5": 60*5
})


def ewma_linear_filter(array, window):
    alpha = 2 /(window + 1)
    b = [alpha]
    a = [1, alpha-1]
    zi = lfiltic(b, a, array[0:1], [0])
    return lfilter(b, a, array, zi=zi)[0]

def dict_values_list(lines_dict):
    return [val for key, val in lines_dict.items()]


smallest_period = 6
middle_period = 16
biggest_period = 18

class MA_Line:
    def __init__(self, symbol: str, chart_period: str, ema_period: int):
        self.line_above = None
        self.line_under = None
        self.previous_above = None
        self.previous_under = None
        self.value = 99999999999.0

        self.symbol = symbol
        self.chart_period = chart_period
        self.ema_period = ema_period

        self.API = XTB(username, password)
        self.API.login()

    def UpdateNeighbours(self, lines):
        self.previous_above = self.line_above
        self.previous_under = self.line_under
        self.line_above = None
        self.line_under = None

        closest_upper_value = 999999999999.0
        closest_under_value = -999999999999.0

        for line in lines:
            if line == self:
                continue

            if line.value - self.value > 0 and line.value - self.value < closest_upper_value - self.value:
                closest_upper_value = line.value
                self.line_above = line
            
            
            if line.value - self.value < 0 and line.value - self.value > closest_under_value - self.value:
                closest_under_value = line.value
                self.line_under = line
    
    def UpdateValue(self, multiplier = 1.0):
        sleep(0.5)
        self.API.login()
        sleep(0.5)
        try:
            candles = self.API.get_Candles(self.chart_period, self.symbol, qty_candles=40)[1:]
            closing_values = [(candle["open"] + candle["close"]) * multiplier for candle in candles]

            self.value = ewma_linear_filter(np.array(closing_values), self.ema_period)[-1]
        except:
            print("could not get candles", datetime.now())
            return

    def UpdateValueDebug(self, candles, divider):
        closing_values = [(candle["open"] + candle["close"])/divider for candle in candles]
        self.value = ewma_linear_filter(np.array(closing_values), self.ema_period)[-1]

    def GetName(self):
        return self.symbol + ", " + self.chart_period + ", " + str(self.ema_period)

    def __eq__(self, other):
        return self.symbol == other.symbol and self.chart_period == other.chart_period and self.ema_period == other.ema_period

class StrategyAbstract(ABC):

    @abstractmethod
    def ShouldShort(self, lines_dict):
        pass

    @abstractmethod
    def ShouldLong(self, lines_dict):
        pass

    @abstractmethod
    def ShouldSellLong(self, lines_dict):
        pass

    @abstractmethod
    def ShouldSellShort(self, lines_dict):
        return self.ShouldLong(lines_dict)

class StrategyM5(StrategyAbstract):
    def __init__(self):
        return

    def ShouldShort(self, lines_dict):
        return lines_dict[("M5", smallest_period)].value < lines_dict[("M5", middle_period)].value \
            and lines_dict[("M5", smallest_period)].value < lines_dict[("M5", biggest_period)].value

    def ShouldSellShort(self, lines_dict):
        return self.ShouldLong(lines_dict)

    def ShouldLong(self, lines_dict):
        return lines_dict[("M5", smallest_period)].value > lines_dict[("M5", middle_period)].value \
            and lines_dict[("M5", smallest_period)].value > lines_dict[("M5", biggest_period)].value
    
    def ShouldSellLong(self, lines_dict):
        return self.ShouldShort(lines_dict)


class StrategyM30(StrategyAbstract):
    def __init__(self):
        return

    def ShouldShort(self, lines_dict):
        return lines_dict[("M30", smallest_period)].value < lines_dict[("M30", middle_period)].value \
            and lines_dict[("M30", smallest_period)].value < lines_dict[("M30", biggest_period)].value

    def ShouldSellShort(self, lines_dict):
        return self.ShouldLong(lines_dict)

    def ShouldLong(self, lines_dict):
        return lines_dict[("M30", smallest_period)].value > lines_dict[("M30", middle_period)].value \
            and lines_dict[("M30", smallest_period)].value > lines_dict[("M30", biggest_period)].value
    
    def ShouldSellLong(self, lines_dict):
        return self.ShouldShort(lines_dict)

class StrategyUniversal(StrategyAbstract):
    def __init__(self, period, s, m, b):
        self.period = period
        self.s = s
        self.m = m
        self.b = b
        return

    def ShouldShort(self, lines_dict):
        return lines_dict[(self.period, self.s )].value < lines_dict[(self.period, self.m)].value \
            and lines_dict[(self.period, self.s )].value < lines_dict[(self.period, self.b)].value

    def ShouldSellShort(self, lines_dict):
        return self.ShouldLong(lines_dict)

    def ShouldLong(self, lines_dict):
        return lines_dict[(self.period, self.s )].value > lines_dict[(self.period, self.m)].value \
            and lines_dict[(self.period, self.s )].value > lines_dict[(self.period, self.b)].value
    
    def ShouldSellLong(self, lines_dict):
        return self.ShouldShort(lines_dict)

class TraderStatus(Enum):
    IDLE = 1
    SHORT = 2
    LONG = 3

class Trader:
    def __init__(self, symbol, volume, strategy, program_start = True):
        self.status = TraderStatus.IDLE
        self.symbol = symbol
        self.volume = volume

        self.strategy = strategy
        self.program_start = program_start
        self.API = XTB(username, password)
        self.API.login()
    
    def Update(self, lines_dict):
        try:
            if self.status == TraderStatus.IDLE:
                if self.strategy.ShouldShort(lines_dict):
                    self.Short()
                elif self.strategy.ShouldLong(lines_dict):
                    self.Long()
            elif self.status == TraderStatus.SHORT:
                if self.strategy.ShouldSellShort(lines_dict):
                    self.CloseCurrent()
                    sleep(1)
            elif self.status == TraderStatus.LONG:
                if self.strategy.ShouldSellLong(lines_dict):
                    self.CloseCurrent()
                    sleep(1)
        except:
            print("EXCEPTION CAUGHT, SLEEPING 30s")
            sleep(30)

    def Short(self):
        sleep(0.5)
        self.API.login()
        self.status = TraderStatus.SHORT
        if self.program_start:
            return True

        ret = self.API.make_Trade(self.symbol, 1, 0, self.volume)
        print("SLEEPING "+ self.period + ", SHORTING")
        sleep(sleep_time_after_transaction[self.strategy.period]) # wait one candle
        return ret

    def Long(self):
        sleep(0.5)
        self.API.login()
        self.status = TraderStatus.LONG
        if self.program_start:
            return True

        ret = self.API.make_Trade(self.symbol, 0, 0, self.volume)
        print("SLEEPING "+ self.period + ", LONGING")
        sleep(sleep_time_after_transaction[self.strategy.period]) # wait one candle
        return ret

    def CloseCurrent(self):
        sleep(0.5)
        self.status = TraderStatus.IDLE
        if self.program_start:
            self.program_start = False
            return True

        self.API.login()
        current_trades = self.API.get_Trades()
        ret = []
        for trade in current_trades:
            if trade["symbol"] != self.symbol:
                continue

            self.API.login()
            ret.append(self.API.make_Trade(self.symbol, trade["cmd"], 2, self.volume, order=trade["order"]))
            sleep(0.75)
        return ret

class DebugTrader:
    def __init__(self, symbol, volume, strategy, PIPS_SIZE, PIPS_VALUE, DEBUG = False):
        self.status = TraderStatus.IDLE
        self.symbol = symbol
        self.volume = volume

        self.PIPS_SIZE = PIPS_SIZE
        self.PIPS_VALUE = PIPS_VALUE

        self.strategy = strategy
        self.program_start = True
        self.profit = 0.0

        self.DEBUG = DEBUG
    
    def Update(self, lines_dict, current_value):
        try:
            if self.status == TraderStatus.IDLE:
                if self.strategy.ShouldShort(lines_dict):
                    self.Short(current_value)
                elif self.strategy.ShouldLong(lines_dict):
                    self.Long(current_value)
            elif self.status == TraderStatus.SHORT:
                if self.strategy.ShouldSellShort(lines_dict):
                    self.CloseCurrent(current_value)
            elif self.status == TraderStatus.LONG:
                if self.strategy.ShouldSellLong(lines_dict):
                    self.CloseCurrent(current_value)

            # if self.CheckTP(current_value):
            #     self.CloseCurrent(current_value, self.status)
        except:
            print("EXCEPTION CAUGHT, SLEEPING 30s")
            sleep(30)

    def Short(self, price):
        self.status = TraderStatus.SHORT

        if self.program_start:
            return True

        if self.DEBUG:
            print("SHORTING FOR:", price)
        self.bought_for_price = price

    def Long(self, price):
        self.status = TraderStatus.LONG

        if self.program_start:
            return True

        if self.DEBUG:
            print("LONGING FOR:", price)
        self.bought_for_price = price

    def CloseCurrent(self, current_price, newStatus = TraderStatus.IDLE):
        assert(self.status != TraderStatus.IDLE)

        profit_multiplier = -1 if self.status == TraderStatus.SHORT else 1

        self.status = newStatus
        if self.program_start:
            self.program_start = False
            return True

        # if self.status == TraderStatus.LONG: # SHORTING ONLY CONFIGURATION
        #     return False
        
        if self.DEBUG:
            print("CLOSING FOR:", (current_price - self.bought_for_price) * profit_multiplier / self.PIPS_SIZE * self.PIPS_VALUE)
            print("PIPS DIFFERENCE:", (current_price - self.bought_for_price) * profit_multiplier / self.PIPS_SIZE)
        self.profit += (current_price - self.bought_for_price) * profit_multiplier / self.PIPS_SIZE * self.PIPS_VALUE