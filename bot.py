import os
from dotenv import load_dotenv
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
from backtest import backtesting

import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
from PIL import Image
from io import BytesIO

# Retrieve Token
load_dotenv()
API_TOKEN = os.getenv("TOKEN")

# Enable logging
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Local dictionaries to store users' input
data = {'symbol': "", 'day': "", 'month': "", 'year': ""}
wallet = {}
SYMBOL, DATE, ADD, REMOVE, CHECK = range(5)

'''
General Functions - Command Handlers
'''
def start(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        """Welcome to InvestLiao. If you just come one, click /help then uncle will show you how""")


def help_command(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
    """Come come let me show you what uncle can do.
/wallet - maintain your stock wallet for you
/stocks [stock_name] - show what stocks you want me to show
/backtest [stock_name] [date] - come test our amazing algo trading software
    """)


def cancel(update: Update, context: CallbackContext) -> int:
    update.effective_message.reply_text('canceled')
    # end of conversation
    return ConversationHandler.END

'''
Stocks Graph Functions - Command Handlers
'''

PORT = int(os.getenv("PORT", 8443))

def stocks_command(update: Update, context: CallbackContext) -> None:
    # Ensure that a stock name has been given
    if len(context.args) == 0:
        update.effective_message.reply_text("Wrong command leh. Give me a stock name so become /stocks apple")
        return

    stock_name = context.args[0]

    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1D", callback_data="1D_" + stock_name),
            InlineKeyboardButton("5D", callback_data="5D_" + stock_name),
            InlineKeyboardButton("1M", callback_data="1M_" + stock_name),
            InlineKeyboardButton("6M", callback_data="6M_" + stock_name),
        ],
        [
            InlineKeyboardButton("YTD", callback_data="YTD_" + stock_name),
            InlineKeyboardButton("1Y", callback_data="1Y_" + stock_name),
            InlineKeyboardButton("5Y", callback_data="5Y_" + stock_name),
            InlineKeyboardButton("MAX", callback_data="MAX_" + stock_name),
        ]
    ])
    update.effective_message.reply_text("Lai lai choose a time period", reply_markup=reply_markup)

def stocks_callback(update: Update, context: CallbackContext) -> int:
    update.effective_message.delete()

    # Retrieve time period
    query = update.callback_query
    query.answer()
    choice = query.data
    if "_" in choice:
        [time_period, stock_name] = choice.split("_")

    
    if choice == 'Yes':
        clear_wallet(update, context)
        return ConversationHandler.END

    if choice == 'Cancel':
        cancel(update, context)

    
    if choice == 'Add':
        new_entry(update, context)
        return ADD

    
    if choice == 'Remove':
        remove_entry(update, context)
        return REMOVE


    if choice == 'Calculate':
        calculate(update, context)
        return ConversationHandler.END


    if choice == 'Clear All':
        clear_all(update, context)
        return ConversationHandler.END
    
    # Send wait message
    wait_message = update.effective_message.reply_text("Wait ah I fetching your stock information")

    # Opens page for associated stock
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
        wait_message.delete()
        update.effective_message.reply_text("Cannot find the stock leh. Give me a valid stock name")
        return

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
    try:
        ticker = yf.Ticker(ticker_symbol)
        ticker_info = ticker.info
        caption_format = ("<a href=\"{url}\">{symbol}</a>\n<b>Open:</b> {open}\n<b>Previous close:</b> {previous_close}\n" + 
            "<b>Volume:</b> {volume}")
        caption = caption_format.format(url=url, symbol=ticker_info["symbol"], open=ticker_info["open"], 
            previous_close=ticker_info["previousClose"], volume=ticker_info["volume"])

        wait_message.delete()
        update.effective_message.reply_photo(im, caption=caption, parse_mode=constants.PARSEMODE_HTML)
    except:
        wait_message.delete()
        update.effective_message.reply_photo(im, caption="Sorry ah don't have ticker information")



'''
Backtesting Functions - Command Handlers
'''

def backtest(update: Update, context: CallbackContext) -> int:
    global data
    """Create new empty dictionary"""
    data = {'symbol': "", 'date' : ""}
    update.effective_message.reply_text("Come we backtest using Guppy Multiple Moving Average.\n\nWhat stock symbol to backtest (e.g AAPL)?")
    return SYMBOL

def symbol(update: Update, context: CallbackContext) -> int:
    data['symbol'] = update.message.text
    update.effective_message.reply_text(f"You want: {update.effective_message.text.upper()}\n\nNow type the date to backtest from, in DDMMYYYY format (e.g 01012020):")
    return DATE

