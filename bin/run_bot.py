import os

from telegram.ext import Application, MessageHandler, filters
import sentry_sdk

from pycamp_bot.commands import auth
from pycamp_bot.commands import voting
from pycamp_bot.commands import manage_pycamp
from pycamp_bot.commands import projects
from pycamp_bot.commands import wizard
from pycamp_bot.commands import base
from pycamp_bot.commands import raffle
from pycamp_bot.commands import schedule
from pycamp_bot.commands import announcements
from pycamp_bot.commands import devtools
from pycamp_bot.models import models_db_connection
from pycamp_bot.logger import logger


SENTRY_DATA_SOURCE_NAME_ENVVAR = 'SENTRY_DATA_SOURCE_NAME'
if SENTRY_DATA_SOURCE_NAME_ENVVAR in os.environ:
    sentry_sdk.init(dsn=os.environ[SENTRY_DATA_SOURCE_NAME_ENVVAR])


async def unknown_command(update, context):
    text = "No reconozco el comando, para ver comandos válidos usá /ayuda"
    await context.bot.send_message(chat_id=update.message.chat_id, text=text)


def set_handlers(application):
    base.set_handlers(application)
    auth.set_handlers(application)
    wizard.set_handlers(application)
    voting.set_handlers(application)
    manage_pycamp.set_handlers(application)
    projects.set_handlers(application)
    raffle.set_handlers(application)
    schedule.set_handlers(application)
    announcements.set_handlers(application)
    devtools.set_handlers(application)
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))


if __name__ == '__main__':
    logger.info('Starting PyCamp Bot')

    if 'TOKEN' in os.environ.keys():
        models_db_connection()

        application = Application.builder().token(os.environ['TOKEN']).build()
    # application.add_handler(CommandHandler("start", start))
        set_handlers(application)
        application.run_polling()

    else:
        logger.info('Token not defined. Exiting.')
