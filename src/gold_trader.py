from trader_runner.trader_runner import RunTrader

smallest_period = 9
middle_period = 13
biggest_period = 13


SYMBOL = "GOLD"
VOLUME = 0.07
PERIOD = "M30"


RunTrader(SYMBOL, PERIOD, VOLUME, smallest_period, middle_period, biggest_period)
