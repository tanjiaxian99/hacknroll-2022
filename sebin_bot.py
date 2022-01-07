#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from dotenv import load_dotenv
import os
from backtest import backtesting
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
# from pandas_datareader import data as pdr
# yf.pdr_override()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

data = {'symbol': "", 'day': "", 'month': "", 'year': ""}
SYMBOL, DATE = range(2)

# Get token value 
load_dotenv()
token = os.getenv("TOKEN")

# Define a few command handlers. These usually take the two arguments update and
# context. 

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2 (
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )
    return

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def backtest(update: Update, context: CallbackContext) -> int:
    global data
    
    """Create new empty dictionary"""
    data = {'symbol': "", 'date' : ""}
    update.message.reply_text("Backtest using Guppy Multiple Moving Average!\n\nType in the stock symbol to backtest (e.g AAPL):")
    return SYMBOL

    # input_ticker = context.args[0]
    # ticker = yf.Ticker(input_ticker.upper())
    # info = ticker.info
    # stock_name = info.get("longName")
    # update.message.reply_text(stock_name)

def symbol(update: Update, context: CallbackContext) -> int:
    data['symbol'] = update.message.text
    update.message.reply_text(f"ticker: {update.message.text.upper()}\n\nNow type in the date to backtest from, in DDMMYYYY format (e.g 01012020):")
    return DATE

def date(update: Update, context: CallbackContext) -> int:
    data['day'] = update.message.text[0:2]
    data['month'] = update.message.text[2:4]
    data['year'] = update.message.text[4:] 
    
    try:
        results = backtesting(data['symbol'], data['day'], data['month'], data['year'])
    except: 
        update.message.reply_text("You did not type the right symbol or date.\n\nLet's redo!\nType in the stock symbol to backtest (e.g AAPL):")
        return SYMBOL
    else: 
        update.message.reply_text(f"Backtesting {data['symbol'].upper()} from: {update.message.text[0:2]}/{update.message.text[2:4]}/{update.message.text[4:]}" )
        update.message.reply_text(f"Stock: {results['stock'].upper()}\nSample Size: {results['sample_size']}\nEMAs Used: {results['EMAs_used']}\nBatting Average: {results['Batting_Avg']}\nGain Loss Ratio: {results['GainLoss_ratio']}\nAverage Gain: {results['Average_Gain']}\nAverage Loss: {results['Average_Loss']}\nMax Return: {results['Max_Return']}\nMax Loss: {results['Max_Loss']}\nTotal Return: {results['Total_return']}")
        update.message.reply_text("If you want to learn more about the indicator used (i.e GMMA), type /gmma")
        return ConversationHandler.END
        
    # msg = """I got all data
    # symbol: {}
    # day: {}
    # month: {}
    # year: {}""".format(data['symbol'], data['day'], data['month'], data['year'])
    # update.message.reply_text(msg)

'''
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr

def calc(update: Update, context: CallbackContext) -> int:
    return DATE
    
def date(update: Update, context: CallbackContext) -> int:

    now = dt.datetime.now()
    df = pdr.get_data_yahoo(stock, now, now)

retrieve quantity, buy_price from wallet through ticker symbol 
output profit_loss = (today_price - buy_price) * quantity 
'''

def gmma(update: Update, context: CallbackContext) -> None:
    msg = "GMMA is a technical indicator that identifies changes in trends, providing an objective method to know when to get in and when to get out of a trade."
    msg2 = "6 short-term EMAs in red (3, 5, 8, 10, 12, 15), and 6 long-term EMAs in blue (30, 35, 40, 35, 50, 60) are used.\n\nWhen red crosses above blue (i.e Red White Blue), it is a Buy Signal.\n\nWhen blue crosses above red (i.e Blue White Red), it is a Sell Signal/"
    update.message.reply_text(msg)
    update.message.reply_text(msg2)

def trial(update: Update, context: CallbackContext) -> None:
    msg = """I got all data
    symbol: {}
    day: {}
    month: {}
    year: {}""".format(data['symbol'], data['day'], data['month'], data['year'])
    update.message.reply_text(msg)

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('canceled')
    # end of conversation
    return ConversationHandler.END

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    user = update.effective_user
    update.message.reply_markdown_v2 (
        fr'What would you like me to do, {user.mention_markdown_v2()}\?',
        reply_markup=ForceReply(selective=True),
    )

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Add conversation handler with states symbol, date 
    conv_handler = ConversationHandler (
        entry_points=[CommandHandler('backtest', backtest)],
        states={
            SYMBOL: [
                CommandHandler('cancel', cancel),  # has to be before MessageHandler to catch `/cancel` as command, not as `title`
                MessageHandler(Filters.text, symbol)
            ],
            DATE: [
                CommandHandler('cancel', cancel),  # has to be before MessageHandler to catch `/cancel` as command, not as `title`
                MessageHandler(Filters.text, date)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("trial", trial))
    dispatcher.add_handler(CommandHandler("gmma", gmma))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("cancel", cancel))

    # # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()