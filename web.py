from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.io import to_html
import ccxt
from ta import CandleBodyType, sma_tv, supertrend_tv
import plotly.graph_objects as go

app = FastAPI(root_path="/trading")  # Create a FastAPI instance
SYMBOL = 'ETH/USDT'
TIMEFRAME = '5m'  # You can change the timeframe as needed
CANDLE_LIMITS = 50 # Limit the number of candles fetched
EXCHANGE = ccxt.binance()
SUP_ATR = 5 # More like min length of candles
FACTOR = 3
PLT_CHK = True

record_history = np.empty((0, 6))
def draw_indicator(sources):
    supr, dirc = supertrend_tv(
        candles=sources,
        atr_length=SUP_ATR,
        factor=FACTOR,
    )
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

# // Function to detect triple bullish engulfing pattern
# tripleBullishEngulfing() =>
# bullishEng1 = close[1] > open[1] and close[1] - open[1] > 2 * syminfo.mintick
#     bullishEng2 = close[2] > open[2] and close[2] - open[2] > 2 * syminfo.mintick
#     bullishEng3 = close[3] > open[3] and close[3] - open[3] > 2 * syminfo.mintick
#     bullishEng1 and bullishEng2 and bullishEng3
def tripleBullishEngulfing(candles):
    close = candles[:, CandleBodyType.Close]
    open_s = candles[:, CandleBodyType.Open]
    MIN_TICK = 0.1
    bullishEng1 = close[1] > open_s[1] and close[1] - open_s[1] > 2 * MIN_TICK
    bullishEng2 = close[2] > open_s[2] and close[2] - open_s[2] > 2 * MIN_TICK
    bullishEng3 = close[3] > open_s[3] and close[3] - open_s[3] > 2 * MIN_TICK
    return bullishEng1 and bullishEng2 and bullishEng3

# // Function to detect bearish triple engulfing pattern
# bearishTripleEngulfing() =>
#     smallBullish1 = close[1] > open[1] and close[1] - open[1] <= 2 * syminfo.mintick
#     largeBearish2 = close[2] < open[2] and close[2] - open[2] > 2 * syminfo.mintick
#     bearishEng2 = close[2] < open[2] and close[2] - open[2] > 2 * syminfo.mintick
#     bearishEng3 = close[3] < open[3] and close[3] - open[3] > 2 * syminfo.mintick
    
#     smallBullish1 and largeBearish2 and bearishEng2 and bearishEng3

def bearishTripleEngulfing(candles):
    close = candles[:, CandleBodyType.Close]
    open_s = candles[:, CandleBodyType.Open]
    MIN_TICK = 0.1
    smallBullish1 = close[1] > open_s[1] and close[1] - open_s[1] <= 2 * MIN_TICK
    largeBearish2 = close[2] < open_s[2] and close[2] - open_s[2] > 2 * MIN_TICK
    bearishEng2 = close[2] < open_s[2] and close[2] - open_s[2] > 2 * MIN_TICK
    bearishEng3 = close[3] < open_s[3] and close[3] - open_s[3] > 2 * MIN_TICK
    return smallBullish1 and largeBearish2 and bearishEng2 and bearishEng3
    

# // Function to check for long signal (replace with your actual long signal condition)
# longSignalCondition() =>
#     var float longSignal = na
#     longSignal := pltChk and dirc < 0 and dirc != dirc[1] ? super : na
#     longSignal := na(longSignal) ? na : longSignal    

def longSignalCondition(dirc, supr):
    longSignal = None
    if PLT_CHK and (dirc[0] < 0) and (dirc[0] != dirc[1]):
        longSignal = supr[0]
    return longSignal

# // Function to check for short signal (replace with your actual short signal condition)
# shortSignalCondition() =>
#     var float shortSignal = na
#     shortSignal := pltChk and dirc > 0 and dirc != dirc[1] ? super : na
#     shortSignal := na(shortSignal) ? na : shortSignal

def shortSignalCondition(dirc, supr):
    shortSignal = None
    if PLT_CHK and (dirc[0] > 0) and (dirc[0] != dirc[1]):
        shortSignal = supr[0]
    return shortSignal


def process_candlesticks(candles):
    record_history = np.empty((0, 6))
    indicators = []
    triple_engulfing = []

    def update_indicator(record):
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
    
    def check_triple_engulfing_condition(record):
        try:
            reverse_history = record_history[::-1]
            supr, dirc = supertrend_tv(
                candles=reverse_history,
                atr_length=SUP_ATR,
                factor=FACTOR,
            )
            supr = supr[::-1]
            dirc = dirc[::-1]
            tripleBullishEngulfingCondition = tripleBullishEngulfing(record_history) and bool(longSignalCondition(dirc, supr))
            bearishTripleEngulfingCondition = bearishTripleEngulfing(record_history) and bool(shortSignalCondition(dirc, supr))
            if tripleBullishEngulfingCondition:
                triple_engulfing.append([record[0],record[3] - 600, 'tripleBullishEngulfing'])
            elif bearishTripleEngulfingCondition:
                triple_engulfing.append([record[0],record[3] - 600,'bearishTripleEngulfing'])
            # else:
            #     triple_engulfing.append(np.nan)
        except:
            pass
            # triple_engulfing.append(np.nan)


    for i, record in enumerate(candles):
        record_history = np.insert(record_history, 0, np.array([record]), axis=0)
        update_indicator(record)
        check_triple_engulfing_condition(record)

    return indicators, triple_engulfing


