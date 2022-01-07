import os
from dotenv import load_dotenv
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
from backtest import backtesting

import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr

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
wallet = {"AAPL": [12,222.2]}
SYMBOL, DATE, ADD, REMOVE, CHECK = range(5)

'''
General Functions - Command Handlers
'''
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.effective_message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.effective_message.reply_text('Help!')

def cancel(update: Update, context: CallbackContext) -> int:
    update.effective_message.reply_text('canceled')
    # end of conversation
    return ConversationHandler.END

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    user = update.effective_user
    update.effective_message.reply_markdown_v2 (
        fr'What would you like me to do, {user.mention_markdown_v2()}\?',
        reply_markup=ForceReply(selective=True),
    )

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
    data['symbol'] = update.effective_message.text
    update.effective_message.reply_text(f"You want: {update.message.text.upper()}\n\nNow type the date to backtest from, in DDMMYYYY format (e.g 01012020):")
    return DATE

def date(update: Update, context: CallbackContext) -> int:
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
    inputs = update.message.text.split(" ")
    to_add = [inputs[0].upper(), int(inputs[1]), float("{:.2f}".format(float(inputs[2])))] #name, qty, price 
    return error_add(update, context, to_add)

def error_add(update: Update, context: CallbackContext, to_add) -> None:
    try:
        results = backtesting(to_add[0], '01', '01', '2020')
    except: 
        update.message.reply_text("Eh your symbol is wrong.\nTry to add again or type /cancel to panggang.")
        update.message.reply_text("Type in the stock symbol, amount bought and buy price,\nseparated by a space (e.g AAPL 10 172.00):")
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
            update.message.reply_text("Added liao.")
            return check(update, context)
        else:
            wallet[to_add[0]] = to_add[1:]
            update.message.reply_text("Added liao.")
            return check(update, context)

def check(update: Update, context: CallbackContext) -> None:
    """Check current wallet"""
    if len(wallet) == 0:
        update.message.reply_text("Your wallet bo liu leh")
    else:
        sortedWallet = sorted(wallet.keys())
        update.message.reply_text("Your wallet:")
        for i in sortedWallet:
            update.message.reply_text("{}, Amount bought: {}, Average Price: {}".format(i, wallet[i][0], wallet[i][1]))
    

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
    inputs = update.message.text.split(" ")
    sym = inputs[0].upper()
    amt = int(inputs[1])
    price = float(inputs[2])
    return error_remove(update, context, sym, amt, price)

def error_remove(update: Update, context: CallbackContext, sym, amt, price) -> None:
    try:
        results = backtesting(sym, '01', '01', '2020')
    except:
        update.message.reply_text("Wrong entry leh.\nTry to remove again or type /cancel to panggang.")
        update.message.reply_text("Type in the stock symbol, amount sold and sell price,\nseparated by a space (e.g AAPL 10):")
        return REMOVE
    else:
        if sym not in wallet:
            update.message.reply_text("Where got such stock? Try again or type /cancel to panggang")
            update.message.reply_text("Sell stock is it?")
            update.message.reply_text("Type in the stock symbol, amount sold and sell price,\nseparated by a space (e.g AAPL 10):")
            return REMOVE
        else:
            if amt <= 0 or amt > wallet.get(sym)[0]:
                update.message.reply_text("Wrong amount sia.\nTry to remove again or type /cancel to panggang")
                update.message.reply_text("Type in the stock symbol, amount sold and sell price,\nseparated by a space (e.g AAPL 10):")
                return REMOVE
            elif amt == wallet.get(sym)[0]:
                wallet.pop(sym)
                update.message.reply_text("Successful Huat Ah!")
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
                update.message.reply_text("Successful Huat Ah!")
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

'''
Calculate Functions - Command Handlers
'''
yf.pdr_override()
def calculate(update: Update, context: CallbackContext) -> None:
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

'''
Inline Keyboard Buttons
'''
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    choice = query.data
    
    # Define what choice do what
    if choice == 'Yes':
        clear_wallet(update, context)


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


    if choice == 'Clear All':
        clear_all(update, context)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(API_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
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
    
    conv_handler_1 = ConversationHandler (
        entry_points=[CallbackQueryHandler(button)],
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
    
    # conv_handler_2 = ConversationHandler (
    #     entry_points=[CallbackQueryHandler(button)],
    #     states={
    #         REMOVE: [
    #             CommandHandler('cancel', cancel),  # has to be before MessageHandler to catch `/cancel` as command, not as `title`
    #             MessageHandler(Filters.text, remove)
    #         ],
    #         CHECK: [
    #             CommandHandler('cancel', cancel),
    #             MessageHandler(Filters.text, check)
    #         ]
    #     },
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )
    
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("wallet", check))
    dispatcher.add_handler(CommandHandler("gmma", gmma))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    dispatcher.add_handler(CommandHandler("calculate", calculate))
    dispatcher.add_handler(CommandHandler("clear_all", clear_all))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(conv_handler_1)
#    dispatcher.add_handler(conv_handler_2)
    dispatcher.add_handler(CallbackQueryHandler(button))

    # on non command i.e message - echo the message on Telegram
    #dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()