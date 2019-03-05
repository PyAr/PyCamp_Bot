import logging

from telegram.ext import CommandHandler

from pycamp_bot.models import Pycampista
from pycamp_bot.commands.help_msg import HELP_MESSAGE


logger = logging.getLogger(__name__)


def msg_to_active_pycamp_chat(bot, text):
    chat_id = -220368252  # Prueba
    bot.send_message(
        chat_id=chat_id,
        text=text
        )


def start(bot, update):
    logger.info('Start command')
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]
    user.save()
    logger.debug("Pycampista {} agregado a la DB".format(user.username))

    if username is None:
        bot.send_message(
                chat_id=chat_id,
                text="""Hola! Necesitas tener un username primero.
                        \nCreate uno siguiendo esta guia: https://ewtnet.com/technology/how-to/how-to-add-a-username-on-telegram-android-app.
                        Y despues dame /start the nuevo :) """)

    elif username:
        bot.send_message(
                chat_id=chat_id,
                text='Hola ' + username + '! Bienvenidx'
                )


def help(bot, update):
    logger.info('Returning help message')
    bot.send_message(chat_id=update.message.chat_id, text=HELP_MESSAGE)


def error(bot, update, error):
    '''Log Errors caused by Updates.'''
    logger.warning('Update {} caused error {}'.format(update, error))


def set_handlers(updater):
    updater.dispatcher.add_error_handler(error)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('ayuda', help))
