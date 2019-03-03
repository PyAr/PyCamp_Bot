from datetime import date, datetime

from telegram.ext import CommandHandler


date_start_pycamp = None


def is_auth(bot, username):
    """Checks if the user is authorized"""
    authorized = ["WinnaZ", "sofide", "ArthurMarduk", "xcancerberox"]

    if username not in authorized:
        bot.send_message("No estas Autorizadx para hacer esta acción")
        return False
    else:
        return True


def is_pycamp_started(update):
    global date_start_pycamp
    if date_start_pycamp:
        return True
    else:
        update.message.reply_text(text="PyCamp no ha comenzado")
        return False


def ping_PyCamp_group(bot, text):
    chat_id = -220368252  # Prueba
    # chat_id = -1001326267611 #Posta
    bot.send_message(
        chat_id=chat_id,
        text=text
                    )


def start_pycamp(bot, update):
    global date_start_pycamp
    if not is_auth(bot, update.message.from_user.username):
        return

    if is_pycamp_started:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="PyCamp Ya habia empezado ! {}".format(str(date_start_pycamp))
        )
        return

    date_start_pycamp = date.today()
    bot.send_message(
            chat_id=update.message.chat_id,
            text="Empezó Pycamp :) ! {}".format(str(date_start_pycamp))
        )


def end_pycamp(bot, update):
    if not is_auth(bot, update.message.from_user.username):
        return

    bot.send_message(
            chat_id=update.message.chat_id,
            text="Terminó Pycamp :( !"
        )


def set_handlers(updater):
    updater.dispatcher.add_handler(
            CommandHandler('empezar_pycamp', start_pycamp))
    updater.dispatcher.add_handler(
            CommandHandler('terminar_pycamp', end_pycamp))
