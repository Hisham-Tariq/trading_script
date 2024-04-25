from stock_analysis import StockAnalysis
    
TELEGRAM_BOT_TOKEN = '6763183063:AAEmPmKc18NhZcVN37CMSfkLBuOOnDeB1xE'
TELEGRAM_CHAT_ID = '-1002023135053'

currencies = []
# read the currency_list.txt file
with open('currency_list.txt', 'r') as f:
    currencies = f.readlines()
    currencies = [currency.strip().upper() for currency in currencies]

# EXCHANGE Data Constants
TIMEFRAME = '2h'  # You can change the timeframe as needed
CANDLE_LIMITS = 5  # Limit the number of candles fetched

def send_to_telegram(message):
    import requests
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    requests.post(url, data=data)

for symbol in currencies:
    result = StockAnalysis(
        symbol=symbol,
        timeframe=TIMEFRAME,
        candle_limits=CANDLE_LIMITS
    ).analyze()

    if result == 'bueng':
        send_to_telegram(f'{symbol} is bullish')
    elif result == 'beeng':
        send_to_telegram(f'{symbol} is bearish')
    else:
        send_to_telegram(f'{symbol} is neutral')


