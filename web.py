from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.io import to_html
import ccxt
from ta import CandleBodyType, sma_tv
import plotly.graph_objects as go

app = FastAPI()  # Create a FastAPI instance
SYMBOL = 'BTC/USDT'
TIMEFRAME = '2h'  # You can change the timeframe as needed
CANDLE_LIMITS = 100 # Limit the number of candles fetched
EXCHANGE = ccxt.binance()


record_history = np.empty((0, 6))
def draw_indicator(sources):
    open_s = sources[:, CandleBodyType.Open]
    close = sources[:, CandleBodyType.Close]
    Bueng = open_s[3] > close[3] and open_s[2] > close[2] and open_s[1] > close[1] and close[0] > open_s[0] and (close[0] >= open_s[1] or close[1] >= open_s[0]) and close[0] - open_s[0] > open_s[1] - close[1]
    # // bearish engulfing (Beeng)
    Beeng = open_s[3] < close[3] and open_s[2] < close[2] and close[1] > open_s[1] and open_s[0] > close[0] and (open_s[0] >= close[1] or open_s[1] >= close[0]) and open_s[0] - close[0] > close[1] - open_s[1]
    if Bueng:
        return "green"
    elif Beeng:
        return "red"
    else:
        return np.nan
    
def process_candlesticks(candles):
    record_history = np.empty((0, 6))
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
    return indicators


# @app.get("/")
# async def root():
#     return {"message": "Welcome to the Titanic API, we are learning on codanics.com"}




@app.get("/", response_class=HTMLResponse)
async def survival_rate_plotly():
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

    indicators = process_candlesticks(candles)


    indicators = np.array(indicators)

    indicators_df = pd.DataFrame(indicators, columns=['Timestamp', 'Price', 'Color'])
    indicators_df['Timestamp'] = pd.to_datetime(indicators_df['Timestamp'], unit='ms')

    for record in indicators_df.to_numpy():
        if record[2] == 'green':
            fig.add_annotation(x=record[0], y=record[1], text="▲", showarrow=False, font=dict(size=16, color='LightSeaGreen'))
        elif record[2] == 'red':
            fig.add_annotation(x=record[0], y=record[1], text="▼", showarrow=False, font=dict(size=16, color='red'))

    
    # Convert the plot to HTML
    plot_div = to_html(fig, full_html=False)
    
    # Create the full HTML document
    html_content = f"""
    <html>
        <head>
            <title>CandleStick (BTC/USDT)</title>
        </head>
        <body>
            {plot_div}
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
