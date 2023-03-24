import logging
from telegram.ext import CommandHandler
from pycamp_bot.models import Project, Pycampista, Vote
from pycamp_bot.commands.auth import get_admins_username


logger = logging.getLogger(__name__)


def announce(bot, update):
    username = update.message.from_user.username
    admins = get_admins_username()
    project_name = update.message.text.split()[1:]

    project_name = " ".join(project_name)
    project = Project.select().where(Project.name == project_name)

    if len(project) <= 0:
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"El proyecto '{project_name}' no existe o esta mal escroto.\n"
            "El formato de este comando es:\n"
            "/anunciar NOMBRE_DEL_PROYECTO"
        )
        return

    if not (project.get().owner.username == username or username in admins):
        bot.send_message(
            chat_id=update.message.chat_id,
            text="No sos ni admin ni el owner de este proyecto, Careta."
        )
        return

    pycampistas = Vote.select().join(Pycampista).where((Vote.project == project) & (Vote.interest))

    chat_id_list = [user.pycampista.chat_id for user in pycampistas]

    for chat_id in chat_id_list:
        bot.send_message(
            chat_id=chat_id,
            text=f"Esta por empezar {project_name} a cargo de @{project.get().owner.username}."
        )
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Anunciado!"
    )


def set_handlers(updater):
    updater.dispatcher.add_handler(CommandHandler('anunciar', announce))
