from telegram.ext import (ConversationHandler, CommandHandler,
                          MessageHandler, Filters)
from models import Pycampista, Project, ProjectOwner, Slot, Vote, Wizard
from manage_pycamp import ping_PyCamp_group, is_auth

project_auth = False
users_status = {}
current_projects = {}
NOMBRE, DIFICULTAD, TOPIC = range(3)


def load_project(bot, update):
    '''Command to start the cargar_proyectos dialog'''
    username = update.message.from_user.username
    if project_auth:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Usuario: " + username
        )

        bot.send_message(
            chat_id=update.message.chat_id,
            text="Ingresá el Nombre del Proyecto a proponer",
        )
        return NOMBRE
    else:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Carga de projectos Cerrada"
        )
        return ConversationHandler.END


def naming_project(bot, update):
    '''Dialog to set project name'''
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
            text="Nooooooo input no válido, por favor ingresá 1, 2 o 3".format(text)
        )
        return DIFICULTAD


def project_topic(bot, update):
    '''Dialog to set project topic'''
    username = update.message.from_user.username
    text = update.message.text

    new_project = current_projects[username]
    new_project.topic = text

    new_project.save()

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Excelente {}! La temática de tu proyecto es: {}.".format(
                                                            username, text)
    )
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Tu proyecto ha sido cargado".format(username, text)
    )
    return ConversationHandler.END


def cancel(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Has cancelado la carga del proyecto"
        )
    return ConversationHandler.END


def start_project_load(bot, update):
    """Allow people to upload projects"""
    global project_auth
    if not is_auth(bot, update.message.from_user.username):
        return

    if not project_auth:
        update.message.reply_text("Autorizadx \nCarga de proyectos Abierta")
        ping_PyCamp_group(bot, "Carga de proyectos Abierta")
        project_auth = True
    else:
        update.message.reply_text("La carga de proyectos ya estaba abierta")


def end_project_load(bot, update):
    """Prevent people for keep uploading projects"""
    if not is_auth(bot, update.message.from_user.username):
        return

    ping_PyCamp_group(bot, "La carga de projectos esta Cerrada")
    update.message.reply_text(
            "Autorizadx \nInformación Cargada, carga de proyectos cerrada")


load_project_handler = ConversationHandler(
       entry_points=[CommandHandler('cargar_proyecto', load_project)],
       states={
           NOMBRE: [MessageHandler(Filters.text, naming_project)],
           DIFICULTAD: [MessageHandler(Filters.text, project_level)],
           TOPIC: [MessageHandler(Filters.text, project_topic)],
       },
       fallbacks=[CommandHandler('cancel', cancel)]
   )
