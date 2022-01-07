# FinanceBros Bot

A Telegram bot that provides commands to

- Track user's investments
- Display real-time stock market data and charts from Yahoo Finance
- Backtest using Guppy Multiple Moving Average (GMMA).

This was built as our team's submission for Hack & Roll 2022. All of these are written in Python 3.8.

### Investment Tracker

The bot tracks users existing investments, in 3 fields:

- Stock Symbol
- Amount bought
- Buy Price

Through our command `wallet` and ` `.

### Stock Searching and Charting

We obtained real-time stock market data from [`yfinance`](https://github.com/ranaroussi/yfinance).

Charting is done using `pandas` and `seaborn`.

### Backtesting

Backtest with Guppy Multiple Moving Average (GMMA), a technical indicator that identifies changing trends, breakouts, and trading opportunities in the price of an asset by combining two groups of moving averages (MA) with different time periods.

After you input the stock symbol, and the date to backtest from, the bot will output :

- Stock
- Sample Size
- EMAs Used
- Batting Average
- Gain Loss Ratio
- Average Gain
- Average Loss
- Max Return
- Max Loss
- Total Return

... as of todays date.
