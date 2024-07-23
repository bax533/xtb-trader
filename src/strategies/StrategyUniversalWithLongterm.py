import StrategyAbstract

class StrategyUniversalWithLongterm(StrategyAbstract):
    def __init__(self, period):
        self.period = period

    def ShouldShort(self, lines_dict):
        return lines_dict["s"].value < lines_dict["m"].value \
            and lines_dict["s"].value < lines_dict["b"].value \
            and lines_dict["longterm_s"].value < lines_dict["longterm_m"].value

    def ShouldSellShort(self, lines_dict, current_value = 999999999.9, take_profit_value = -1.0, program_start = True):
        return lines_dict["s"].value < lines_dict["m"].value \
            and lines_dict["s"].value < lines_dict["b"].value

    def ShouldLong(self, lines_dict):
        return lines_dict["s"].value > lines_dict["m"].value \
            and lines_dict["s"].value > lines_dict["b"].value \
            and lines_dict["longterm_s"].value > lines_dict["longterm_m"].value

    
    def ShouldSellLong(self, lines_dict, current_value = -999999999.9, take_profit_value = -1.0, program_start = True):
        return lines_dict["s"].value > lines_dict["m"].value \
            and lines_dict["s"].value > lines_dict["b"].value