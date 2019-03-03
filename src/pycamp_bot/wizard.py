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
    wizard = Wizard.get(Wizard.current is True)
    bot.send_message(
        chat_id=wizard.chat_id,
        text="PING PING PING MAGX! @{} te necesesita!".format(username)
    )