def date(update: Update, context: CallbackContext, ) -> int:
    data['day'] = update.effective_message.text[0:2]
    data['month'] = update.effective_message.text[2:4]
    data['year'] = update.effective_message.text[4:] 
    
    try:
        results = backtesting(data['symbol'], data['day'], data['month'], data['year'])
    except: 
        update.effective_message.reply_text("Aiyo your symbol or date is wrong.\n\nTry again or press /cancel to panggang.\n\nWhat stock symbol to backtest (e.g AAPL)?")
        return SYMBOL
    else: 
        update.effective_message.reply_text(f"Backtesting {data['symbol'].upper()} from: {update.effective_message.text[0:2]}/{update.effective_message.text[2:4]}/{update.effective_message.text[4:]}" )
        update.effective_message.reply_text(f"Stock: {results['stock'].upper()}\nSample Size: {results['sample_size']}\nEMAs Used: {results['EMAs_used']}\nBatting Average: {results['Batting_Avg']}\nGain Loss Ratio: {results['GainLoss_ratio']}\nAverage Gain: {results['Average_Gain']}\nAverage Loss: {results['Average_Loss']}\nMax Return: {results['Max_Return']}\nMax Loss: {results['Max_Loss']}\nTotal Return: {results['Total_return']}")
        update.effective_message.reply_text("If you want to learn more about the indicator used (i.e GMMA), type /gmma")
        return ConversationHandler.END


def gmma(update: Update, context: CallbackContext) -> None:
    msg = "GMMA is a technical indicator that identifies changes in trends, providing an objective method to know when to get in and when to get out of a trade."
    msg2 = "6 short-term EMAs in red (3, 5, 8, 10, 12, 15), and 6 long-term EMAs in blue (30, 35, 40, 35, 50, 60) are used.\n\nWhen red crosses above blue (i.e Red White Blue), it is a Buy Signal.\n\nWhen blue crosses above red (i.e Blue White Red), it is a Sell Signal."
    update.effective_message.reply_text(msg)
    update.effective_message.reply_text(msg2)

'''
Wallet Functions - Command Handlers
'''

def new_entry(update: Update, context: CallbackContext) -> int:
    """Add stock into the wallet"""
    update.effective_message.reply_text("Buy new stocks ah?")
    update.effective_message.reply_text("Type in the stock symbol, amount bought and buy price,\nseparated by a space (e.g AAPL 10 172.00):")
    return ADD

def add(update: Update, context: CallbackContext) -> int:
    """Put the entry into the wallet"""
    # Obtain data from text
    inputs = update.effective_message.text.split(" ")
    to_add = [inputs[0].upper(), int(inputs[1]), float("{:.2f}".format(float(inputs[2])))] #name, qty, price 
    return error_add(update, context, to_add)

def error_add(update: Update, context: CallbackContext, to_add) -> None:
    try:
        results = backtesting(to_add[0], '01', '01', '2020')
    except: 
        update.effective_message.reply_text("Eh your symbol is wrong.\nTry to add again or type /cancel to panggang.")
        update.effective_message.reply_text("Type in the stock symbol, amount bought and buy price,\nseparated by a space (e.g AAPL 10 172.00):")
        return ADD
    else: 
        if to_add[0] in wallet:
            # Update quantity
            prev_qty = wallet.get(to_add[0])[0] #[qty, price]
            new_qty = prev_qty + to_add[1]
            wallet.get(to_add[0])[0] = new_qty
            # Update avg price
            prev_pri = wallet.get(to_add[0])[1] * prev_qty
            new_pri = (prev_pri + to_add[2]*to_add[1])/new_qty
            wallet.get(to_add[0])[1] = new_pri
            update.effective_message.reply_text("Added liao.")
            return check(update, context)
        else:
            wallet[to_add[0]] = to_add[1:]
            update.effective_message.reply_text("Added liao.")
            return check(update, context)

