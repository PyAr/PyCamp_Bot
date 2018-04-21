import logging

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
     CallbackQueryHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


updater = Updater(token='448602941:AAHXrYB7Yj67dzNwsco6-L-fJbdFBz9g7zI')
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


# repeat all messages user send to bot
def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)
