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

