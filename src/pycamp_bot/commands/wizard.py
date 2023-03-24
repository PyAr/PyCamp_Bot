from telegram.ext import CommandHandler
from pycamp_bot.models import Pycampista


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
    try:
        wizard = Pycampista.get(Pycampista.wizard is True)
        await context.bot.send_message(
            chat_id=wizard.chat_id,
            text="PING PING PING MAGX! @{} te necesesita!".format(username)
        )
    except Pycampista.DoesNotExist:
        await context.bot.send_message(
            chat_id=update.chat_id,
            text="Hubo un accidente, el mago esta en otro plano.".format(username)
        )


def set_handlers(application):
    application.add_handler(
            CommandHandler('evocar_magx', summon_wizard))
    application.add_handler(
            CommandHandler('ser_magx', become_wizard))
