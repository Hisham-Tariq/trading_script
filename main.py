import requests
import logging
import time
from stock_analysis import StockAnalysis
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
# Configure logging
logging.basicConfig(filename=os.path.join(ROOT_PATH, 'trading_script.log'), level=logging.INFO)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') 
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Constants
TIMEFRAME = '2h'
CANDLE_LIMITS = 50


currencies = []
# Read the currency list
with open(os.path.join(ROOT_PATH, 'currency_list.txt'), 'r') as f:
    currencies = [currency.strip().upper() for currency in f.readlines()]



def send_to_telegram(message):
    B_T = [
        TELEGRAM_BOT_TOKEN,
        '7099206933:AAHaxBbWnppc1OnCULvRuS-b7t0Exa0gZec',
        '6368295855:AAFr-_uaGnOZOheEX-HqsjX3JhmdLvbF4Qw'
    ]

    C_I = [
        TELEGRAM_CHAT_ID,
        '-4128390434',
        '-1002115210977',
    ]

    for i in range(len(B_T)):
        url = f'https://api.telegram.org/bot{B_T[i]}/sendMessage'
        data = {
            'chat_id': C_I[i],
            'text': message
        }
        try:
            requests.post(url, data=data)
        except Exception as e:
            logging.error(f"Error sending message to Telegram: {e}") 

   

def run_script():
    for symbol in currencies:
        try:
            s_analysis = StockAnalysis(
                symbol=symbol,
                timeframe=TIMEFRAME,
                candle_limits=CANDLE_LIMITS
            )
            message = s_analysis.analyze()
            
            if message:
                send_to_telegram(f'{symbol} {message}')
            else:
                send_to_telegram(f'{symbol} No signal found')
            logging.info(f"Analysis completed for {symbol}. Message: {message}, Time is {datetime.now()}")
            logging.info(f"Records are: {s_analysis.records_history().tolist()}", )
        except Exception as e:
            import traceback
            traceback.print_exc()
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