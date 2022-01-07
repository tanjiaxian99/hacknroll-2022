import os
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from backtest import backtesting

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

'''
Backtesting Functions - Command Handlers
'''

def backtest(update: Update, context: CallbackContext) -> int:
    global data
    
    """Create new empty dictionary"""
    data = {'symbol': "", 'date' : ""}
    update.message.reply_text("Backtest using Guppy Multiple Moving Average!\n\nType in the stock symbol to backtest (e.g AAPL):")
    return SYMBOL

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
        update.message.reply_text("You did not type in the correct symbol or date.\n\nTry again or press /cancel to quit.\n\nType in the stock symbol to backtest (e.g AAPL):")
        return SYMBOL
    else: 
        update.message.reply_text(f"Backtesting {data['symbol'].upper()} from: {update.message.text[0:2]}/{update.message.text[2:4]}/{update.message.text[4:]}" )
        update.message.reply_text(f"Stock: {results['stock'].upper()}\nSample Size: {results['sample_size']}\nEMAs Used: {results['EMAs_used']}\nBatting Average: {results['Batting_Avg']}\nGain Loss Ratio: {results['GainLoss_ratio']}\nAverage Gain: {results['Average_Gain']}\nAverage Loss: {results['Average_Loss']}\nMax Return: {results['Max_Return']}\nMax Loss: {results['Max_Loss']}\nTotal Return: {results['Total_return']}")
        update.message.reply_text("If you want to learn more about the indicator used (i.e GMMA), type /gmma")
        return ConversationHandler.END


def gmma(update: Update, context: CallbackContext) -> None:
    msg = "GMMA is a technical indicator that identifies changes in trends, providing an objective method to know when to get in and when to get out of a trade."
    msg2 = "6 short-term EMAs in red (3, 5, 8, 10, 12, 15), and 6 long-term EMAs in blue (30, 35, 40, 35, 50, 60) are used.\n\nWhen red crosses above blue (i.e Red White Blue), it is a Buy Signal.\n\nWhen blue crosses above red (i.e Blue White Red), it is a Sell Signal."
    update.message.reply_text(msg)
    update.message.reply_text(msg2)
    
'''
Wallet Functions - Command Handlers
'''

def new_entry(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Insert stocks to your wallet.\n\nType in the stock symbol, amount and price, \nseparated by a space (e.g AAPL 10 172.00):")
    return ADD

def add(update: Update, context: CallbackContext) -> int:
    """Put the entry into the wallet"""
    # Obtain data from text
    inputs = update.message.text.split(" ")
    to_add = [inputs[0].upper(), int(inputs[1]), float("{:.2f}".format(float(inputs[2])))] 
    return error_add(update, context, to_add)

def error_add(update: Update, context: CallbackContext, to_add) -> None:
    try:
        results = backtesting(to_add[0], '01', '01', '2020')
        if to_add[0] in wallet:
            update.message.reply_text("Stock has already been added.\nTry to add again or type /cancel to quit.")
            update.message.reply_text("Type in the stock symbol, amount and price,\nseparated by a space (e.g AAPL 10 172.00):")
            return ADD
        else:
            wallet[to_add[0]] = to_add[1:]
            update.message.reply_text("Added successfully.")
            return check(update, context)
    except: 
        update.message.reply_text("You did not type in the correct symbol.\nTry to add again or type /cancel to quit.")
        update.message.reply_text("Type in the stock symbol, amount and price,\nseparated by a space (e.g AAPL 10 172.00):")
        return ADD

def check(update: Update, context: CallbackContext) -> None:
    """Check current wallet"""
    if len(wallet) == 0:
        update.message.reply_text("Your wallet is currently empty")
    else:
        sortedWallet = sorted(wallet.keys())
        update.message.reply_text("Your wallet:")
        for i in sortedWallet:
            update.message.reply_text("{}, Amount: {}, Price: {}".format(i, wallet[i][0], wallet[i][1]))
    return ConversationHandler.END

def remove_entry(update: Update, context: CallbackContext) -> int:
    """Remove stock from wallet"""
    if len(wallet) == 0:
        update.message.reply_text("Your wallet is currently empty")
    else:
        update.message.reply_text("Remove stock from your wallet.\n\nType in the stock symbol and amount,\nseparated by a space (e.g AAPL 10 ):")
        check(update, context)
    return REMOVE

def remove(update: Update, context: CallbackContext) -> int:
    inputs = update.message.text.split(" ")
    sym = inputs[0].upper()
    amt = int(inputs[1])
    return error_remove(update, context, sym, amt)

def error_remove(update: Update, context: CallbackContext, sym, amt) -> None:
    try:
        results = backtesting(sym, '01', '01', '2020')
        if sym not in wallet:
            update.message.reply_text("No such stock found in your wallet. Try again or type /cancel to quit")
            update.message.reply_text("Remove stock from your wallet.\n\nType in the stock symbol and amount,\nseparated by a space (e.g AAPL 10):")
            return REMOVE
        else:
            if amt <= 0 or amt > wallet[sym][0]:
                update.message.reply_text("Invalid amount.\nTry to remove again or type /cancel to quit")
                update.message.reply_text("Type in the stock symbol and amount,\nseparated by a space (e.g AAPL 10):")
                return REMOVE
            elif amt == wallet[sym][0]:
                wallet.pop(sym)
                update.message.reply_text("Removed successfully.")
                return check(update, context)
            else:
                old = wallet[sym]
                wallet[sym] = [old[0]-amt, old[1]]
                update.message.reply_text("Removed successfully.")
                return check(update, context)
    except:
        update.message.reply_text("Invalid entry.\nTry to remove again or type /cancel to quit.")
        update.message.reply_text("Type in the stock symbol and amount,\nseparated by a space (e.g AAPL 10):")
        return REMOVE

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
        entry_points=[CommandHandler('add', new_entry)],
        states={
            ADD: [
                CommandHandler('cancel', cancel),  # has to be before MessageHandler to catch `/cancel` as command, not as `title`
                MessageHandler(Filters.text, add)
            ],
            CHECK: [
                CommandHandler('cancel', cancel),
                MessageHandler(Filters.text, check)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    conv_handler_2 = ConversationHandler (
        entry_points=[CommandHandler('remove', remove_entry)],
        states={
            REMOVE: [
                CommandHandler('cancel', cancel),  # has to be before MessageHandler to catch `/cancel` as command, not as `title`
                MessageHandler(Filters.text, remove)
            ],
            CHECK: [
                CommandHandler('cancel', cancel),
                MessageHandler(Filters.text, check)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("check", check))
    dispatcher.add_handler(CommandHandler("gmma", gmma))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(conv_handler_1)
    dispatcher.add_handler(conv_handler_2)

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