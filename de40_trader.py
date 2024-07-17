from trader_runner import RunTrader

smallest_period, middle_period, biggest_period = (6, 16, 18)

SYMBOL = "DE40"
VOLUME = 0.03
PERIOD = "M30"

RunTrader(SYMBOL, PERIOD, VOLUME, smallest_period, middle_period, biggest_period)
