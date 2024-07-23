import numpy as np
from time import sleep
from datetime import datetime
from enum import Enum
import numpy as np
from env import username, password
from API.API import XTB

sleep_time_after_transaction = dict({
    "H1": 60*61,
    "M30": 60*31,
    "M15": 60*15,
    "M5": 60*5
})

class TraderStatus(Enum):
    IDLE = 1
    SHORT = 2
    LONG = 3

class Trader:
    def __init__(self, symbol, volume, strategy, program_start = True, Debug = False, Verbose=False, PIPS_SIZE=0.0, PIPS_VALUE=0.0, TP_PIPS=-1.0):
        self.status = TraderStatus.IDLE
        self.symbol = symbol
        self.volume = volume

        self.previous_status = TraderStatus.IDLE

        self.strategy = strategy
        self.program_start = program_start
        self.Debug = Debug
        self.Verbose = Verbose

        self.TP_PIPS = TP_PIPS
        self.PIPS_SIZE = PIPS_SIZE
        self.PIPS_VALUE = PIPS_VALUE

        self.API = XTB(username, password)
        if not Debug:
            self.API.login()
    
    def Update(self, lines_dict_sell, lines_dict_buy):
        try:
            if self.Verbose:
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
        if not self.Debug:
            sleep(0.5)
            self.API.login()
        self.status = TraderStatus.SHORT
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("SETTING STATUS SHORT ", current_time, " TIME (PROGRAM)")
        if self.program_start:
            print("Returning program start")
            return True

        ret = None
        if not self.Debug:
            ret = self.API.make_Trade(self.symbol, 1, 0, self.volume, tp_pips=self.TP_PIPS, pips_size=self.PIPS_SIZE, pips_value=self.PIPS_VALUE)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("SLEEPING "+ self.strategy.period + ", SHORTING", current_time, " TIME (PROGRAM)")
        
        if not self.Debug:
            sleep(sleep_time_after_transaction[self.strategy.period]) # wait one candle
        print("WOKE UP!")

        return ret

    def Long(self):
        if not self.Debug:
            sleep(0.5)
            self.API.login()
        self.status = TraderStatus.LONG
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("SETTING STATUS LONG ", current_time, " TIME (PROGRAM)")
        if self.program_start:
            print("Returning program start")
            return True

        ret = None
        if not self.Debug:
            ret = self.API.make_Trade(self.symbol, 0, 0, self.volume, tp_pips=self.TP_PIPS, pips_size=self.PIPS_SIZE, pips_value=self.PIPS_VALUE)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("SLEEPING "+ self.strategy.period + ", LONGING", current_time, " TIME (PROGRAM)")

        if not self.Debug:
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

        ret = []
        if not self.Debug:
            self.API.login()
            current_trades = self.API.get_Trades()
            for trade in current_trades:
                if trade["symbol"] != self.symbol:
                    continue

                self.API.login()
                ret.append(self.API.make_Trade(self.symbol, trade["cmd"], 2, trade["volume"], order=trade["order"]))
                sleep(0.75)
        return ret

class DebugTrader:
    def __init__(self, symbol, volume, strategy, PIPS_SIZE, PIPS_VALUE, DEBUG = False, take_profit_pips = -1.0, spread_pips = 0.0):
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

        self.short_loses = 0.0
        self.long_loses = 0.0

        self.num_of_trades = 0
        self.long_trades = 0
        self.short_trades = 0

        self.bought_for_price = -1.0
        self.take_profit_value = -1.0
        self.take_profit_pips = take_profit_pips
        self.spread_pips = spread_pips

        self.previous_status = TraderStatus.IDLE
        self.DEBUG = DEBUG
    
    def Update(self, lines_dict_sell, lines_dict_buy, current_value):
        try:
            if self.DEBUG:
                print("----------- PRICE: ", current_value)
            if self.status == TraderStatus.IDLE:
                if self.strategy.ShouldShort(lines_dict_buy) and (self.previous_status == TraderStatus.LONG or self.previous_status == TraderStatus.IDLE):
                    self.Short(current_value)
                elif self.strategy.ShouldLong(lines_dict_buy) and (self.previous_status == TraderStatus.SHORT or self.previous_status == TraderStatus.IDLE):
                    self.Long(current_value)
            elif self.status == TraderStatus.SHORT:
                if self.strategy.ShouldSellShort(lines_dict_sell, current_value, self.take_profit_value, self.program_start):
                    self.CloseCurrent(current_value)
            elif self.status == TraderStatus.LONG:
                if self.strategy.ShouldSellLong(lines_dict_sell, current_value, self.take_profit_value, self.program_start):
                    self.CloseCurrent(current_value)

            # if self.CheckTP(current_value):
            #     self.CloseCurrent(current_value, self.status)
        except Exception as e:
            print("EXCEPTION CAUGHT, SLEEPING 30s", e)
            sleep(30)

    def Short(self, price):
        self.status = TraderStatus.SHORT

        if self.program_start:
            return True

        direction = -1

        self.bought_for_price = price  + direction * self.PIPS_SIZE * self.spread_pips
        self.take_profit_value = (price + direction * self.take_profit_pips) if self.take_profit_pips > 0.0 else -1.0

        if self.DEBUG:
            print("SHORTING FOR:", price)
            print("TAKE PROFIT AT:", self.take_profit_value)


    def Long(self, price):
        self.status = TraderStatus.LONG

        if self.program_start:
            return True

        direction = 1

        self.bought_for_price = price + direction * self.PIPS_SIZE * self.spread_pips
        self.take_profit_value = (price + direction * self.take_profit_pips) if self.take_profit_pips > 0.0 else -1.0

        if self.DEBUG:
            print("LONGING FOR:", price)
            print("TAKE PROFIT AT:", self.take_profit_value)

    def CloseCurrent(self, current_price, newStatus = TraderStatus.IDLE):
        assert(self.status != TraderStatus.IDLE)

        profit_multiplier = -1 if self.status == TraderStatus.SHORT else 1

        self.previous_status = self.status
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
            self.short_trades += 1
            self.short_profit += current_profit
            if current_profit < 0:
                self.short_loses += current_profit
        else:
            self.long_trades += 1
            self.long_profit += current_profit
            if current_profit < 0:
                self.long_loses += current_profit


