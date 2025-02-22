import functools
import peewee
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from pycamp_bot.commands.base import msg_to_active_pycamp_chat
from pycamp_bot.commands.auth import admin_needed
from pycamp_bot.commands.manage_pycamp import active_needed, get_active_pycamp
from pycamp_bot.models import Pycampista, Project, Vote
from pycamp_bot.logger import logger


VOTE_PATTERN = 'vote'


def vote_authorized(func):
    @functools.wraps(func)
    async def wrap(*args):
        logger.info('Vote authorized wrapper')

        update, context = args
        is_active, pycamp = get_active_pycamp()
        if pycamp.vote_authorized:
            await func(update, context)
        else:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="La eleccion no está autorizada. Avisale a un admin (/admins)!")
    return wrap


@admin_needed
@active_needed
async def start_voting(update, context):
    logger.info("Empezando la seleccion.")

    is_active, pycamp = get_active_pycamp()

    if not pycamp.vote_authorized:
        pycamp.vote_authorized = True
        pycamp.save()
        await update.message.reply_text("Autorizadx. \nSelección Abierta.")
        await msg_to_active_pycamp_chat(context.bot, "La elección de proyectos esta abierta!")
    else:
        await update.message.reply_text("La eleccion ya estaba abierta.")


async def button(update, context):
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
        _project_pycampista_id=f"{project.id}-{user.id}"
    )

    # Save vote in the database and confirm the chosen proyects.

    if query.data.split(':')[1] == "si":
        result = f"✅ Sumade a {project_name}!"
        new_vote.interest = True
    else:
        new_vote.interest = False
        result = f'❌ Proyecto {project_name} salteado.'

    try:
        new_vote.save()
        await context.bot.edit_message_text(text=result,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    except peewee.IntegrityError:
        logger.warning(f"Error al guardar la eleccion de {username} en el proyecto {project_name}")
        await context.bot.edit_message_text(
            text=f"Ya te habías sumado al proyecto {project_name}!",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )


@vote_authorized
async def vote(update, context):
    logger.info("Vote message")

    await update.message.reply_text(
        'Te interesa el proyecto:'
    )

    # if there is not project in the database, create a new project
    if not Project.select().exists():
        Project.create(name='PROYECTO DE PRUEBA')

    # ask user for each project in the database
    for project in Project.select():
        keyboard = [[InlineKeyboardButton("Me Sumo!", callback_data=f"{VOTE_PATTERN}:si"),
                    InlineKeyboardButton("Paso", callback_data=f"{VOTE_PATTERN}:no")]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=project.name,
            reply_markup=reply_markup
        )


@admin_needed
@active_needed
@vote_authorized
async def end_voting(update, context):
    is_active, pycamp = get_active_pycamp()

    pycamp.vote_authorized = False
    pycamp.save()
    await update.message.reply_text("Selección cerrada")
    await msg_to_active_pycamp_chat(context.bot, "La selección de proyectos ha finalizado.")

async def vote_count(update, context):
    votes = [vote.pycampista_id for vote in Vote.select()]
    vote_count = len(set(votes))
    await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Votaron: {vote_count}"
        )


def set_handlers(application):
    application.add_handler(
        CallbackQueryHandler(button, pattern=VOTE_PATTERN))
    application.add_handler(
        CommandHandler('empezar_votacion_proyectos', start_voting))
    application.add_handler(
        CommandHandler('votar', vote))
    application.add_handler(
        CommandHandler('terminar_votacion_proyectos', end_voting))
    application.add_handler(
        CommandHandler('contar_votos', vote_count))
