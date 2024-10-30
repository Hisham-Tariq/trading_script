import ccxt
import numpy as np
from ta import CandleBodyType, index_tv, supertrend_tv


class StockAnalysis:
    
    def __init__(self, symbol, timeframe, candle_limits, **kwargs) -> None:
        self.symbol = symbol
        self.timeframe = timeframe  # You can change the timeframe as needed
        self.candle_limits = candle_limits + 1  # Limit the number of candles fetched
        self.exchange = ccxt.binance()
        self.candles = None
        self.open = None
        self.close = None
        self.high = None
        self.low = None
        self.MIN_TICK = kwargs.get('MIN_TICK', 0.1)
        self.PLT_CHK = kwargs.get('PLT_CHK', True)
        self.SUP_ATR = kwargs.get('SUP_ATR', 10)
        self.FACTOR = kwargs.get('FACTOR', 3)
    
    def __fetch_candles(self) -> np.array:
        candles = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=self.candle_limits)
        # remove the last/active candle
        candles = candles[:-1]
        candles = np.array(candles)
        supr, dirc = supertrend_tv(
            candles=candles,
            atr_length=self.SUP_ATR,
            factor=self.FACTOR,
        )
        self.super = supr[:-1]
        self.dirc = dirc[:-1]
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
    
    
    def tripleBullishEngulfing(self):
        bullishEng1 = self.close[1] > self.open[1] and self.close[1] - self.open[1] > 2 * self.MIN_TICK
        bullishEng2 = self.close[2] > self.open[2] and self.close[2] - self.open[2] > 2 * self.MIN_TICK
        bullishEng3 = self.close[3] > self.open[3] and self.close[3] - self.open[3] > 2 * self.MIN_TICK
        return bullishEng1 and bullishEng2 and bullishEng3


    def bearishTripleEngulfing(self):
        smallBullish1 = self.close[1] > self.open[1] and self.close[1] - self.open[1] <= 2 * self.MIN_TICK
        largeBearish2 = self.close[2] < self.open[2] and self.close[2] - self.open[2] > 2 * self.MIN_TICK
        bearishEng2 = self.close[2] < self.open[2] and self.close[2] - self.open[2] > 2 * self.MIN_TICK
        bearishEng3 = self.close[3] < self.open[3] and self.close[3] - self.open[3] > 2 * self.MIN_TICK
        return smallBullish1 and largeBearish2 and bearishEng2 and bearishEng3
        

    def longSignalCondition(self):
        longSignal = None
        if self.PLT_CHK and (self.dirc[0] < 0) and (self.dirc[0] != self.dirc[1]):
            longSignal = self.super[0]
        return longSignal

    def shortSignalCondition(self):
        shortSignal = None
        if self.PLT_CHK and (self.dirc[0] > 0) and (self.dirc[0] != self.dirc[1]):
            shortSignal = self.super[0]
        return shortSignal
    
    def analyze(self):
        self.__fetch_candles()
        tripleBullishEngulfingCondition = self.tripleBullishEngulfing() and bool(self.longSignalCondition())
        bearishTripleEngulfingCondition = self.bearishTripleEngulfing() and bool(self.shortSignalCondition())
        
        if tripleBullishEngulfingCondition:
            return 'Triple Bullish Engulfing Alert'
        elif bearishTripleEngulfingCondition:
            return 'Triple Bearish Engulfing Alert'
        elif self.__is_bueng():
            return 'bullish engulfing (Bueng)'
        elif self.__is_beeng():
            return 'bearish engulfing (Beeng)'
        else:
            return None
