import logging
import os
from telegram.ext import Application
from pycamp_bot.commands import auth
from pycamp_bot.commands import voting
from pycamp_bot.commands import manage_pycamp
from pycamp_bot.commands import projects
from pycamp_bot.commands import wizard
from pycamp_bot.commands import base
from pycamp_bot.commands import raffle
from pycamp_bot.commands import schedule
from pycamp_bot.commands import announcements
from pycamp_bot.models import models_db_connection


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


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


if __name__ == '__main__':
    logger.info('Starting PyCamp Bot')

    # escribo environ para pruebas por no poder pasar kargs en consola windows
    os.environ['TOKEN'] = '6166771762:AAGifhVfpIpvqL6EZVJ3YnVK7r1YG9C5OME'

    if 'TOKEN' in os.environ.keys():
        models_db_connection()

        application = Application.builder().token(os.environ['TOKEN']).build()
    # application.add_handler(CommandHandler("start", start))
        set_handlers(application)
        application.run_polling()

    else:
        logger.info('Token not defined. Exiting.')