# @app.get("/")
# async def root():
#     return {"message": "Welcome to the Titanic API, we are learning on codanics.com"}



@app.get("/trading/send_message")
async def send_to_telegram():
    import requests
    url = 'https://api.telegram.org/bot7099206933:AAHaxBbWnppc1OnCULvRuS-b7t0Exa0gZec/sendMessage'
    data = {
        'chat_id': '-4128390434',
        'text': "Sending From Server"
    }
    res = requests.post(url, data=data)
    return res.json()


@app.get("/trading/ETH-USDT", response_class=HTMLResponse)
@app.get("/trading/BTC-USDT", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
async def survival_rate_plotly(request: Request):
    # check if path is / or /ETH-USDT or /BTC-USDT
    if request.url.path == '/' or request.url.path == '/BTC-USDT':
        SYMBOL = 'BTC/USDT'
    else:
        SYMBOL = 'ETH/USDT'
    candles = EXCHANGE.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=CANDLE_LIMITS)
    candles = np.array(candles)
    # supr, dirc = supertrend_tv(
    #     candles=candles,
    #     atr_length=SUP_ATR,
    #     factor=FACTOR,
    # )

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
        ),
        # go.Scatter(
        #     x=df['Timestamp'],
        #     y=supr,
        #     mode='lines',
        #     name='SuperTrend',
        #     line=dict(color='purple', width=1)
        # ),
        # go.Scatter(
        #     x=df['Timestamp'],
        #     y=dirc,
        #     mode='lines',
        #     name='Direction',
        #     line=dict(color='black', width=1)
        # )

    ])

    indicators, triple_engulfing = process_candlesticks(candles)


    indicators = np.array(indicators)

    indicators_df = pd.DataFrame(indicators, columns=['Timestamp', 'Price', 'Color'])
    indicators_df['Timestamp'] = pd.to_datetime(indicators_df['Timestamp'], unit='ms')
    

    for record in indicators_df.to_numpy():
        if record[2] == 'green':
            fig.add_annotation(x=record[0], y=record[1], text="▲", showarrow=False, font=dict(size=16, color='LightSeaGreen'))
        elif record[2] == 'red':
            fig.add_annotation(x=record[0], y=record[1], text="▼", showarrow=False, font=dict(size=16, color='red'))
    print(triple_engulfing)

    if len(triple_engulfing) != 0:
        triple_engulfing = np.array(triple_engulfing)
        triple_engulfing_df = pd.DataFrame(triple_engulfing, columns=['Timestamp', 'Price', 'Pattern'])
        triple_engulfing_df['Timestamp'] = pd.to_datetime(triple_engulfing_df['Timestamp'], unit='ms')
        for record in triple_engulfing_df.to_numpy():
            if record[2] == 'tripleBullishEngulfing':
                fig.add_annotation(x=record[0], y=record[1], text="•", showarrow=False, font=dict(size=30, color='#3a26bc'))
                fig.add_annotation(x=record[0], y=record[1], text="TripleBullishEngulfing", showarrow=True, font=dict(size=12, color='#3a26bc'))
            elif record[2] == 'bearishTripleEngulfing':
                fig.add_annotation(x=record[0], y=record[1], text="•", showarrow=False, font=dict(size=30, color='#bc14de'))
                fig.add_annotation(x=record[0], y=record[1], text="TripleBearishEngulfing ", showarrow=True, font=dict(size=12, color='#bc14de'))

    
    # Convert the plot to HTML
    plot_div = to_html(fig, full_html=False)
    
    # Create the full HTML document
    html_content = f"""
    <html>
        <head>
            <title>CandleStick ({SYMBOL})</title>
            <script>
                function sendMessage() {{
                    // Generate a random message
                    var messages = ["Telegram Connection Testing"];
                    var randomIndex = Math.floor(Math.random() * messages.length);
                    var message = messages[randomIndex];
                    
                    // Send the message to Telegram
                    var xhr = new XMLHttpRequest();
                    xhr.open("GET", "/send_message", true);
                    xhr.send();
                }}
            </script>
        </head>
        <body>
            <h1>CandleStick Chart ({SYMBOL})</h1>
            <div style="display: flex; flex-direction: row; gap: 12px;">
                <button style="background-color: black; color: white; padding: 15 40; border-radius: 8px; border: unset; cursor: pointer" onclick="sendMessage()">Send Message</button>
                <a style="background-color: black; color: white; padding: 15 40; border-radius: 8px; border: unset; cursor: pointer" href="/BTC-USDT">BTC/USDT</button>
                <a style="background-color: black; color: white; padding: 15 40; border-radius: 8px; border: unset; cursor: pointer" href="/ETH-USDT">ETH/USDT</button>
            </div> 
            <div></div>
            {plot_div}
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
