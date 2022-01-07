from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

#Load Telegram Bot Token
import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("TOKEN")
ADD, REMOVE, CHECK = range(3)

# Enable logging
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


wallet = {}

# Command Handlers
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


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    user = update.effective_user
    update.message.reply_markdown_v2 (
        fr'What would you like me to do, {user.mention_markdown_v2()}\?',
        reply_markup=ForceReply(selective=True),
    )


def new_entry(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Insert stocks to your wallet.\n\n Type in the stock symbol, amount and price \n separated by a space (e.g AAPL 10 172.00):")
    return ADD

def add(update: Update, context: CallbackContext) -> int:
    """Put the entry into the wallet"""
    # Obtain data from text
    inputs = update.message.text.split(" ")
    to_add = [inputs[0].upper(), int(inputs[1]), float("{:.2f}".format(float(inputs[2])))]
    #try: check valid symbol here
    if to_add[0] in wallet:
        update.message.reply_text("Stock already added. Try again")
        return ADD
    else:
        wallet[to_add[0]] = to_add[1:]
        update.message.reply_text("Added successfully.")
        return check(update, context)
    #except: 
    #    update.message.reply_text("Invalid entry. Try again")
    #    return ADD


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
        update.message.reply_text("Remove stock from your wallet. \n\n Type in the stock symbol and amount \n separated by a space (e.g AAPL 10 ):")
        check(update, context)
    return REMOVE

def remove(update: Update, context: CallbackContext) -> int:
    inputs = update.message.text.split(" ")
    sym = inputs[0].upper()
    amt = int(inputs[1])
    #try: check valid symbol here
        
    if sym not in wallet:
        update.message.reply_text("No stocks found. Try again")
        return REMOVE
    else:
        if amt <= 0 or amt > wallet[sym][0]:
            update.message.reply_text("Invalid amount. Try again")
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
    # except:
    #     update.message.reply_text("Invalid entry. Try again")
    #     return REMOVE

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('canceled')
    # end of conversation
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(API_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
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