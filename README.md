<div align="center">

# 🕵️ SPYBOY

**A multi-strategy SPY options trading bot built on Alpaca.**

![Python](https://img.shields.io/badge/python-3.9+-3776ab?style=flat-square&logo=python&logoColor=white)
![Alpaca](https://img.shields.io/badge/broker-Alpaca-ffce00?style=flat-square)
![Oracle Cloud](https://img.shields.io/badge/deploy-Oracle%20Cloud%20Free-f80000?style=flat-square&logo=oracle&logoColor=white)

</div>

---

> ⚠️ **Educational project. Not financial advice.** Run it on a paper-trading account first.

## 🧠 Strategies

| # | Strategy | Idea |
|---|----------|------|
| 1 | **RSI-2 mean reversion** | Fade extreme short-term oversold/overbought readings |
| 2 | **VWAP σ-band reversion** | Enter when price stretches to a standard-deviation band around VWAP |
| 3 | **TTM Squeeze** | Detect volatility compression and trade the breakout |
| 4 | **Opening-range breakout** | VIX-adaptive range break after the open |
| 5 | **Gap fade** | Small gap-downs tend to fill |

## 🛡️ Risk management

- ATR-based dynamic stops
- Quarter-Kelly position sizing
- 3% daily loss circuit breaker
- Time-of-day filters
- Multi-timeframe trend confirmation

## 🧾 Options logic

- Buys near-ATM **calls** on BUY signals and **puts** on SELL signals
- 2–5 DTE for intraday, 5–14 DTE for swing
- Limit orders at mid-price for better fills
- Auto-closes at stop, target, or end of day

## 🚀 Quick start

```bash
pip install -r requirements.txt
export ALPACA_API_KEY="your_alpaca_key"
export ALPACA_API_SECRET="your_alpaca_secret"
python spyboy.py
```

## 📁 Layout

| File | Purpose |
|------|---------|
| `spyboy.py` | The v2 bot |
| `spyboy-v0.py` | Original RSI / MA / VWAP equity bot |
| `spyboy.html` | Dashboard UI |
| `oracle-setup.sh` | One-shot provisioning for an Oracle Cloud Always Free instance |

---

<div align="center"><sub>Made by <a href="https://github.com/emmanuelhuff7">@emmanuelhuff7</a></sub></div>
