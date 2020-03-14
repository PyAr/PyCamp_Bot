import peewee
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from pycamp_bot.commands.base import msg_to_active_pycamp_chat
from pycamp_bot.commands.auth import admin_needed
from pycamp_bot.commands.manage_pycamp import active_needed, get_active_pycamp
from pycamp_bot.models import Pycampista, Project, Vote

import logging


logger = logging.getLogger(__name__)


def vote_authorized(f):
    def wrap(*args, **kargs):
        logger.info('Vote authorized wrapper')

        bot, update = args
        is_active, pycamp = get_active_pycamp()
        if pycamp.vote_authorized:
            f(*args)
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="La votacion no está autorizada. Avisale a un admin\
                (/admins)!")
    return wrap


@admin_needed
@active_needed
def start_voting(bot, update):
    logger.info("Empezando la votacion")

    is_active, pycamp = get_active_pycamp()

    if not pycamp.vote_authorized:
        pycamp.vote_authorized = True
        pycamp.save()
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
    new_vote = Vote(
        pycampista=user,
        project=project,
        _project_pycampista_id="{}-{}".format(project.id, user.id),
    )

    # Save vote in the database and send a message
    if query.data == "si":
        result = 'Interesadx en: ' + project_name + ' 👍'
        new_vote.interest = True
    else:
        new_vote.interest = False
        result = 'No te interesa el proyecto ' + project_name

    try:
        new_vote.save()
        bot.edit_message_text(text=result,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    except peewee.IntegrityError:
        logger.warning("Error al guardar el voto de {} del proyecto {}".format(
            username,
            project_name
        ))
        bot.edit_message_text(
            text="Ya habías votado el proyecto {}!!".format(project_name),
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )


@vote_authorized
def vote(bot, update):
    logger.info("Vote message")

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


@admin_needed
@active_needed
@vote_authorized
def end_voting(bot, update):
    is_active, pycamp = get_active_pycamp()

    pycamp.vote_authorized = False
    pycamp.save()
    update.message.reply_text("Votación cerrada")
    msg_to_active_pycamp_chat(bot, "La Votación esta cerrada")


def set_handlers(updater):
    updater.dispatcher.add_handler(
        CallbackQueryHandler(button))
    updater.dispatcher.add_handler(
        CommandHandler('empezar_votacion', start_voting))
    updater.dispatcher.add_handler(
        CommandHandler('votar', vote))
    updater.dispatcher.add_handler(
        CommandHandler('terminar_votacion', end_voting))
