import logging
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from pycamp_bot.models import Pycampista, Project, Vote
from pycamp_bot.commands.base import msg_to_active_pycamp_chat
from pycamp_bot.commands.manage_pycamp import active_needed, get_active_pycamp
from pycamp_bot.commands.auth import admin_needed, get_admins_username
import peewee


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
    text = update.message.text

    new_project = Project(name=text)
    current_projects[username] = new_project

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Estamos cargando tu proyecto: {}!".format(username)
    )
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Tu proyecto se llama: {}".format(text)
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
            text="Nooooooo input no válido, por favor "
                 "ingresá 1, 2 o 3".format(text)
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
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Excelente {}! La temática de tu proyecto es: {}.".format(username, text))
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Tu proyecto ha sido cargado".format(username, text)
        )
    
    except peewee.IntegrityError:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Ups ese proyecto ya fue cargado".format(username, text)
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
    # await msg_to_active_pycamp_chat(context.bot, "La carga de proyectos esta Cerrada")


load_project_handler = ConversationHandler(
    entry_points=[CommandHandler('cargar_proyecto', load_project)],
    states={
        NOMBRE: [MessageHandler(filters.TEXT, naming_project)],
        DIFICULTAD: [MessageHandler(filters.TEXT, project_level)],
        TOPIC: [MessageHandler(filters.TEXT, project_topic)]},
    fallbacks=[CommandHandler('cancel', cancel)])


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
        participants_count = Vote.select().where((Vote.project == project)
                                                 & (Vote.interest)).count()
        if participants_count > 0:
            project_text += "\n Interesades: {}".format(participants_count)
        text.append(project_text)
    text.append(project_text)

    if text:
        text = "\n\n".join(text)
    else:
        text = "Todavía no hay ningún proyecto cargado"

    await update.message.reply_text(text)

@admin_needed
async def cancel_project(update, context):
    """Cancel project loaded"""
    project_name = update.message.text.split()[1]
    print('project: ', project_name)

    try:
        project = Project.select().where(Project.name == project_name).get()
        #time.sleep(5)
        print('project: ', dir(project))
        Project.delete().where(Project.name == project_name).execute()
    except:
        await update.message.reply_text(
            "Parece que no lo pudimos cargar, controla que hayas puesto bien el nombre del proyecto")
    #project.delete_instance()
    #print('project: ', project.owner.username)

    username = update.message.from_user.username
    admins = get_admins_username()

def set_handlers(application):
    application.add_handler(CommandHandler('cancelar_proyecto', cancel_project))
    
    application.add_handler(load_project_handler)
    application.add_handler(
        CommandHandler('empezar_carga_proyectos', start_project_load))
    application.add_handler(
        CommandHandler('terminar_carga_proyectos', end_project_load))
    application.add_handler(
        CommandHandler('proyectos', show_projects))
