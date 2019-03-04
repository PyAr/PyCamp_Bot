from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from pycamp_bot.commands.base import msg_to_active_pycamp_chat
from pycamp_bot.commands.auth import admin_needed
from pycamp_bot.models import Pycampista, Project, Vote, BotStatus

import logging


logger = logging.getLogger(__name__)

vote_auth = False


@admin_needed
def start_voting(bot, update):
    logger.info("Empezando la votacion")

    bot_status = BotStatus.select()[0]

    if not bot_status.vote_authorized:
        bot_status.vote_authorized = True
        bot_status.save()
        update.message.reply_text("Autorizadx \nVotación Abierta")
        msg_to_active_pycamp_chat(bot, "La Votación esta abierta")
    else:
        update.message.reply_text("La votacion ya estaba abierta")


def button(bot, update):
    '''Save user vote in the database'''
    query = update.callback_query
    username = query.message['chat']['username']
    chat_id = query.message.chat_id
    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]
    project_name = query.message['text']

    # Get project from the database
    project = Project.get(Project.name == project_name)

    # create a new vote object
    new_vote = Vote(pycampista=user, project=project)

    # Save vote in the database and send a message
    if query.data == "si":
        result = 'Interesadx en: ' + project_name + ' 👍'
        new_vote.interest = True
        new_vote.save()
    else:
        new_vote.interest = False
        new_vote.save()
        result = 'No te interesa el proyecto ' + project_name

    bot.edit_message_text(text=result,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def vote(bot, update):
    logger.info("Vote message")

    bot_status = BotStatus.select()[0]

    if bot_status.vote_authorized:
        update.message.reply_text(
            'Te interesa el proyecto:'
        )

        # if there is not project in the database, create a new project
        if not Project.select().exists():
            Project.create(name='PROYECTO DE PRUEBA')

        # ask user for each project in the database
        for project in Project.select():
            keyboard = [[InlineKeyboardButton("Si!", callback_data="si"),
                        InlineKeyboardButton("Nop", callback_data="no")]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            update.message.reply_text(
                text=project.name,
                reply_markup=reply_markup
            )
    else:
        update.message.reply_text("Votación Cerrada")


@admin_needed
def end_voting(bot, update):
    bot_status = BotStatus.select()[0]

    if bot_status.vote_authorized:
        bot_status.vote_authorized = False
        bot_status.save()
        update.message.reply_text("Autorizadx \nVotación cerrada")
        msg_to_active_pycamp_chat(bot, "La Votación esta cerrada")
    else:
        update.message.reply_text("La votación ya estaba cerrada")


def set_handlers(updater):
    updater.dispatcher.add_handler(
            CallbackQueryHandler(button))
    updater.dispatcher.add_handler(
            CommandHandler('empezar_votacion', start_voting))
    updater.dispatcher.add_handler(
            CommandHandler('votar', vote))
    updater.dispatcher.add_handler(
            CommandHandler('terminar_votacion', end_voting))
