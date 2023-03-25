from telegram.ext import CommandHandler
from pycamp_bot.models import Project, Pycampista, Vote
from pycamp_bot.commands.auth import get_admins_username


async def announce(update, context):
    username = update.message.from_user.username
    admins = get_admins_username()
    project_name = update.message.text.split()[1:]

    project_name = " ".join(project_name)
    project = Project.select().where(Project.name == project_name)

    if len(project) <= 0:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"El proyecto '{project_name}' no existe o esta mal escroto.\n"
            "El formato de este comando es:\n"
            "/anunciar NOMBRE_DEL_PROYECTO"
        )
        return

    if not (project.get().owner.username == username or username in admins):
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="No sos ni admin ni el owner de este proyecto, Careta."
        )
        return

    pycampistas = Vote.select().join(Pycampista).where((Vote.project == project) & (Vote.interest))

    chat_id_list = [user.pycampista.chat_id for user in pycampistas]

    for chat_id in chat_id_list:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Esta por empezar {project_name} a cargo de @{project.get().owner.username}."
        )
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Anunciado!"
    )


def set_handlers(application):
    application.add_handler(CommandHandler('anunciar', announce))
