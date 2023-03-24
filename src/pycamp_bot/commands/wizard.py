from telegram.ext import CommandHandler
from pycamp_bot.models import Pycampista


def become_wizard(bot, update):
    current_wizards = Pycampista.select().where(Pycampista.wizard is True)

    for w in current_wizards:
        w.current = False
        w.save()

    username = update.message.from_user.username
    chat_id = update.message.chat_id

    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]
    user.wizard = True
    user.save()

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Felicidades! Eres el Magx de turno"
    )


def summon_wizard(bot, update):
    username = update.message.from_user.username
    try:
        wizard = Pycampista.get(Pycampista.wizard is True)
        bot.send_message(
            chat_id=wizard.chat_id,
            text="PING PING PING MAGX! @{} te necesesita!".format(username)
        )
    except Pycampista.DoesNotExist:
        bot.send_message(
            chat_id=update.chat_id,
            text="Hubo un accidente, el mago esta en otro plano.".format(username)
        )


def set_handlers(updater):
    updater.dispatcher.add_handler(
            CommandHandler('evocar_magx', summon_wizard))
    updater.dispatcher.add_handler(
            CommandHandler('ser_magx', become_wizard))
