import logging
import sys
import os
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler, ConversationHandler)


from pycamp_bot import voting
from pycamp_bot import manage_pycamp
from pycamp_bot import projects
from pycamp_bot import wizard
from pycamp_bot import base_commands
from pycamp_bot import raffle

from pycamp_bot.models import models_db_connection


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


def set_handlers(updater):
    base_commands.set_handlers(updater)
    wizard.set_handlers(updater)
    voting.set_handlers(updater)
    manage_pycamp.set_handlers(updater)
    projects.set_handlers(updater)
    raffle.set_handlers(updater)


if __name__ == '__main__':
    logger.info('Starting PyCamp Bot')

    if 'TOKEN' in os.environ.keys():
        updater = Updater(token=os.environ['TOKEN'])
        dispatcher = updater.dispatcher

        users_status = {}
        current_projects = {}

        updater.start_polling()

        set_handlers(updater, dispatcher)
        models_db_connection(eval(sys.argv[1]))
    else:
        logger.info('Token not defined. Exiting.')
