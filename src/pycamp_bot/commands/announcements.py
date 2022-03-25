import logging
import os

from telegram.ext import CommandHandler
from pycamp_bot.models import Project, Pycampista, Vote


logger = logging.getLogger(__name__)
def announce(bot, update):
    project_name = update.message.text.split()[1:]

    project_name = " ".join(project_name)
    project =Project.select().where(Project.name ==project_name)
    if len(project) <= 0:
        bot.send_message(
        chat_id=update.message.chat_id,
        text=f"El proyecto '{project_name}' no existe o esta mal escroto.\n"
            "El formato de este comando es:\n"
            "/anunciar NOMBRE_DEL_PROYECTO"
        )
        return

    pycampistas = Vote.select().join(Pycampista).where(Vote.project == project.get())

    chat_id_list = [user.pycampista.chat_id for user in pycampistas]
    
    for chat_id in chat_id_list:
        bot.send_message(
            chat_id=chat_id,
            text=f"Esta por empezar {project_name} a cargo de @{project.get().owner.username}."
        )
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Anunciado!"
        )

def set_handlers(updater):
    updater.dispatcher.add_handler(CommandHandler('anunciar', announce))

