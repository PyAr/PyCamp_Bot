import logging
import peewee
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ConversationHandler, CommandHandler, MessageHandler, filters
from pycamp_bot.models import Pycampista, Project, Slot, Vote
from pycamp_bot.commands.base import msg_to_active_pycamp_chat
from pycamp_bot.commands.manage_pycamp import active_needed, get_active_pycamp
from pycamp_bot.commands.auth import admin_needed, get_admins_username
from pycamp_bot.commands.schedule import DIAS
from pycamp_bot.utils import escape_markdown


current_projects = {}

NOMBRE = "nombre"
DIFICULTAD = "dificultad"
TOPIC = "topic"
CHECK_REPOSITORIO = "check_repositorio"
REPOSITORIO = "repositorio"

REPO_EXISTS_PATTERN = 'repoexists'
PROJECT_NAME_PATTERN = 'projectname'

logger = logging.getLogger(__name__)


def load_authorized(f):
    async def wrap(*args, **kargs):
        logger.info('Load authorized wrapper')

        update, context = args
        is_active, pycamp = get_active_pycamp()
        if pycamp.project_load_authorized:
            return await f(*args, **kargs)
        else:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="La carga de proyectos no está autorizada. Avisale a un\
                admin (/admins)!")
    return wrap


@load_authorized
@active_needed
async def load_project(update, context):
    '''Command to start the cargar_proyectos dialog'''
    logger.info("Adding project")
    username = update.message.from_user.username

    logger.info("Load autorized. Starting dialog")
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Usuario: " + username
    )

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Ingresá el Nombre del Proyecto a proponer",
    )
    return NOMBRE


async def naming_project(update, context):
    '''Dialog to set project name'''
    logger.info("Nombrando el proyecto")
    username = update.message.from_user.username
    name = update.message.text

    user = Pycampista.get_or_create(username=username, chat_id=update.message.chat_id)[0]

    new_project = Project(name=name)
    new_project.owner = user

    current_projects[username] = new_project

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Estamos cargando tu proyecto: {}!".format(username)
    )
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Tu proyecto se llama: {}".format(name)
    )
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="""Cual es el nivel de dificultad?
            1 = newbie friendly
            2 = intermedio
            3 = python avanzado"""
    )
    return DIFICULTAD


async def project_level(update, context):
    '''Dialog to set project level'''
    username = update.message.from_user.username
    text = update.message.text

    if text in ["1", "2", "3"]:
        new_project = current_projects[username]
        new_project.difficult_level = text

        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Ok! Tu proyecto es nivel: {}".format(text)
        )
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="""Ahora necesitamos que nos digas la temática de tu proyecto.
            Algunos ejemplos pueden ser:
            - flask
            - django
            - telegram
            - inteligencia artificial
            - recreativo"""
        )
        return TOPIC
    else:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Nooooooo input no válido, por favor ingresá 1, 2 o 3"
        )
        return DIFICULTAD


async def project_topic(update, context):
    '''Dialog to set project topic'''
    username = update.message.from_user.username
    text = update.message.text

    new_project = current_projects[username]
    new_project.topic = text

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Excelente {}! La temática de tu proyecto es: {}.".format(username, text)
    )

    keyboard = [
        [
            InlineKeyboardButton("Sí", callback_data=f"{REPO_EXISTS_PATTERN}:si"),
            InlineKeyboardButton("No", callback_data=f"{REPO_EXISTS_PATTERN}:no"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="¿Existe un repositorio para tu proyecto?",
        reply_markup=reply_markup,
    )

    return CHECK_REPOSITORIO


async def save_project(username, chat_id, context):
    '''Save project to database'''
    new_project = current_projects[username]

    try:
        new_project.save()
    except peewee.IntegrityError:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Ups ese proyecto ya fue cargado"
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Tu proyecto ha sido cargado"
        )


async def ask_if_repository_exists(update, context):
    '''Dialog to ask if a repository exists'''
    callback_query = update.callback_query
    chat = callback_query.message.chat

    if callback_query.data.split(':')[1] == "si":
        await context.bot.send_message(
            chat_id=chat.id,
            text="¿Cuál es la URL del repositorio?",
        )
        return REPOSITORIO
    else:
        await context.bot.send_message(
            chat_id=chat.id,
            text="Si creás un repositorio, podés agregarlo con /agregar_repositorio."
        )
        await save_project(callback_query.from_user.username, chat.id, context)
        return ConversationHandler.END


async def project_repository(update, context):
    '''Dialog to set project repository'''
    username = update.message.from_user.username
    text = update.message.text

    new_project = current_projects[username]
    new_project.repository_url = text

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"El repositorio de tu proyecto es: {text}."
    )

    await save_project(username, update.message.chat_id, context)

    return ConversationHandler.END


