import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime

# ✅ Telegram Bot Details
BOT_TOKEN = "8021146799:"  # Replace with your token
CHAT_ID = ""


def send_telegram_message(message):
    """Send a message to the Telegram bot."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, json=payload)


# ✅ Bitstamp API for BTC price (Free & 24/7)
BITSTAMP_URL = "https://www.bitstamp.net/api/v2/ticker/btcusd/"

# ✅ Live data storage
live_data = []


def fetch_price():
    """Fetch BTC price from Bitstamp API."""
    try:
        response = requests.get(BITSTAMP_URL, timeout=5)
        data = response.json()
        return float(data["last"]) if "last" in data else None
    except requests.exceptions.RequestException:
        return None


def find_support_resistance(df, window=10):
    """Calculate support and resistance levels."""
    df['support'] = df['low'].rolling(window=window).min()
    df['resistance'] = df['high'].rolling(window=window).max()
    return df


def detect_breakout(df):
    """Detect breakout conditions."""
    df['breakout_up'] = df['close'] > df['resistance'].shift(1)
    df['breakout_down'] = df['close'] < df['support'].shift(1)
    return df


def confirm_trade(df, volume_threshold=1.2):
    """Confirm breakout with strong candles and volume spike."""
    df['strong_candle'] = (df['close'] - df['open']) / (df['high'] -
                                                        df['low']) > 0.6
    df['volume_spike'] = df['volume'] > df['volume'].rolling(
        10).mean() * volume_threshold
    df['confirmed_breakout'] = df['strong_candle'] & df['volume_spike']
    return df


def detect_trap(df):
    """Detect false breakouts (stop-loss hunting)."""
    df['false_breakup'] = (df['breakout_up'] &
                           (df['close'] < df['resistance'].shift(1)))
    df['false_breakdown'] = (df['breakout_down'] &
                             (df['close'] > df['support'].shift(1)))
    return df


def check_trading_signal():
    """Analyze price and send alerts if a breakout occurs."""
    if len(live_data) < 20:
        return

    df = pd.DataFrame(live_data)
    df = find_support_resistance(df)
    df = detect_breakout(df)
    df = confirm_trade(df)
    df = detect_trap(df)

    current_price = df['close'].iloc[-1]
    prev_resistance = df['resistance'].iloc[-2]
    prev_support = df['support'].iloc[-2]

    if df['confirmed_breakout'].iloc[-1]:
        if df['breakout_up'].iloc[-1]:
            message = f"🚀 Breakout Alert! BTC Above Resistance: ${current_price:.2f}"
        elif df['breakout_down'].iloc[-1]:
            message = f"⚠️ Breakdown Alert! BTC Below Support: ${current_price:.2f}"
        send_telegram_message(message)

    if df['false_breakup'].iloc[-1] or df['false_breakdown'].iloc[-1]:
        send_telegram_message(
            f"⚠️ Fake Breakout Detected! BTC at ${current_price:.2f}")


def start_monitoring():
    """Continuously monitor BTC price."""
    print("✅ Monitoring BTC price for trading signals...")

    while True:
        btc_price = fetch_price()
        if btc_price:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            live_data.append({
                "timestamp": timestamp,
                "close": btc_price,
                "high": btc_price,
                "low": btc_price,
                "open": btc_price,
                "volume": 1
            })

            if len(live_data) > 50:
                live_data.pop(0)

            check_trading_signal()

        time.sleep(15)  # Check price every 15 seconds


# Start monitoring BTC price
start_monitoring()
