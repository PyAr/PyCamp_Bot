from datetime import date, datetime

from telegram.ext import CommandHandler

from pycamp_bot.commands.auth import admin_needed

date_start_pycamp = None


def is_pycamp_started(update):
    global date_start_pycamp
    if date_start_pycamp:
        return True
    else:
        update.message.reply_text(text="PyCamp no ha comenzado")
        return False


@admin_needed
def start_pycamp(bot, update):
    global date_start_pycamp

    if is_pycamp_started(update):
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


@admin_needed
def end_pycamp(bot, update):
    bot.send_message(
            chat_id=update.message.chat_id,
            text="Terminó Pycamp :( !"
        )


def set_handlers(updater):
    updater.dispatcher.add_handler(
            CommandHandler('empezar_pycamp', start_pycamp))
    updater.dispatcher.add_handler(
            CommandHandler('terminar_pycamp', end_pycamp))
