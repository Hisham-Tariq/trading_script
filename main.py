import requests
import logging
import time
from stock_analysis import StockAnalysis
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
print(ROOT_PATH)
# Configure logging
logging.basicConfig(filename=os.path.join(ROOT_PATH, 'trading_script.log'), level=logging.INFO)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') 
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Constants
TIMEFRAME = '2h'
CANDLE_LIMITS = 5

currencies = []
# Read the currency list
with open('currency_list.txt', 'r') as f:
    currencies = [currency.strip().upper() for currency in f.readlines()]



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
            logging.info(f"Analysis completed for {symbol}. Result: {result}")
        except Exception as e:
            logging.error(f"Error analyzing {symbol}: {e}")



# Retry mechanism
MAX_RETRIES = 3
RETRY_DELAY = 60 * 5  # 5 minutes

for _ in range(MAX_RETRIES):
    try:
        run_script()
        logging.info("Script execution successful.")
        break  # Exit loop if successful
    except Exception as e:
        logging.error(f"Error running script: {e}")
        time.sleep(RETRY_DELAY)
else:
    logging.error("Max retries reached. Exiting.")