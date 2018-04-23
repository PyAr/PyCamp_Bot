#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Bot to reply to Telegram messages.
This is built on the API wrapper, see echobot2.py to see the same example built
on the telegram.ext bot framework.
This program is dedicated to the public domain under the CC0 license.
"""
import logging
import telegram
from telegram.ext import CommandHandler
import json
import imput_projects
from pprint import pprint
from telegram.error import NetworkError, Unauthorized
from time import sleep


update_id = None


def main():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot('357811653:AAFaLB_tXns3LchYECBNyy-Swa6h4FbGEDc')

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1


def echo(bot):
    """Echo the message the user sent."""
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        pprint (update)
        update_id = update.update_id + 1
        # start_handler = CommandHandler('start', start)
        # update.add_handler(start_handler)
        if update.message:  # your bot can receive updates without messages
            # Reply to the message
            print (update.message.text)
            if update.message.text == "/insert_proyect":
                update.message.reply_text("holi :)")
                imput_projects.insert_proyect(update)




if __name__ == '__main__':
    main()
###

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
