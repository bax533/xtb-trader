import numpy as np
from utils.utils import ewma_linear_filter

class MACD_Line:
    def __init__(self, fast_ema, slow_ema, signal_ema):
        self.macd_value = 99999999999.0
        self.signal_value = 99999999999.0

        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.signal_ema = signal_ema

    def _CalculateMacdValue(self, closing_values):
        return ewma_linear_filter(np.array(closing_values), self.fast_ema)[-1] - \
                    ewma_linear_filter(np.array(closing_values), self.slow_ema)[-1]

    def UpdateValue(self, candles, divider):
        assert(len(candles) > self.slow_ema + self.signal_ema)
        closing_values = [(candle["open"] + candle["close"])/divider for candle in candles]
        self.macd_value = self._CalculateMacdValue(closing_values)

        last_macd_values = [self._CalculateMacdValue(closing_values[len(closing_values) - self.slow_ema - i : len(closing_values) - i ]) \
                                for i in range(self.signal_ema, -1, -1)]
        self.signal_value = ewma_linear_filter(np.array(last_macd_values), self.signal_ema)[-1]