import ccxt
import numpy as np
from ta import CandleBodyType, index_tv


class StockAnalysis:
    
    def __init__(self, symbol, timeframe, candle_limits, **kwargs) -> None:
        self.symbol = symbol
        self.timeframe = timeframe  # You can change the timeframe as needed
        self.candle_limits = candle_limits  # Limit the number of candles fetched
        self.exchange = ccxt.binance()
        self.candles = None
        self.open = None
        self.close = None
        self.high = None
        self.low = None
    
    def __fetch_candles(self) -> np.array:
        candles = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=self.candle_limits)
        candles = np.array(candles)
        self.open = candles[:, CandleBodyType.Open][::-1]
        self.high = candles[:, CandleBodyType.High][::-1]
        self.low = candles[:, CandleBodyType.Low][::-1]
        self.close = candles[:, CandleBodyType.Close][::-1]
        self.candles = candles
        return candles

    def records_history(self):
        return self.candles
    

    def __is_bueng(self):
        return self.open[3] > self.close[3] and self.open[2] > self.close[2] and self.open[1] > self.close[1] and self.close[0] > self.open[0] and (self.close[0] >= self.open[1] or self.close[1] >= self.open[0]) and self.close[0] - self.open[0] > self.open[1] - self.close[1]
    
    def __is_beeng(self):
        return self.open[3] < self.close[3] and self.open[2] < self.close[2] and self.close[1] > self.open[1] and self.open[0] > self.close[0] and (self.open[0] >= self.close[1] or self.open[1] >= self.close[0]) and self.open[0] - self.close[0] > self.close[1] - self.open[1]
    
    def analyze(self):
        self.__fetch_candles()
        if self.__is_bueng():
            return 'bueng'
        elif self.__is_beeng():
            return 'beeng'
        else:
            return 'none'
