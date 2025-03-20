import asyncio
import requests  # Required for sending messages to Telegram
import os
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import pandas as pd
import numpy as np
import telegram
import time
from binance.client import Client
from binance import ThreadedWebsocketManager
from datetime import datetime

# Binance API (for public data, API keys are not strictly required)
BINANCE_SYMBOL = "BTCUSDT"
client = Client()  # For public endpoints; add your keys if needed

# === Option 1: Use environment variables ===
# BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === Option 2: Hardcode values (for testing only) ===
BOT_TOKEN = "8021146799:AAFYJR3G72OS3Xk_kmA79aG1XZdiudcLLDs"   # Replace with your token
CHAT_ID = "6419058496"                 # Replace with your chat ID

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Missing Telegram BOT_TOKEN or CHAT_ID environment variables.")

bot = telegram.Bot(token=BOT_TOKEN)

# ✅ Store live data
live_data = []

def process_message(msg):
    """Process Binance real-time ticker messages and send updates to Telegram."""
    global live_data

    if 'p' not in msg or 'T' not in msg:
        return  # Ignore messages that don't have price data

    price = float(msg['p'])  # Trade price
    timestamp = datetime.utcfromtimestamp(msg['T'] / 1000)  # Convert ms to seconds

    print(f"📊 Received data - Price: {price}, Time: {timestamp}")  # Debugging

    # Append latest price data
    live_data.append({"timestamp": timestamp, "price": price})
    if len(live_data) > 50:
        live_data.pop(0)  # Keep last 50 records

    # Send price update to Telegram
    message = f"📊 BTCUSDT Update: ${price:.2f} at {timestamp}"
    bot.send_message(chat_id=CHAT_ID, text=message)

    # Check for breakout signals
    check_trading_signal()

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

def start_stream():
    """Starts the Binance WebSocket stream using ThreadedWebsocketManager."""
    print("✅ Script started. Connecting to Binance WebSocket...")

    # ✅ No API key needed for public WebSocket
    twm = ThreadedWebsocketManager()
    twm.start()
    twm.start_symbol_ticker_socket(callback=process_message, symbol=BINANCE_SYMBOL)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("❌ Stopping stream...")
        twm.stop()

# ✅ Start the WebSocket stream
start_stream()