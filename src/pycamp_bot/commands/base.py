import logging
from telegram.ext import CommandHandler
from pycamp_bot.commands.help_msg import get_help


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

    if update.message.from_user.username is None:
        bot.send_message(
                chat_id=chat_id,
                text="""Hola! Necesitas tener un username primero.
                        \nCreate uno siguiendo esta guia: https://ewtnet.com/technology/how-to/how-to-add-a-username-on-telegram-android-app.
                        Y despues dame /start the nuevo :) """)

    elif update.message.from_user.username:
        bot.send_message(
                chat_id=chat_id,
                text='Hola ' + update.message.from_user.username +
                     '! Bienvenidx'
                )


def help(bot, update):
    logger.info('Returning help message')
    bot.send_message(chat_id=update.message.chat_id, text=get_help(bot, update))


def error(bot, update, error):
    '''Log Errors caused by Updates.'''
    logger.warning('Update {} caused error {}'.format(update, error))


def set_handlers(updater):
    updater.dispatcher.add_error_handler(error)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('ayuda', help))
