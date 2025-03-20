import requests
import time
from datetime import datetime
import os

# ✅ Fix for Windows event loop issue
if os.name == 'nt':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ✅ Telegram Bot Credentials
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Use environment variables
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ Function to send messages to Telegram
def send_telegram_message(message):
    TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(TELEGRAM_API_URL, params=params)
    
    if response.status_code == 200:
        print("📩 Telegram Alert Sent!")
    else:
        print(f"❌ Failed to send Telegram message: {response.text}")

# ✅ Fetch BTC price using CoinGecko API
def get_binance_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url).json()
    return response['bitcoin']['usd']

# ✅ Main function to monitor price
def start_monitoring():
    print("✅ Script started. Monitoring BTC price...")

    last_price = None  # Store last price for comparison

    while True:
        try:
            current_price = get_binance_price()
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            print(f"📊 BTC Price: ${current_price} at {timestamp}")

            # ✅ Send update every 1 minute
            message = f"📊 BTC Price Update: ${current_price} at {timestamp}"
            send_telegram_message(message)

            # ✅ Check for price changes
            if last_price and abs(current_price - last_price) >= 50:  # Adjust threshold if needed
                alert_msg = f"🚨 Price Alert! BTC moved by ${current_price - last_price:.2f}!"
                send_telegram_message(alert_msg)

            last_price = current_price  # Update last price

            time.sleep(60)  # ✅ Wait 1 minute before checking again

        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)  # Wait before retrying

# ✅ Start the monitoring function
start_monitoring()