async def cancel(update, context):
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Has cancelado la carga del proyecto")
    return ConversationHandler.END


@active_needed
async def ask_project_name(update, context):
    '''Command to start the agregar_repositorio dialog'''
    username = update.message.from_user.username

    projects = Project.select().join(Pycampista).where(Pycampista.username == username)

    if not projects:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="No cargaste ningún proyecto",
        )
        return ConversationHandler.END

    keyboard = []
    for project in projects:
        keyboard.append([InlineKeyboardButton(project.name, callback_data=f"{PROJECT_NAME_PATTERN}:{project.name}")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="¿A qué proyecto querés agregar un repositorio?",
        reply_markup=reply_markup,
    )

    return 1


async def ask_repository_name(update, context):
    '''Dialog to set project name'''
    callback_query = update.callback_query
    chat = callback_query.message.chat

    username = callback_query.from_user.username

    current_projects[username] = callback_query.data.split(':')[1]

    await context.bot.send_message(
        chat_id=chat.id,
        text="¿Cuál es la URL del repositorio?",
    )
    return 2


async def add_repository(update, context):
    '''Dialog to set repository'''
    username = update.message.from_user.username
    text = update.message.text

    project = Project.select().where(Project.name == current_projects[username]).get()

    project.repository_url = text
    project.save()

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f'Repositorio "{text}" agregado al proyecto "{current_projects[username]}"',
    )
    return ConversationHandler.END


@active_needed
@admin_needed
async def start_project_load(update, context):
    """Allow people to upload projects"""
    _, pycamp = get_active_pycamp()

    if not pycamp.project_load_authorized:
        pycamp.project_load_authorized = True
        pycamp.save()

        await update.message.reply_text("Autorizadx \nCarga de proyectos Abierta")
        await msg_to_active_pycamp_chat(context.bot, "Carga de proyectos Abierta")
    else:
        await update.message.reply_text("La carga de proyectos ya estaba abierta")


@active_needed
@admin_needed
async def end_project_load(update, context):
    """Prevent people for keep uploading projects"""
    logger.info("Closing proyect load")

    _, pycamp = get_active_pycamp()

    if pycamp.project_load_authorized:
        pycamp.project_load_authorized = False
        pycamp.save()

    await update.message.reply_text(
        "Autorizadx \nInformación Cargada, carga de proyectos cerrada")
    await msg_to_active_pycamp_chat(context.bot, "La carga de proyectos esta Cerrada")


load_project_handler = ConversationHandler(
    entry_points=[CommandHandler('cargar_proyecto', load_project)],
    states={
        NOMBRE: [MessageHandler(filters.TEXT, naming_project)],
        DIFICULTAD: [MessageHandler(filters.TEXT, project_level)],
        TOPIC: [MessageHandler(filters.TEXT, project_topic)],
        CHECK_REPOSITORIO: [CallbackQueryHandler(ask_if_repository_exists, pattern=f'^{REPO_EXISTS_PATTERN}:')],
        REPOSITORIO: [MessageHandler(filters.TEXT, project_repository)],
    },
    fallbacks=[CommandHandler('cancel', cancel)])


