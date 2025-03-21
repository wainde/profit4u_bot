import requests
import pandas as pd
import time
import telegram
from datetime import datetime

# Telegram Bot Details
BOT_TOKEN = "8021146799:AAFYJR3G72OS3Xk_kmA79aG1XZdiudcLLDs"  # Replace with your bot token
CHAT_ID = "6419058496"  # Replace with your chat ID
bot = telegram.Bot(token=BOT_TOKEN)

# Bitstamp API URL for BTC price (FREE & 24/7)
BITSTAMP_URL = "https://www.bitstamp.net/api/v2/ticker/btcusd/"

# Store live price data
live_data = []

def fetch_price():
    """Fetch BTC price from Bitstamp API (Free & 24/7)."""
    try:
        response = requests.get(BITSTAMP_URL, timeout=5)  # Added timeout
        data = response.json()

        # Debugging: Print API response
        print(f"🔍 Bitstamp API Response: {data}")

        if "last" in data:
            return float(data["last"])
        else:
            print(f"⚠️ Unexpected API response format: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Network error fetching price: {e}")
        return None
    except ValueError:
        print("⚠️ Failed to parse API response.")
        return None

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
        bot.send_message(chat_id=CHAT_ID, text=message)

    elif current_price < prev_support:
        message = f"⚠️ Breakdown Alert! BTC Below Support: ${current_price:.2f}"
        print(f"✅ Sending Telegram Alert: {message}")
        bot.send_message(chat_id=CHAT_ID, text=message)

def start_monitoring():
    """Continuously monitor BTC price and send alerts when needed."""
    print("✅ Monitoring BTC price for trading signals...")

    while True:
        btc_price = fetch_price()
        if btc_price:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            live_data.append({"timestamp": timestamp, "price": btc_price})

            if len(live_data) > 50:
                live_data.pop(0)  # Keep only the last 50 records

            check_trading_signal()

        time.sleep(15)  # Check price every 15 seconds

# Start monitoring
start_monitoring()
