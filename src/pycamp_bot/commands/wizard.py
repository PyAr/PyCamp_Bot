from telegram.ext import CommandHandler
from pycamp_bot.models import Pycampista
import random


async def become_wizard(update, context):
    current_wizards = Pycampista.select().where(Pycampista.wizard is True)

    for w in current_wizards:
        w.current = False
        w.save()

    username = update.message.from_user.username
    chat_id = update.message.chat_id

    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]
    user.wizard = True
    user.save()

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Felicidades! Eres el Magx de turno"
    )


async def summon_wizard(update, context):
    username = update.message.from_user.username
    wizard_list = list(Pycampista.select().where(Pycampista.wizard==True))
    if len(wizard_list) == 0:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="No hay ningunx magx todavia"
        )
    else:
        wizard = random.choice(wizard_list)
        await context.bot.send_message(
            chat_id=wizard.chat_id,
            text="PING PING PING MAGX! @{} te necesita!".format(username)
        )
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Tu magx asignadx es: @{}".format(wizard.username)
        )

def set_handlers(application):
    application.add_handler(
            CommandHandler('evocar_magx', summon_wizard))
    application.add_handler(
            CommandHandler('ser_magx', become_wizard))
