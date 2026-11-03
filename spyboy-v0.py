import os
import time
import json
import logging
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

API_KEY = os.getenv("ALPACA_API_KEY", "YOUR_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET", "YOUR_API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

SYMBOL = "SPY"
TRADE_QTY = 1
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
MA_FAST = 9
MA_SLOW = 21

def get_bars(symbol, timeframe="5Min", limit=100):
    end = datetime.utcnow()
    start = end - timedelta(hours=6)
    bars = api.get_bars(symbol, timeframe, start=start.isoformat(), end=end.isoformat(), adjustment='raw').df
    return bars

def calc_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calc_vwap(bars):
    tp = (bars['high'] + bars['low'] + bars['close']) / 3
    return (tp * bars['volume']).cumsum() / bars['volume'].cumsum()

def get_signal(bars):
    close = bars['close']
    rsi = calc_rsi(close, RSI_PERIOD)
    ma_fast = close.rolling(MA_FAST).mean()
    ma_slow = close.rolling(MA_SLOW).mean()
    vwap = calc_vwap(bars)

    latest_rsi = rsi.iloc[-1]
    latest_close = close.iloc[-1]
    latest_vwap = vwap.iloc[-1]
    ma_cross_bull = ma_fast.iloc[-1] > ma_slow.iloc[-1] and ma_fast.iloc[-2] <= ma_slow.iloc[-2]
    ma_cross_bear = ma_fast.iloc[-1] < ma_slow.iloc[-1] and ma_fast.iloc[-2] >= ma_slow.iloc[-2]
    above_vwap = latest_close > latest_vwap

    score = 0
    reasons = []

    if latest_rsi < RSI_OVERSOLD:
        score += 2
        reasons.append(f"RSI oversold ({latest_rsi:.1f})")
    elif latest_rsi > RSI_OVERBOUGHT:
        score -= 2
        reasons.append(f"RSI overbought ({latest_rsi:.1f})")

    if ma_cross_bull:
        score += 2
        reasons.append("Bullish MA crossover")
    elif ma_cross_bear:
        score -= 2
        reasons.append("Bearish MA crossover")

    if above_vwap:
        score += 1
        reasons.append("Price above VWAP")
    else:
        score -= 1
        reasons.append("Price below VWAP")

    if score >= 3:
        signal = "BUY"
    elif score <= -3:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "signal": signal,
        "score": score,
        "rsi": round(latest_rsi, 2),
        "ma_fast": round(ma_fast.iloc[-1], 2),
        "ma_slow": round(ma_slow.iloc[-1], 2),
        "vwap": round(latest_vwap, 2),
        "price": round(latest_close, 2),
        "reasons": reasons,
        "timestamp": datetime.utcnow().isoformat()
    }

def get_position():
    try:
        pos = api.get_position(SYMBOL)
        return int(pos.qty)
    except:
        return 0

def execute_trade(signal, current_position):
    if signal == "BUY" and current_position == 0:
        api.submit_order(symbol=SYMBOL, qty=TRADE_QTY, side='buy', type='market', time_in_force='day')
        log.info(f"BUY {TRADE_QTY} {SYMBOL}")
        return "BUY"
    elif signal == "SELL" and current_position > 0:
        api.submit_order(symbol=SYMBOL, qty=current_position, side='sell', type='market', time_in_force='day')
        log.info(f"SELL {current_position} {SYMBOL}")
        return "SELL"
    return "HOLD"

def get_status():
    account = api.get_account()
    position = get_position()
    bars = get_bars(SYMBOL)
    signal_data = get_signal(bars)
    orders = api.list_orders(status='all', limit=20)
    trades = []
    for o in orders:
        if o.symbol == SYMBOL and o.status == 'filled':
            trades.append({
                "time": o.filled_at,
                "side": o.side,
                "qty": o.filled_qty,
                "price": float(o.filled_avg_price) if o.filled_avg_price else 0
            })
    return {
        "account": {
            "equity": float(account.equity),
            "cash": float(account.cash),
            "buying_power": float(account.buying_power),
            "pnl": float(account.equity) - float(account.last_equity)
        },
        "signal": signal_data,
        "position": position,
        "trades": trades[:10]
    }

if __name__ == "__main__":
    log.info("SPY Bot starting...")
    while True:
        try:
            clock = api.get_clock()
            if not clock.is_open:
                log.info("Market closed. Waiting...")
                time.sleep(60)
                continue
            bars = get_bars(SYMBOL)
            signal_data = get_signal(bars)
            position = get_position()
            log.info(f"Signal: {signal_data['signal']} | Price: {signal_data['price']} | RSI: {signal_data['rsi']} | Position: {position}")
            execute_trade(signal_data['signal'], position)
            time.sleep(300)
        except Exception as e:
            log.error(f"Error: {e}")
            time.sleep(60)