async def delete_project(update, context):
    """delete project loaded"""
    username = update.message.from_user.username
    project_name_splited = update.message.text.split()
    project_name_lower = [i.lower() for i in project_name_splited]

    if len(project_name_splited) < 2:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=(
                "Debes ingresar el nombre de proyecto a eliminar.\n"
                "Ej: /borrar_proyecto intro django."
            )
        )
        return
    else:
        try:
            project_name = ' '.join(project_name_lower[1:])
            project = Project.select().where(Project.name == project_name).get()
        except Exception:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="No se encontró el proyecto '{}'.".format(project_name)
            )
            return

    if username != project.owner.username and username not in get_admins_username():
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="No sos ni admin ni el owner de este proyecto, Careta."
        )
        return
    else:
        project.delete_instance()
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Se ha eliminado el proyecto {} satisfactoriamente.".format(project_name.title())
        )
        return


async def show_projects(update, context):
    """Show available projects"""
    projects = Project.select()
    text = []
    for project in projects:
        project_text = "{} \n Owner: {} \n Temática: {} \n Nivel: {} \n Repositorio: {}".format(
            project.name,
            project.owner.username,
            project.topic,
            project.difficult_level,
            project.repository_url or '(ninguno)',
        )
        participants_count = Vote.select().where(
            (Vote.project == project) & (Vote.interest)).count()
        if participants_count > 0:
            project_text += "\n Interesades: {}".format(participants_count)
        text.append(project_text)

    if text:
        text = "\n\n".join(text)
    else:
        text = "Todavía no hay ningún proyecto cargado"

    await update.message.reply_text(text)



async def show_participants(update, context):
    """Show participants for a project"""
    
    if len(update.message.text.split()) < 2:
        await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="No se indico el nombre del proyecto. Modo de uso: '/participantes <NOMBRE_PROYECTO>'"
        )
        return  
    project_name = update.message.text.split()
    project_name = ' '.join(project_name[1:])
    project = Project.select().where(Project.name == project_name)
    if not project:
        await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="No se encontro el proyecto. Consulte /proyectos"
        )
        return

    votes = Vote.select().where(
            (Vote.project == project) & (Vote.interest))
    participants = set()
    for vote in votes:
        participants.add(vote.pycampista.username)

    response = f"Participantes:\n"
    for participant in participants:
        response = response + f"{participant} \n"

    await update.message.reply_text(response)

    
async def show_my_projects(update, context):
    """Let people see what projects they have voted for"""

    user = Pycampista.get(
        Pycampista.username == update.message.from_user.username,
    )
    votes = (
        Vote
        .select(Project, Slot)
        .join(Project)
        .join(Slot)
        .where(
            (Vote.pycampista == user) &
            Vote.interest
        )
        .order_by(Slot.code)
    )

    if votes:
        text_chunks = []

        prev_slot_day_code = None

        for vote in votes:
            slot_day_code = vote.project.slot.code[0]
            slot_day_name = DIAS[slot_day_code]

            if slot_day_code != prev_slot_day_code:
                text_chunks.append(f'*{slot_day_name}*')

            project_lines = [
                f'{vote.project.slot.start}:00',
                escape_markdown(vote.project.name),
                f'Owner: @{escape_markdown(vote.project.owner.username)}',
            ]

            text_chunks.append('\n'.join(project_lines))

            prev_slot_day_code = slot_day_code

        text = '\n\n'.join(text_chunks)
    else:
        text = "No votaste por ningún proyecto"

    await update.message.reply_text(text, parse_mode='MarkdownV2')

def set_handlers(application):
    add_repository_handler = ConversationHandler(
        entry_points=[CommandHandler('agregar_repositorio', ask_project_name)],
        states={
            1: [CallbackQueryHandler(ask_repository_name, pattern=f'^{PROJECT_NAME_PATTERN}:')],
            2: [MessageHandler(filters.TEXT, add_repository)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(load_project_handler)
    application.add_handler(add_repository_handler)

    application.add_handler(
        CommandHandler('empezar_carga_proyectos', start_project_load))
    application.add_handler(
        CommandHandler('terminar_carga_proyectos', end_project_load))
    application.add_handler(
        CommandHandler('borrar_proyecto', delete_project))
    application.add_handler(
        CommandHandler('proyectos', show_projects))
    application.add_handler(
        CommandHandler('participantes', show_participants))
    application.add_handler(
        CommandHandler('mis_proyectos', show_my_projects))

