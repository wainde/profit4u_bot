import requests
import time
import pandas as pd
import os
from datetime import datetime

# ✅ Telegram Bot Credentials (Use environment variables)
BOT_TOKEN = os.getenv("8021146799:AAFYJR3G72OS3Xk_kmA79aG1XZdiudcLLDs")
CHAT_ID = os.getenv("6419058496")

# ✅ Store price data
live_data = []

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
def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url).json()
    return response['bitcoin']['usd']

# ✅ Check Trading Signal (Your Logic)
def check_trading_signal():
    """Analyze price data and send alerts if a breakout occurs."""
    if len(live_data) < 20:
        return
    
    df = pd.DataFrame(live_data)
    df['support'] = df['price'].rolling(window=10).min()
    df['resistance'] = df['price'].rolling(window=10).max()

    current_price = df['price'].iloc[-1]
    prev_resistance = df['resistance'].iloc[-2]
    prev_support = df['support'].iloc[-2]

    print(f"🔍 Checking signals - Current Price: {current_price}, Resistance: {prev_resistance}, Support: {prev_support}")

    if current_price > prev_resistance:
        message = f"🚀 Breakout Alert! BTC Above Resistance: ${current_price:.2f}"
        print(f"✅ Sending Telegram Alert: {message}")
        send_telegram_message(message)
    
    elif current_price < prev_support:
        message = f"⚠️ Breakdown Alert! BTC Below Support: ${current_price:.2f}"
        print(f"✅ Sending Telegram Alert: {message}")
        send_telegram_message(message)

# ✅ Monitor BTC price & detect trade
def monitor_price():
    """Fetch BTC price every 10 seconds and check for breakout signals."""
    print("🚀 Monitoring BTC Price for Breakout Signals...")
    
    while True:
        try:
            current_price = get_btc_price()
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            
            # ✅ Store price data
            live_data.append({"timestamp": timestamp, "price": current_price})
            if len(live_data) > 50:
                live_data.pop(0)  # Keep last 50 records

            print(f"📊 BTC Price: ${current_price} at {timestamp}")
            check_trading_signal()  # ✅ Check for breakout

            time.sleep(10)  # ✅ Check every 10 seconds

        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)  # Wait before retrying

# ✅ Start price monitoring
monitor_price()
