import random
from telegram.ext import CommandHandler
from pycamp_bot.models import Pycampista
from pycamp_bot.commands.auth import admin_needed


@admin_needed
def raffle(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Voy a sortear algo entre todxs lxs Pycampistas!"
        )
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Y la persona ganadora eeeeeeeeeeeeessss...."
        )
    pycampistas = Pycampista.select(Pycampista.username)
    lista_pycampistas = [persona.username for persona in pycampistas]
    persona_ganadora = random.choice(lista_pycampistas)
    bot.send_message(
        chat_id=update.message.chat_id,
        text="@{}".format(persona_ganadora)
        )


def set_handlers(updater):
    updater.dispatcher.add_handler(
            CommandHandler('sorteo', raffle))
