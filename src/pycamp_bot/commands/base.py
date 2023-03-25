import logging
from telegram.ext import CommandHandler
from pycamp_bot.commands.help_msg import get_help


logger = logging.getLogger(__name__)


async def msg_to_active_pycamp_chat(bot, text):
    chat_id = -220368252  # Prueba
    await bot.send_message(
        chat_id=chat_id,
        text=text
        )


async def start(update, context):
    logger.info('Start command')
    chat_id = update.message.chat_id

    if update.message.from_user.username is None:
        await context.bot.send_message(
                chat_id=chat_id,
                text="""Hola! Necesitas tener un username primero.
                        \nCreate uno siguiendo esta guia: https://ewtnet.com/technology/how-to/how-to-add-a-username-on-telegram-android-app.
                        Y despues dame /start the nuevo :) """)

    elif update.message.from_user.username:
        await context.bot.send_message(
                chat_id=chat_id,
                text='Hola ' + update.message.from_user.username +
                     '! Bienvenidx'
                )


async def help(update, context):
    logger.info('Returning help message')
    await context.bot.send_message(chat_id=update.message.chat_id, text=get_help(update, context))


# async def error(update, context):
#     '''Log Errors caused by Updates.'''
#     logger.warning('Update {} caused error {}'.format(update, context.error))


def set_handlers(application):
#     application.add_error_handler(error)

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('ayuda', help))
