import requests
import logging
import time
from stock_analysis import StockAnalysis
from dotenv import load_dotenv
import os

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') 
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
logging.basicConfig(filename='/root/trading_script/trading_script.log', level=logging.ERROR)

currencies = []
# Read the currency list
with open('currency_list.txt', 'r') as f:
    currencies = [currency.strip().upper() for currency in f.readlines()]

# Constants
TIMEFRAME = '2h'
CANDLE_LIMITS = 5

def send_to_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        logging.error(f"Error sending message to Telegram: {e}")

def run_script():
    for symbol in currencies:
        try:
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
        except Exception as e:
            logging.error(f"Error analyzing {symbol}: {e}")



# Retry mechanism
MAX_RETRIES = 3
RETRY_DELAY = 60 * 5  # 5 minutes

for _ in range(MAX_RETRIES):
    try:
        run_script()
        break  # Exit loop if successful
    except Exception as e:
        logging.error(f"Error running script: {e}")
        time.sleep(RETRY_DELAY)
else:
    logging.error("Max retries reached. Exiting.")