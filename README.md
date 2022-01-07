# FinanceBros Bot

A Telegram bot that provides commands to

- Display real-time stock market data and charts from Yahoo Finance.
- Track user's investments.
- Backtest using Guppy Multiple Moving Average (GMMA).

This was written in Python 3.8 and built as our team's submission for Hack & Roll 2022.

### Stock Searching and Charting

We obtained real-time stock market data from [`yfinance`](https://github.com/ranaroussi/yfinance).

Charting is done using the [`Selenium`](https://pypi.org/project/selenium/) library, which visits Google Finance and automatically keys in the name of the input stock. A cropped screenshot is then taken and displayed to the user. The data from the site is also used to retrieve other ticker information from the yfinance library.

### Investment Tracker

The bot tracks users' stock positions, in 3 fields:

- Stock Symbol
- Amount bought
- Buy Price

Through our command:

1. `/add`, users are able to add new investments made.
2. `/remove`, users are able to remove desired amount of any existing stock positions.
3. `/calculate`, users are able to their unrealised profit and loss.
4. `/check`, users are able to check their existing stock positions.

### Backtesting

Backtesting is a term used in modeling to refer to testing a trading strategy on historical data.

Users can backtest with Guppy Multiple Moving Average (GMMA), a technical indicator that identifies changing trends, breakouts, and trading opportunities in the price of an asset by combining two groups of moving averages (MA) with different time periods. It provides an objective method to know when to get in and when to get out of a trade.

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
