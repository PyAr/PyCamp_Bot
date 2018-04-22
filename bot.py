import logging

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import vote

updater = Updater(token='357811653:AAFaLB_tXns3LchYECBNyy-Swa6h4FbGEDc')
dispatcher = updater.dispatcher


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


updater.start_polling()


# command /start give usear a message
def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Hello world! I want to talk with you')


def button(bot, update):
    query = update.callback_query
    if query.data == "si":
        result = 'Te interesa el proyecto'
    else:
        result = 'No te interesa el proyecto'
    bot.edit_message_text(text=result,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


# repeat all messages user send to bot
def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

updater.dispatcher.add_handler(CommandHandler('vote', vote.vote))
updater.dispatcher.add_handler(CallbackQueryHandler(button))



def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


updater.dispatcher.add_error_handler(error)
