import logging
from pycamp_bot.scheduler.scheduler import internal_export
from pycamp_bot.scheduler.db_to_json import internal_json

from telegram.ext import CommandHandler

logger = logging.getLogger(__name__)

def make_schedule(bot, update):
    data_json = internal_json()
    my_schedule = internal_export(data_json)
    logger.info(my_schedule)

def set_handlers(updater):
    updater.dispatcher.add_handler(CommandHandler('cronogramear', make_schedule))
