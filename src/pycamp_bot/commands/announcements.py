from telegram import Update, Bot
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackContext
from pycamp_bot.models import Project, Pycampista, Vote
from pycamp_bot.commands.auth import get_admins_username
from pycamp_bot.logger import logger
from pycamp_bot.commands.manage_pycamp import active_needed

PROYECTO, LUGAR, MENSAJE = ["proyecto", "lugar", "mensaje"]

ERROR_MESSAGES = {
    "format_error": "Error de formato, recuerde que el formato debe ser el siguiente:\n/anunciar tu_proyecto\nPor favor comienza de nuevo.",
    "not_admin": "No tenes proyectos para anunciar y no eres admin.",
    "not_found": "No se encontro el proyecto *{project_name}*. Intenta de nuevo por favor.",
    "no_admin": "No puedes anunciar proyectos si no eres el owner.\nPor favor contacta un admin"
}


class AnnouncementState:
    def __init__(self):
        self.username = None
        self.p_name = ''
        self.current_project = False
        self.projects = []
        self.owner = ''
        self.lugar = ''
        self.mensaje = ''

state = AnnouncementState()

async def user_is_admin(pycampist: str) -> bool:
    return pycampist in get_admins_username()

async def should_be_able_to_announce(pycampista: str, proyect: Project) -> bool:
    return pycampista == proyect.owner.username or await user_is_admin(pycampista)


@active_needed
async def announce(update: Update, context: CallbackContext) -> str:
    logger.info("Announcement project process started")
    parameters: list[str] = update.message.text.split()

    if len(parameters) > 2:
        await handle_error(context, update.message.chat_id, "format_error")
        logger.warning("Error de formato en la solicitud. Too many parameters")
        return ConversationHandler.END
    state.username = update.message.from_user.username
    state.projects = Project.select().join(Pycampista).where(Pycampista.username == state.username)

    if len(state.projects) == 0:
        if not await user_is_admin(state.username):
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=ERROR_MESSAGES["no_admin"],
            )
            logger.warn(f"Pycampista {state.username} no contiene proyectos creados.")
            return ConversationHandler.END
        else:
            state.projects = Project.select()
            return await get_project(update, context)

    if len(parameters) == 1:
        project_list: str = ""
        if len(state.projects) == 0:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Ingresá el Nombre del Proyecto a anunciar."
            )
        else:
            project_list = "\n".join(p.name.capitalize() for p in state.projects)
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"""Ingresá el Nombre del Proyecto a anunciar.\n\nTienes los siguientes proyectos:\n{project_list}""",
            )

    if len(parameters) == 2:
        print('-Handle correct commands-')
        state.p_name = update.message.text.split()[1].lower()
        _projects = Project.select().join(Pycampista).where(Project.name == state.p_name)

        if len(_projects) == 0:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"No existe el proyecto: *{state.p_name}*.",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        elif not await should_be_able_to_announce(state.username, _projects[0]):
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=ERROR_MESSAGES["no_admin"],
            )
            logger.warn(f"Solicitud de anuncio no autorizada.")
            return ConversationHandler.END
        else:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"Anunciando el proyecto: *{_projects[0].name.capitalize()}* !!!",
                parse_mode='Markdown'
            )
            state.owner = _projects[0].owner.username
            state.current_project = _projects[0]
        return await get_project(update, context)
    return PROYECTO


async def get_project(update: Update, context: CallbackContext) -> str:
    '''Dialog to set project to announce'''
    logger.info("Getting project")
    parameters_list: list[str] = update.message.text.split()

    if len(parameters_list) > 2:
        await handle_error(context, update.message.chat_id, "format_error")
        return ConversationHandler.END

    if "/anunciar" in parameters_list:
        if len(parameters_list) == 2:
            state.current_project = Project.select().join(Pycampista).where(Project.name == parameters_list[1].lower())
            if not await should_be_able_to_announce(update.message.from_user.username, state.current_project[0]):
                await handle_error(context, update.message.chat_id, "format_error", state.current_project)
                logger.warning(f"Project {parameters_list[1]} not found!")
                return PROYECTO
            else:
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text="Ingrese lugar donde comienza el proyecto."
                )
                state.p_name = parameters_list[1].lower()
                state.current_project = state.current_project[0]
        if len(parameters_list) == 1:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Ingrese el nombre del proyecto."
            )
            return PROYECTO

    elif len(parameters_list) == 2:
        await handle_error(context, update.message.chat_id, "format_error")
        logger.warning("Error de formato en la solicitud. Too many parameters")
        return PROYECTO

    else:
        c_proyect = Project.select().where(Project.name == parameters_list[0].lower()).first()
        print('c_proyect: ', c_proyect)
        if c_proyect:
            if await should_be_able_to_announce(update.message.from_user.username, c_proyect):
                state.current_project = c_proyect
                state.p_name = c_proyect.name
                state.owner = c_proyect.owner.username
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text="Ingrese lugar donde comienza el proyecto."
                    )
            else:
                logger.warning("Solicitud de anuncio no autorizada.")
                await handle_error(
                        context, 
                        update.message.chat_id, 
                        "no_admin"
                    )
                return ConversationHandler.END
        else:
            logger.warning("Solicitud de anuncio no autorizada.")
            await handle_error(
                    context, 
                    update.message.chat_id, 
                    "not_found",
                    project_name=parameters_list[0]
                )
            logger.warning("Error de formato en la solicitud. No se encontró el proyecto.")
            return PROYECTO
    return LUGAR


async def meeting_place(update: Update, context: CallbackContext) -> str:
    '''Dialog to set the place of the meeting'''
    logger.info("Setting place")
    state.lugar = update.message.text.capitalize()
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Escribe un mensaje a los pycampistas suscriptos ..."
    )
    return MENSAJE


async def message_project(update: Update, context: CallbackContext) -> str:
    '''Dialog to set project topic'''
    state.mensaje = update.message.text.capitalize()
    pycampistas: list[Vote] = Vote.select().join(
        Pycampista).where(
        (Vote.project == Project.select().where(
            Project.name == state.current_project.name)) & (Vote.interest))
    chat_id_list: list[int] = [user.pycampista.chat_id for user in pycampistas]
    for chat_id in chat_id_list:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f'''Está por empezar el proyecto *"{(state.p_name).capitalize()}"* a cargo de *@{state.owner}*.\n*¿Dónde?* 👉🏼 {state.lugar}''',
                parse_mode='Markdown'
            )
            if update.message.from_user.username == state.owner:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f'*Project Owner says:* **{state.mensaje}**',
                    parse_mode='Markdown'
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f'Admin *@{update.message.from_user.username}* says: **{state.mensaje}**',
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Error al enviar el mensaje: {e}")
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Anunciado!"
    )
    logger.info('Project announced!')
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> str:
    '''Cancel the project announcement'''
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Has cancelado el anuncio del proyecto")
    logger.warning("Announcement canceled")
    return ConversationHandler.END


async def handle_error(context: CallbackContext, chat_id: int, error_key: str, **kwargs: list) -> None:
    error_message = ERROR_MESSAGES[error_key].format(**kwargs)
    print('error_message: ', error_message)
    '''Handle error messages'''
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=error_message,
            #parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error al enviar el mensaje: {e}")


start_project_handler = ConversationHandler(
    entry_points=[CommandHandler('anunciar', announce)],
    states={
        PROYECTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_project)],
        LUGAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, meeting_place)],
        MENSAJE: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_project)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

def set_handlers(application):
    '''Add handlers to the application'''
    application.add_handler(start_project_handler)