def check(update: Update, context: CallbackContext):
    """Check current wallet"""
    if len(wallet) == 0:
        update.effective_message.reply_text("Your wallet bo liu leh")
    else:
        sortedWallet = sorted(wallet.keys())
        update.effective_message.reply_text("Your wallet:")
        for i in sortedWallet:
            update.effective_message.reply_text("{}, Amount bought: {}, Average Price: {}".format(i, wallet[i][0], wallet[i][1]))

    keyboard = [
        [
            InlineKeyboardButton("Add", callback_data='Add'),
            InlineKeyboardButton("Remove", callback_data='Remove')
        ],
        [
            InlineKeyboardButton("Calculate", callback_data='Calculate'),
            InlineKeyboardButton("Clear All", callback_data='Clear All')    
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text("Come select what you want.", reply_markup=reply_markup)
    return ConversationHandler.END


def remove_entry(update: Update, context: CallbackContext) -> int:
    """Remove stock from the wallet"""
    if len(wallet) == 0:
        update.effective_message.reply_text("Your wallet has no more moneh.")
    else:
        update.effective_message.reply_text("Sell stocks ah?")
        update.effective_message.reply_text("Type in the stock symbol, amount sold and sell price,\nseparated by a space (e.g AAPL 10 121.00):")
    return REMOVE

def remove(update: Update, context: CallbackContext) -> int:
    inputs = update.effective_message.text.split(" ")
    sym = inputs[0].upper()
    amt = int(inputs[1])
    price = float(inputs[2])
    return error_remove(update, context, sym, amt, price)

def error_remove(update: Update, context: CallbackContext, sym, amt, price) -> None:
    try:
        results = backtesting(sym, '01', '01', '2020')
    except:
        update.effective_message.reply_text("Wrong entry leh.\nTry to remove again or type /cancel to panggang.")
        update.effective_message.reply_text("Type in the stock symbol, amount sold and sell price,\nseparated by a space (e.g AAPL 10):")
        return REMOVE
    else:
        if sym not in wallet:
            update.effective_message.reply_text("Where got such stock? Try again or type /cancel to panggang")
            update.effective_message.reply_text("Sell stock is it?")
            update.effective_message.reply_text("Type in the stock symbol, amount sold and sell price,\nseparated by a space (e.g AAPL 10):")
            return REMOVE
        else:
            if amt <= 0 or amt > wallet.get(sym)[0]:
                update.effective_message.reply_text("Wrong amount sia.\nTry to remove again or type /cancel to panggang")
                update.effective_message.reply_text("Type in the stock symbol, amount sold and sell price,\nseparated by a space (e.g AAPL 10):")
                return REMOVE
            elif amt == wallet.get(sym)[0]:
                wallet.pop(sym)
                update.effective_message.reply_text("Successful Huat Ah!")
                return check(update, context)
            else:
                # Update quantity symbol : [qty, price]
                prev_qty = wallet.get(sym)[0]
                new_qty =  prev_qty - amt
                wallet.get(sym)[0] = new_qty
                # Update price
                prev_pri = wallet.get(sym)[1] * prev_qty
                new_pri = (prev_pri - amt*price)/new_qty
                wallet.get(sym)[1] = new_pri
                update.effective_message.reply_text("Successful Huat Ah!")
                return check(update, context)

def clear_all(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_text("This will make your money dissapear leh.")

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data='Yes'),
            InlineKeyboardButton("Cancel", callback_data='Cancel'),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text("Sure anot?", reply_markup=reply_markup)

def clear_wallet(update: Update, context: CallbackContext) -> None:
    global wallet
    wallet = {}
    update.effective_message.reply_text("No more stocks hor.")
    check(update, context)


yf.pdr_override()
def calculate(update: Update, context: CallbackContext):
    start = dt.datetime(2020, 12, 25)
    now = dt.datetime.now()
    sortedWallet = sorted(wallet.keys())
    total = 0
    for i in sortedWallet:
        df = pdr.get_data_yahoo(i, start, now)
        # Obtain today's price
        latest_price = df["Adj Close"][-1]
        net = wallet[i][0] * (latest_price - wallet[i][1])
        total += net
        update.effective_message.reply_text("Return of {} as of today: {}".format(i, "{:.2f}".format(net)))

    update.effective_message.reply_text("Total return of your wallet as of today: {}".format("{:.2f}".format(total)))
    if total <= 0:
        update.effective_message.reply_text("Lose money sian...")
    else:
        update.effective_message.reply_text("Huat Ah!")
    return ConversationHandler.END



'''
Main Function
'''

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(API_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    conv_handler = ConversationHandler (
        entry_points=[MessageHandler(~Filters.regex(r' '), symbol)],
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
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    conv_handler_1 = ConversationHandler (
        entry_points=[CallbackQueryHandler(stocks_callback)],
        states={
            ADD: [
                CommandHandler('cancel', cancel),  # has to be before MessageHandler to catch `/cancel` as command, not as `title`
                MessageHandler(Filters.text, add)
            ],
            CHECK: [
                CommandHandler('cancel', cancel),
                MessageHandler(Filters.text, check)
            ],
            REMOVE: [
                CommandHandler('cancel', cancel),  # has to be before MessageHandler to catch `/cancel` as command, not as `title`
                MessageHandler(Filters.text, remove)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("stocks", stocks_command))
    dispatcher.add_handler(CommandHandler("wallet", check))
    dispatcher.add_handler(CommandHandler("backtest", backtest))
    dispatcher.add_handler(CommandHandler("gmma", gmma))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(conv_handler_1)
    dispatcher.add_handler(CallbackQueryHandler(stocks_callback))

    # Start the Bot


    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()