import logging
import peewee
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from pycamp_bot.models import Pycampista, Project, Slot, Vote
from pycamp_bot.commands.base import msg_to_active_pycamp_chat
from pycamp_bot.commands.manage_pycamp import active_needed, get_active_pycamp
from pycamp_bot.commands.auth import admin_needed, get_admins_username
from pycamp_bot.commands.schedule import DIAS
from pycamp_bot.utils import escape_markdown


current_projects = {}
NOMBRE, DIFICULTAD, TOPIC = ["nombre", "dificultad", "topic"]

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

    new_project = Project(name=name)
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

    chat_id = update.message.chat_id
    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]

    new_project.owner = user
    try:
        new_project.save()
    except peewee.IntegrityError:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Ups ese proyecto ya fue cargado"
        )
        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Excelente {}! La temática de tu proyecto es: {}.".format(username, text))
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Tu proyecto ha sido cargado"
    )
    return ConversationHandler.END


async def cancel(update, context):
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Has cancelado la carga del proyecto")
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
        TOPIC: [MessageHandler(filters.TEXT, project_topic)]},
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
    """Prevent people for keep uploading projects"""
    projects = Project.select()
    text = []
    for project in projects:
        project_text = "{} \n Owner: {} \n Temática: {} \n Nivel: {}".format(
            project.name,
            project.owner.username,
            project.topic,
            project.difficult_level
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
    application.add_handler(load_project_handler)
    application.add_handler(
        CommandHandler('empezar_carga_proyectos', start_project_load))
    application.add_handler(
        CommandHandler('terminar_carga_proyectos', end_project_load))
    application.add_handler(
        CommandHandler('borrar_proyecto', delete_project))
    application.add_handler(
        CommandHandler('proyectos', show_projects))
    application.add_handler(
        CommandHandler('mis_proyectos', show_my_projects))

