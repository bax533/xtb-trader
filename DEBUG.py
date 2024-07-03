

strat = StrategyM5()
trader = Trader("DE40", 0.04, strat)

def DEBUG():
    import matplotlib
    import matplotlib.pyplot as plt

    num_of_candles = 40

    candles = API.get_Candles("M15", "DE40", qty_candles=num_of_candles)[1:]
    closing_values = [candle["open"] + candle["close"] for candle in candles]

    start_it=20

    emas_5 = ewma_linear_filter(np.array(closing_values), smallest_period)[start_it:]
    emas_8 = ewma_linear_filter(np.array(closing_values), middle_period)[start_it:]
    emas_15 = ewma_linear_filter(np.array(closing_values), biggest_period)[start_it:]

    plt.plot([i for i in range(num_of_candles-start_it)], closing_values[start_it:], color='black')
    plt.plot([i for i in range(num_of_candles-start_it)], emas_5, color='cyan')
    plt.plot([i for i in range(num_of_candles-start_it)], emas_8, color='blue')
    plt.plot([i for i in range(num_of_candles-start_it)], emas_15, color='green')
    plt.plot([i for i in range(num_of_candles-start_it)], emas_20, color='red')

    for i in range(len(emas_5)):
        plt.scatter([i], [
            closing_values[start_it + i]
        ], color='magenta' if strat.ShouldShort_M_debug(emas_5[i], emas_8[i], emas_15[i], emas_20[i]) else \
            ('yellow' if strat.ShouldLong_M_debug(emas_5[i], emas_8[i], emas_15[i], emas_20[i]) else 'black'))

    plt.show()

DEBUG()