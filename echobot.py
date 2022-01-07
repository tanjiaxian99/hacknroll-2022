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
import matplotlib.pyplot as plt
import yfinance as yf
yf.pdr_override()

from telegram import Update, ForceReply, constants
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Get token value
load_dotenv()
token = os.getenv("TOKEN")

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
from PIL import Image
from io import BytesIO

def stocks_command(update: Update, context: CallbackContext) -> None:
    # Ensure that a stock name has been given
    if len(context.args) == 0:
        update.message.reply_text("Invalid command. Please key in a stock name, and optionally the time period. " +
        "E.g. /stocks apple 1m")
        return

    # Opens page for associated stock
    stock_name = context.args[0]
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://www.google.com/finance/")
    element = driver.find_element_by_xpath("//body/c-wiz[1]/div[1]/div[3]/div[3]/div[1]/div[1]/div[1]/div[1]/input[2]")
    element.send_keys(stock_name)
    element.send_keys(Keys.ENTER)
    time.sleep(0.5)

    try:
        url = driver.current_url
        ticker_exchange = url.split("/")[5]
        ticker_symbol = ticker_exchange.split(":")[0]
    except:
        update.message.reply_text("Invalid stock name. Please key in a valid stock name.")
        return
    
    # Opens page with the correct time period if it exists
    if len(context.args) >= 2:
        time_period = context.args[1]
        url = url + "?window=" + time_period
        driver.get(url)
    
    # Retrieve the screenshot
    time.sleep(0.5)
    png = driver.get_screenshot_as_png()
    driver.close()

    # Crop the screenshot
    im = Image.open(BytesIO(png))
    im = im.crop((0, 172, 912, 648))
    img_byte_arr = BytesIO()
    im.save(img_byte_arr, format="PNG")
    im = img_byte_arr.getvalue()

    # Ticker values
    ticker = yf.Ticker(ticker_symbol)
    ticker_info = ticker.info
    caption_format = ("<a href=\"{url}\">{symbol}</a>\n<b>Open:</b> {open}\n<b>Previous close:</b> {previous_close}\n" + 
        "<b>Volume:</b> {volume}")
    caption = caption_format.format(url=url, symbol=ticker_info["symbol"], open=ticker_info["open"], 
        previous_close=ticker_info["previousClose"], volume=ticker_info["volume"])

    update.message.reply_photo(im, caption = caption, parse_mode = constants.PARSEMODE_HTML)

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("stocks", stocks_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
