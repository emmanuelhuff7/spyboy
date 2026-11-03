# SPYBOY

A SPY options trading bot using the Alpaca API. It runs a handful of intraday strategies, buys near-the-money calls or puts on signals, and manages exits itself. I wrote it as a learning project; run it on a paper account first.

## Strategies

- RSI-2 mean reversion
- VWAP standard-deviation band reversion
- TTM Squeeze breakout
- Opening range breakout (adjusted by VIX)
- Gap fade

## Risk handling

ATR-based stops, quarter-Kelly position sizing, a 3% daily loss cutoff, time-of-day filters, and a higher-timeframe trend check. Options are 2-5 DTE for intraday and 5-14 DTE for swing trades, entered with limit orders at mid. Open positions are closed at stop, target, or end of day.

## Running it

```
pip install -r requirements.txt
export ALPACA_API_KEY=...
export ALPACA_API_SECRET=...
python spyboy.py
```

## Files

- `spyboy.py` current version
- `spyboy-v0.py` first version (RSI / MA / VWAP on shares)
- `spyboy.html` dashboard
- `oracle-setup.sh` sets up an Oracle Cloud free-tier VM to run the bot

Not financial advice.
