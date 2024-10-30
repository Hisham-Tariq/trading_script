Installation:
1. Python Version: 3.9.6
2. Create venv in the trading_script folder
3. activate the venv
4. install the dependencies using pip3 install -r requirements.txt

For setting up cron job to get alerts
1. Execute 'EDITOR=nano crontab -e'
2. and add the cron '1 */2 * * * /root/trading_script/venv/bin/python /root/trading_script/main.py'
   make sure the path is accurate for python and script

1. Copy the Service file to /etc/systemd/system,
2. save the code in the /root/trading_script
3. enable and start the service

access the page on 80 port

In order to run the last code to get automatic alerts on a currency

1. First add its symbol in the currency_list.txt
2. Add the cron in the system to automaticaly run after a certain internal 
3. Add a .env file with 
  TELEGRAM_BOT_TOKEN='<BOT_TOKEN>'
  TELEGRAM_CHAT_ID='<CHAT_ID>'

for testing run the main.py file if it runs successfully without any errors the script is successfull

