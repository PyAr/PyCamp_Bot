from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from manage_pycamp import ping_PyCamp_group, is_auth
from models import Pycampista, Project, ProjectOwner, Slot, Vote, Wizard

import logging


logger = logging.getLogger(__name__)
vote_auth = False


def start_voting(bot, update):
    logger.info("Empezando la votacion")
    global vote_auth

    if not is_auth(bot, update.message.from_user.username):
        logging.info("Usuario no autorizado")
        return

    if not vote_auth:
        # ping_PyCamp_group(bot, "La Votación esta abierta")
        update.message.reply_text("Autorizadx \nVotación Abierta")
        vote_auth = True
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
        new_vote.save(force_insert=True)
    else:
        new_vote.interest = False
        new_vote.save(force_insert=True)
        result = 'No te interesa el proyecto ' + project_name

    bot.edit_message_text(text=result,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def vote(bot, update):
    logger.info("Vote message")

    if vote_auth:
        update.message.reply_text(
            'Te interesa el proyecto:'
        )

        # if there is not project in the database, create a new project
        if not Project.select().exists():
            Project.create(name='PROYECTO DE PRUEBA')

        # ask user for each project in the database
        for project in Project.select():
            keyboard = [[InlineKeyboardButton("Si!" , callback_data="si"),
                        InlineKeyboardButton("Nop", callback_data="no")]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            update.message.reply_text(
                text=project.name,
                reply_markup=reply_markup
            )
    else:
        update.message.reply_text("Votación Cerrada")


def end_voting(bot, update):
    """Ends voting mode, sets variable vote_auth to False"""

    if not is_auth(bot, update.message.from_user.username):
        return

    global vote_auth

    if vote_auth:
        vote_auth = False
        # ping_PyCamp_group(bot,"La Votación esta cerrada")
        update.message.reply_text("Autorizadx \nVotación cerrada")
    else:
        update.message.reply_text("La votación ya estaba cerrada")
