import ccxt
import numpy as np
import pandas as pd
from ta import supertrend_tv,sma_tv, index_tv, CandleBodyType
import plotly.graph_objects as go
import sys
from datetime import datetime

# Script Variable Constants
SUP_ATR = 10 # More like min length of candles
FACTOR = 3.0
PLT_CHK = True
UP_COLOR = 'green'
DOWN_COLOR = 'red'

# EXCHANGE Data Constants
SYMBOL = 'BTC/USDT'
TIMEFRAME = '2h'  # You can change the timeframe as needed
CANDLE_LIMITS = 100 # Limit the number of candles fetched
EXCHANGE = ccxt.binance()

candles = EXCHANGE.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=CANDLE_LIMITS)
candles = np.array(candles)
df = pd.DataFrame(candles, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
sma = sma_tv(df['Close'].to_numpy(), 10)
fig = go.Figure(data=[
    go.Candlestick(
        x=df['Timestamp'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    ),
    go.Scatter(
        x=df['Timestamp'],
        y=sma,
        mode='lines',
        name='SMA'
    )    
])




# sys.exit()
# empty numpy array

def triple_bullish_engulfing(close, open_s, MIN_TICK):
    bullish_eng_1 = close[1] > open_s[1] and close[1] - open_s[1] > 2 * MIN_TICK
    bullish_eng_2 = close[2] > open_s[2] and close[2] - open_s[2] > 2 * MIN_TICK
    bullish_eng_3 = close[3] > open_s[3] and close[3] - open_s[3] > 2 * MIN_TICK
    return bullish_eng_1 and bullish_eng_2 and bullish_eng_3

def triple_bearish_engulfing(close, open_s, MIN_TICK):
    small_bullish_1 = close[1] > open_s[1] and close[1] - open_s[1] <= 2 * MIN_TICK
    large_bearish_2 = close[2] < open_s[2] and close[2] - open_s[2] > 2 * MIN_TICK
    bearish_eng_2 = close[2] < open_s[2] and close[2] - open_s[2] > 2 * MIN_TICK
    bearish_eng_3 = close[3] < open_s[3] and close[3] - open_s[3] > 2 * MIN_TICK
    return small_bullish_1 and large_bearish_2 and bearish_eng_2 and bearish_eng_3


def long_signal_condition(dirc, supr):
    long_signal = None
    if PLT_CHK and (dirc[0] < 0) and (dirc[0] != dirc[1]):
        long_signal = supr[0]
    return long_signal

def short_signal_condition(dirc, supr):
    short_signal = None
    if PLT_CHK and (dirc[0] > 0) and (dirc[0] != dirc[1]):
        short_signal = supr[0]
    return short_signal

record_history = np.empty((0, 6))
def draw_indicator(sources):
    open_s = sources[:, CandleBodyType.Open]
    high = sources[:, CandleBodyType.High]
    low = sources[:, CandleBodyType.Low]
    close = sources[:, CandleBodyType.Close]
    MIN_TICK = low[0]

    # supr, dirc = supertrend_tv(
    #     candles=sources,
    #     atr_length=SUP_ATR,
    #     factor=FACTOR,
    # )

    # long = dirc[0] != dirc[1] and dirc[0] == -1
    # short = dirc[0] != dirc[1] and dirc[0] == 1 

    # triple_bullish_engulfing_condition = triple_bullish_engulfing(close, open_s, MIN_TICK) and long_signal_condition(dirc, supr)
    # triple_bearish_engulfing_condition = triple_bearish_engulfing(close, open_s, MIN_TICK) and short_signal_condition(dirc, supr)

    Bueng = open_s[3] > close[3] and open_s[2] > close[2] and open_s[1] > close[1] and close[0] > open_s[0] and (close[0] >= open_s[1] or close[1] >= open_s[0]) and close[0] - open_s[0] > open_s[1] - close[1]

    # // bearish engulfing (Beeng)
    Beeng = open_s[3] < close[3] and open_s[2] < close[2] and close[1] > open_s[1] and open_s[0] > close[0] and (open_s[0] >= close[1] or open_s[1] >= close[0]) and open_s[0] - close[0] > close[1] - open_s[1]
    if Bueng:
        return "green"
    elif Beeng:
        return "red"
    else:
        return np.nan

indicators = []

for record in candles:

    record_history = np.insert(record_history, 0, np.array([record]), axis=0)
    res = np.nan
    try:
        res = draw_indicator(record_history)
        # if res is green then get the high value of current and add 400 to it for drawing indicator
    except Exception as e:
        res = np.nan
    if res not in [np.nan]:
        if res == 'green':       
            indicators.append([record[0],record[3] - 400 ,  res])
        else:
            indicators.append([record[0],record[2] + 400 ,  res])
    # if res == 'green':
    #     print("drawing green indicator")
    #     fig.add_annotation(x=current_datetime, y=record[CandleBodyType.Close]+20, text="▲", showarrow=False, font=dict(size=16, color='LightSeaGreen'))
    # elif res == 'red':
    #     print("drawing red indicator")
    #     fig.add_annotation(x=current_datetime, y=record[CandleBodyType.Close]-20, text="▼", showarrow=False, font=dict(size=16, color='red'))

indicators = np.array(indicators)

indicators_df = pd.DataFrame(indicators, columns=['Timestamp', 'Price', 'Color'])
indicators_df['Timestamp'] = pd.to_datetime(indicators_df['Timestamp'], unit='ms')

for record in indicators_df.to_numpy():
    if record[2] == 'green':
        fig.add_annotation(x=record[0], y=record[1], text="▲", showarrow=False, font=dict(size=16, color='LightSeaGreen'))
    elif record[2] == 'red':
        fig.add_annotation(x=record[0], y=record[1], text="▼", showarrow=False, font=dict(size=16, color='red'))

fig.show()