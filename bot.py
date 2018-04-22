import logging

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


# Pycamp vote
def vote(bot, update):
    project = 'JUEGO CON ESPADAS'
    keyboard = [[InlineKeyboardButton("Si!", callback_data="si"),
                 InlineKeyboardButton("Nop", callback_data="no")]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        'Te interesa el proyecto: {}?'.format(project),
        reply_markup=reply_markup
    )


def button(bot, update):
    query = update.callback_query
    if query.data == "si":
        result = 'Te interesa el proyecto'
    else:
        result = 'No te interesa el proyecto'
    bot.edit_message_text(text=result,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

updater.dispatcher.add_handler(CommandHandler('vote', vote))
updater.dispatcher.add_handler(CallbackQueryHandler(button))


# repeat all messages user send to bot
def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


updater.dispatcher.add_error_handler(error)
