from abc import ABC, abstractmethod

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