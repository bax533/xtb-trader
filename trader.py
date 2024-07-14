import numpy as np
from time import sleep
from datetime import datetime
from enum import Enum
import numpy as np
from scipy.signal import lfiltic, lfilter
from env import username, password, demo_username, demo_password
from API import XTB, _DEMO
from abc import ABC, abstractmethod

sleep_time_after_transaction = dict({
    "H1": 60*61,
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


class MA_Line:
    def __init__(self, symbol: str, chart_period: str, ema_period: int, candle_behind: bool = False):
        self.line_above = None
        self.line_under = None
        self.previous_above = None
        self.previous_under = None
        self.value = 99999999999.0
        self.candle_behind = candle_behind

        self.symbol = symbol
        self.chart_period = chart_period
        self.ema_period = ema_period

        if _DEMO:
            username = demo_username
            password = demo_password

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
            candles = self.API.get_Candles(self.chart_period, self.symbol, qty_candles=30)[1:]
            closing_values = []

            #print("LAST CANDLE VALUE: ", [(candle["open"] + candle["close"]) * multiplier for candle in candles][-1], " PREVIOUS CANDLE VALUE:", [(candle["open"] + candle["close"]) * multiplier for candle in candles][-2])

            if self.candle_behind:
                closing_values = [(candle["open"] + candle["close"]) * multiplier for candle in candles][:-1] # WITHOUT CURRENT CANDLE
            else:
                closing_values = [(candle["open"] + candle["close"]) * multiplier for candle in candles]


            self.value = ewma_linear_filter(np.array(closing_values), self.ema_period)[-1]
        except Exception as e:
            print("could not get candles", self.chart_period, self.ema_period, self.symbol, datetime.now())
            print("exception: ", e)
            return

    def UpdateValueDebug(self, candles, divider):
        closing_values = [(candle["open"] + candle["close"])/divider for candle in candles]
        self.value = ewma_linear_filter(np.array(closing_values), self.ema_period)[-1]

    def GetName(self):
        return self.symbol + ", " + self.chart_period + ", " + str(self.ema_period)

    def __eq__(self, other):
        return self.symbol == other.symbol and self.chart_period == other.chart_period and self.ema_period == other.ema_period

class SIGNAL_Line:
    def __init__(self, symbol: str, chart_period: str, ema_period_s: int, ema_period_m: int, ema_period_signal):
        self.line_above = None
        self.line_under = None
        self.previous_above = None
        self.previous_under = None
        self.value = 99999999999.0

        self.symbol = symbol
        self.chart_period = chart_period
        self.ema_period_s = ema_period_s
        self.ema_period_m = ema_period_m
        self.ema_period_signal = ema_period_signal

        if _DEMO:
            username = demo_username
            password = demo_password

        self.API = XTB(username, password)
        self.API.login()
    
    def UpdateValue(self, multiplier = 1.0):
        sleep(0.5)
        self.API.login()
        sleep(0.5)
        try:
            candles = self.API.get_Candles(self.chart_period, self.symbol, qty_candles=40)[1:]
            closing_values = [(candle["open"] + candle["close"]) * multiplier for candle in candles]

            emas_s = [ewma_linear_filter(np.array(closing_values[i: i + 30]), self.ema_period_s)[-1] for i in range(qty_candles - 30)]
            emas_m = [ewma_linear_filter(np.array(closing_values)[i: i + 30], self.ema_period_s)[-1] for i in range(qty_candles - 30)]

            emas_signal = [m - s for m, s in zip(emas_m, emas_s)]

            self.value = ewma_linear_filter(np.array(emas_signal), self.ema_period_signal)
        except:
            print("could not get candles", datetime.now())
            return

    def UpdateValueDebug(self, candles, divider):
        closing_values = [(candle["open"] + candle["close"])/divider for candle in candles]
        emas_s = [ewma_linear_filter(np.array(closing_values[i: i + 30]), self.ema_period_s)[-1] for i in range(len(candles) - 30)]
        emas_m = [ewma_linear_filter(np.array(closing_values)[i: i + 30], self.ema_period_s)[-1] for i in range(len(candles) - 30)]

        emas_signal = [m - s for m, s in zip(emas_m, emas_s)]

        self.value = ewma_linear_filter(np.array(emas_signal), self.ema_period_signal)

    def GetName(self):
        return self.symbol + ", " + self.chart_period + ", " + str(self.ema_period_signal)

    def __eq__(self, other):
        return self.symbol == other.symbol and self.chart_period == other.chart_period and self.ema_period_s == other.ema_period_s and self.ema_period_m == other.ema_period_m and self.ema_period_signal == other.ema_period_signal

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
    def __init__(self, symbol, volume, strategy, program_start = True, Debug = False):
        self.status = TraderStatus.IDLE
        self.symbol = symbol
        self.volume = volume

        self.previous_status = TraderStatus.IDLE

        self.strategy = strategy
        self.program_start = program_start
        self.Debug = Debug

        self.API = XTB(username, password)
        self.API.login()
    
    def Update(self, lines_dict_sell, lines_dict_buy):
        try:
            if self.Debug:
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print(self.previous_status, self.status, " - PREVIOUS  CURRENT", current_time, " TIME (PROGRAM)")
                print(self.strategy.ShouldShort(lines_dict_buy), self.strategy.ShouldLong(lines_dict_buy), " - SHOULD SHORT, SHOULD LONG  (BUY)", current_time, " TIME (PROGRAM)")
                print(self.strategy.ShouldShort(lines_dict_sell), self.strategy.ShouldLong(lines_dict_sell), " - SHOULD SHORT, SHOULD LONG  (SELL)", current_time, " TIME (PROGRAM)")
            if self.status == TraderStatus.IDLE:
                if self.strategy.ShouldShort(lines_dict_buy) and (self.previous_status == TraderStatus.LONG or self.previous_status == TraderStatus.IDLE):
                    self.Short()
                elif self.strategy.ShouldLong(lines_dict_buy) and (self.previous_status == TraderStatus.SHORT or self.previous_status == TraderStatus.IDLE):
                    self.Long()
            elif self.status == TraderStatus.SHORT:
                if self.strategy.ShouldSellShort(lines_dict_sell):
                    self.CloseCurrent()
                    sleep(1)
            elif self.status == TraderStatus.LONG:
                if self.strategy.ShouldSellLong(lines_dict_sell):
                    self.CloseCurrent()
                    sleep(1)
        except Exception as e:
            print("EXCEPTION CAUGHT, SLEEPING 10s", e)
            sleep(10)

    def Short(self):
        sleep(0.5)
        self.API.login()
        self.status = TraderStatus.SHORT
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("SETTING STATUS SHORT ", current_time, " TIME (PROGRAM)")
        if self.program_start:
            print("Returning program start")
            return True

        ret = self.API.make_Trade(self.symbol, 1, 0, self.volume)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("SLEEPING "+ self.strategy.period + ", SHORTING", current_time, " TIME (PROGRAM)")
        sleep(sleep_time_after_transaction[self.strategy.period]) # wait one candle
        print("WOKE UP!")
        return ret

    def Long(self):
        sleep(0.5)
        self.API.login()
        self.status = TraderStatus.LONG
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("SETTING STATUS LONG ", current_time, " TIME (PROGRAM)")
        if self.program_start:
            print("Returning program start")
            return True

        ret = self.API.make_Trade(self.symbol, 0, 0, self.volume)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("SLEEPING "+ self.strategy.period + ", LONGING", current_time, " TIME (PROGRAM)")
        sleep(sleep_time_after_transaction[self.strategy.period]) # wait one candle
        print("WOKE UP!")
        return ret

    def CloseCurrent(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("CLOSING CURRENT", current_time, " TIME (PROGRAM)")
        sleep(0.5)
        self.previous_status = self.status
        self.status = TraderStatus.IDLE
        if self.program_start:
            self.program_start = False

        self.API.login()
        current_trades = self.API.get_Trades()
        ret = []
        for trade in current_trades:
            if trade["symbol"] != self.symbol:
                continue

            self.API.login()
            ret.append(self.API.make_Trade(self.symbol, trade["cmd"], 2, trade["volume"], order=trade["order"]))
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
        self.short_profit = 0.0
        self.long_profit = 0.0

        self.num_of_trades = 0

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
        
        if self.DEBUG:
            print("CLOSING FOR:", (current_price - self.bought_for_price) * profit_multiplier / self.PIPS_SIZE * self.PIPS_VALUE)
            print("PIPS DIFFERENCE:", (current_price - self.bought_for_price) * profit_multiplier / self.PIPS_SIZE)
        
        current_profit = (current_price - self.bought_for_price) * profit_multiplier / self.PIPS_SIZE * self.PIPS_VALUE

        self.profit += current_profit
        self.num_of_trades += 1
        if profit_multiplier == -1:
            self.short_profit += current_profit
        else:
            self.long_profit += current_profit


