import random
from telegram.ext import CommandHandler
from pycamp_bot.models import Pycampista
from pycamp_bot.commands.auth import admin_needed


@admin_needed
async def get_random_user(update, context):
    cantidad_campistas = Pycampista.select().count()
    index_random = random.randint(1,cantidad_campistas)
    user_name = Pycampista.get_by_id(index_random).username
    await update.message.reply_text(user_name)

def set_handlers(application):
    application.add_handler(
        CommandHandler('rifar', get_random_user))
   