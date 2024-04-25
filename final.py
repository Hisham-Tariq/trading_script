
import ccxt
import numpy as np
import pandas as pd
from ta import supertrend_tv,sma_tv, index_tv, CandleBodyType
import plotly.graph_objects as go
import sys
from datetime import datetime

    

TELEGRAM_BOT_TOKEN = '6763183063:AAEmPmKc18NhZcVN37CMSfkLBuOOnDeB1xE'
TELEGRAM_CHAT_ID = '-1002023135053'

# Script Variable Constants
SUP_ATR = 10 # More like min length of candles
FACTOR = 3
PLT_CHK = True
UP_COLOR = 'green'
DOWN_COLOR = 'red'

# EXCHANGE Data Constants
SYMBOL = 'BTC/USDT'
TIMEFRAME = '2h'  # You can change the timeframe as needed
CANDLE_LIMITS = 3  # Limit the number of candles fetched
EXCHANGE = ccxt.binance()

candles = EXCHANGE.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=CANDLE_LIMITS)
candles = np.array(candles)

open_s = candles[:, CandleBodyType.Open]
high = candles[:, CandleBodyType.High]
low = candles[:, CandleBodyType.Low]
close = candles[:, CandleBodyType.Close]
MIN_TICK = low[index_tv()]

def send_to_telegram(message):
    import requests
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    requests.post(url, data=data)

# Super Indicator
supr, dirc = supertrend_tv(
    candles=candles,
    atr_length=SUP_ATR,
    factor=FACTOR,
)

print(supr, dirc)
long = dirc[index_tv()] != dirc[index_tv(1)] and dirc[index_tv()] == -1
short = dirc[index_tv()] != dirc[index_tv(1)] and dirc[index_tv()] == 1 

# Converted Pine script code to python
# Pine Code
# // Function to detect triple bullish engulfing pattern
# tripleBullishEngulfing() =>
    # bullishEng1 = close[1] > open[1] and close[1] - open[1] > 2 * syminfo.mintick
    # bullishEng2 = close[2] > open[2] and close[2] - open[2] > 2 * syminfo.mintick
    # bullishEng3 = close[3] > open[3] and close[3] - open[3] > 2 * syminfo.mintick
    # bullishEng1 and bullishEng2 and bullishEng3

def triple_bullish_engulfing():
    bullish_eng_1 = close[index_tv(1)] > open_s[index_tv(1)] and close[index_tv(1)] - open_s[index_tv(1)] > 2 * MIN_TICK
    bullish_eng_2 = close[index_tv(2)] > open_s[index_tv(2)] and close[index_tv(2)] - open_s[index_tv(2)] > 2 * MIN_TICK
    bullish_eng_3 = close[index_tv(3)] > open_s[index_tv(3)] and close[index_tv(3)] - open_s[index_tv(3)] > 2 * MIN_TICK
    return bullish_eng_1 and bullish_eng_2 and bullish_eng_3 

# Converted the Pine Script Code to python
# Pine Code:
# // Function to detect bearish triple engulfing pattern
# bearishTripleEngulfing() =>
#     smallBullish1 = close[1] > open[1] and close[1] - open[1] <= 2 * syminfo.mintick
#     largeBearish2 = close[2] < open[2] and close[2] - open[2] > 2 * syminfo.mintick
#     bearishEng2 = close[2] < open[2] and close[2] - open[2] > 2 * syminfo.mintick
#     bearishEng3 = close[3] < open[3] and close[3] - open[3] > 2 * syminfo.mintick
#     smallBullish1 and largeBearish2 and bearishEng2 and bearishEng3
def triple_bearish_engulfing():
    small_bullish_1 = close[index_tv(1)] > open_s[index_tv(1)] and close[index_tv(1)] - open_s[index_tv(1)] <= 2 * MIN_TICK
    large_bearish_2 = close[index_tv(2)] < open_s[index_tv(2)] and close[index_tv(2)] - open_s[index_tv(2)] > 2 * MIN_TICK
    bearish_eng_2 = close[index_tv(2)] < open_s[index_tv(2)] and close[index_tv(2)] - open_s[index_tv(2)] > 2 * MIN_TICK
    bearish_eng_3 = close[index_tv(3)] < open_s[index_tv(3)] and close[index_tv(3)] - open_s[index_tv(3)] > 2 * MIN_TICK
    return small_bullish_1 and large_bearish_2 and bearish_eng_2 and bearish_eng_3

# Converted the Pine Script Code to Python
# Pine Code:
# // Function to check for long signal (replace with your actual long signal condition)
# longSignalCondition() =>
#     var float longSignal = na
#     longSignal := pltChk and dirc < 0 and dirc != dirc[1] ? super : na
#     longSignal := na(longSignal) ? na : longSignal

def long_signal_condition():
    long_signal = None
    if PLT_CHK and (dirc[index_tv()] < 0) and (dirc[index_tv()] != dirc[index_tv(1)]):
        long_signal = supr[index_tv()]
    return long_signal

# Converted the Pine Script Code to Python
# Pine Code:
# // Function to check for short signal (replace with your actual short signal condition)
# shortSignalCondition() =>
#     var float shortSignal = na
#     shortSignal := pltChk and dirc > 0 and dirc != dirc[1] ? super : na
#     shortSignal := na(shortSignal) ? na : shortSignal

def short_signal_condition():
    short_signal = None
    if PLT_CHK and (dirc[index_tv()] > 0) and (dirc[index_tv()] != dirc[index_tv(1)]):
        short_signal = supr[index_tv()]
    return short_signal

# Converted the Pine Script Code to Python
# Pine Code:
# // Main script logic
# tripleBullishEngulfingCondition = bool(tripleBullishEngulfing()) and bool(longSignalCondition())
# bearishTripleEngulfingCondition = bool(bearishTripleEngulfing()) and bool(shortSignalCondition())

triple_bullish_engulfing_condition = triple_bullish_engulfing() and long_signal_condition()
triple_bearish_engulfing_condition = triple_bearish_engulfing() and short_signal_condition()

# Converted the Pine Script Code to Python
# Pine Code:
# // Triple Bullish Engulfing Alert
# alertcondition(tripleBullishEngulfingCondition, title="Triple Bullish Engulfing Alert", message="Triple Bullish Engulfing pattern detected within 15 candles of long signal")
# // Bearish Triple Engulfing Alert
# alertcondition(bearishTripleEngulfingCondition, title="Bearish Triple Engulfing Alert", message="Bearish Triple Engulfing pattern detected within 15 candles of short signal")
input("wait")
if triple_bullish_engulfing_condition:
    send_to_telegram("Triple Bullish Engulfing Alert: Triple Bullish Engulfing pattern detected within 15 candles of long signal")
elif triple_bearish_engulfing_condition:
    send_to_telegram("Bearish Triple Engulfing Alert: Bearish Triple Engulfing pattern detected within 15 candles of short signal")
else:
    send_to_telegram("Nothing to do")
