import logging
import os
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler, ConversationHandler)

from pycamp_bot.commands import voting
from pycamp_bot.commands import manage_pycamp
from pycamp_bot.commands import projects
from pycamp_bot.commands import wizard
from pycamp_bot.commands import base
from pycamp_bot.commands import raffle

from pycamp_bot.models import models_db_connection


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


def set_handlers(updater):
    base.set_handlers(updater)
    wizard.set_handlers(updater)
    voting.set_handlers(updater)
    manage_pycamp.set_handlers(updater)
    projects.set_handlers(updater)
    raffle.set_handlers(updater)


if __name__ == '__main__':
    logger.info('Starting PyCamp Bot')

    token = os.environ.get('TOKEN')
    if token is None:
        logger.error('Token not defined. Exiting.')
        exit(1)

    updater = Updater(token=token)

    models_db_connection()
    set_handlers(updater)

    updater.start_polling()
