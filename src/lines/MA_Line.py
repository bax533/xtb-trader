import numpy as np
from utils.utils import ewma_linear_filter

class MA_Line:
    def __init__(self, ema_period):
        self.value = 99999999999.0
        self.ema_period = ema_period

    def _CalculateValue(self, closing_values):
        return ewma_linear_filter(np.array(closing_values), self.ema_period)[-1]

    def UpdateValue(self, candles, divider):
        closing_values = [(candle["open"] + candle["close"])/divider for candle in candles]
        self.value = self._CalculateValue(closing_values)