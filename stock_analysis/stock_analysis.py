import ccxt
import numpy as np
from ta import CandleBodyType, index_tv


class StockAnalysis:
    
    def __init__(self, symbol, timeframe, candle_limits, **kwargs) -> None:
        self.symbol = symbol
        self.timeframe = timeframe  # You can change the timeframe as needed
        self.candle_limits = candle_limits  # Limit the number of candles fetched
        self.exchange = ccxt.binance()
        self.open = None
        self.close = None
        self.high = None
        self.low = None
    
    def __fetch_candles(self) -> np.array:
        candles = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=self.candle_limits)
        candles = np.array(candles)
        self.open = candles[:, CandleBodyType.Open]
        self.high = candles[:, CandleBodyType.High]
        self.low = candles[:, CandleBodyType.Low]
        self.close = candles[:, CandleBodyType.Close]
        return candles
    

    def __is_bueng(self):
        return self.open[index_tv(3)] > self.close[index_tv(3)] and self.open[index_tv(2)] > self.close[index_tv(2)] and self.open[index_tv(1)] > self.close[index_tv(1)] and self.close[index_tv()] > self.open[index_tv()] and (self.close[index_tv] >= self.open[index_tv(1)] or self.close[index_tv(1)] >= self.open[index_tv()]) and self.close[index_tv] - self.open[index_tv()] > self.open[index_tv(1)] - self.close[index_tv(1)]
    
    def __is_beeng(self):
        return self.open[index_tv(3)] < self.close[index_tv(3)] and self.open[index_tv(2)] < self.close[index_tv(2)] and self.close[index_tv(1)] > self.open[index_tv(1)] and self.open[index_tv()] > self.close[index_tv()] and (self.open[index_tv()] >= self.close[index_tv(1)] or self.open[index_tv(1)] >= self.close[index_tv()]) and self.open[index_tv()] - self.close[index_tv()] > self.close[index_tv(1)] - self.open[index_tv(1)]
    
    def analyze(self):
        self.__fetch_candles()
        if self.__is_bueng():
            return 'bueng'
        elif self.__is_beeng():
            return 'beeng'
        else:
            return 'none'
