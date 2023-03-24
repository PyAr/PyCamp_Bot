import logging
from telegram.ext import (ConversationHandler, CommandHandler, MessageHandler, Filters)
from pycamp_bot.models import Pycampista, Project, Vote
from pycamp_bot.commands.base import msg_to_active_pycamp_chat
from pycamp_bot.commands.manage_pycamp import active_needed, get_active_pycamp
from pycamp_bot.commands.auth import admin_needed


current_projects = {}
NOMBRE, DIFICULTAD, TOPIC = ["nombre", "dificultad", "topic"]

logger = logging.getLogger(__name__)


def load_authorized(f):
    def wrap(*args, **kargs):
        logger.info('Load authorized wrapper')

        bot, update = args
        is_active, pycamp = get_active_pycamp()
        if pycamp.project_load_authorized:
            return f(*args, **kargs)
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="La carga de proyectos no está autorizada. Avisale a un\
                admin (/admins)!")
    return wrap


@load_authorized
@active_needed
def load_project(bot, update):
    '''Command to start the cargar_proyectos dialog'''
    logger.info("Adding project")
    username = update.message.from_user.username

    logger.info("Load autorized. Starting dialog")
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Usuario: " + username
    )

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Ingresá el Nombre del Proyecto a proponer",
    )
    return NOMBRE


def naming_project(bot, update):
    '''Dialog to set project name'''
    logger.info("Nombrando el proyecto")
    username = update.message.from_user.username
    text = update.message.text

    new_project = Project(name=text)
    current_projects[username] = new_project

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Estamos cargando tu proyecto: {}!".format(username)
    )
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Tu proyecto se llama: {}".format(text)
    )
    bot.send_message(
        chat_id=update.message.chat_id,
        text="""Cual es el nivel de dificultad?
            1 = newbie friendly
            2 = intermedio
            3 = python avanzado"""
    )
    return DIFICULTAD


def project_level(bot, update):
    '''Dialog to set project level'''
    username = update.message.from_user.username
    text = update.message.text

    if text in ["1", "2", "3"]:
        new_project = current_projects[username]
        new_project.difficult_level = text

        bot.send_message(
            chat_id=update.message.chat_id,
            text="Ok! Tu proyecto es nivel: {}".format(text)
        )
        bot.send_message(
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
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Nooooooo input no válido, por favor "
                 "ingresá 1, 2 o 3".format(text)
        )
        return DIFICULTAD


def project_topic(bot, update):
    '''Dialog to set project topic'''
    username = update.message.from_user.username
    text = update.message.text

    new_project = current_projects[username]
    new_project.topic = text

    chat_id = update.message.chat_id
    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]

    new_project.owner = user

    new_project.save()

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Excelente {}! La temática de tu proyecto es: {}.".format(username, text))
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Tu proyecto ha sido cargado".format(username, text)
    )
    return ConversationHandler.END


def cancel(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Has cancelado la carga del proyecto")
    return ConversationHandler.END


@active_needed
@admin_needed
def start_project_load(bot, update):
    """Allow people to upload projects"""
    _, pycamp = get_active_pycamp()

    if not pycamp.project_load_authorized:
        pycamp.project_load_authorized = True
        pycamp.save()

        update.message.reply_text("Autorizadx \nCarga de proyectos Abierta")
        msg_to_active_pycamp_chat(bot, "Carga de proyectos Abierta")
    else:
        update.message.reply_text("La carga de proyectos ya estaba abierta")


@active_needed
@admin_needed
def end_project_load(bot, update):
    """Prevent people for keep uploading projects"""
    logger.info("Closing proyect load")

    _, pycamp = get_active_pycamp()

    if pycamp.project_load_authorized:
        pycamp.project_load_authorized = False
        pycamp.save()

    update.message.reply_text(
        "Autorizadx \nInformación Cargada, carga de proyectos cerrada")
    msg_to_active_pycamp_chat(bot, "La carga de proyectos esta Cerrada")


load_project_handler = ConversationHandler(
    entry_points=[CommandHandler('cargar_proyecto', load_project)],
    states={
        NOMBRE: [MessageHandler(Filters.text, naming_project)],
        DIFICULTAD: [MessageHandler(Filters.text, project_level)],
        TOPIC: [MessageHandler(Filters.text, project_topic)]},
    fallbacks=[CommandHandler('cancel', cancel)])


def show_projects(bot, update):
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

    update.message.reply_text(text)


def set_handlers(updater):
    updater.dispatcher.add_handler(load_project_handler)
    updater.dispatcher.add_handler(
        CommandHandler('empezar_carga_proyectos', start_project_load))
    updater.dispatcher.add_handler(
        CommandHandler('terminar_carga_proyectos', end_project_load))
    updater.dispatcher.add_handler(
        CommandHandler('proyectos', show_projects))
