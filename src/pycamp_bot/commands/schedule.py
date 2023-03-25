import logging
import string
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from pycamp_bot.models import Project, Slot, Pycampista, Vote
from pycamp_bot.commands.auth import admin_needed
from pycamp_bot.scheduler.db_to_json import export_db_2_json
from pycamp_bot.scheduler.schedule_calculator import export_scheduled_result


DAY_LETTERS = []

logger = logging.getLogger(__name__)


def _dictToString(dicto):
    if dicto:
        return str(dicto).replace(', ', '\r\n').replace('}', '\r\n').replace("u'", "") \
            .replace("'", "").replace('[', '\r\n').replace(']', '\r\n\r\n') \
            .replace(': {', '\r\n')[1:-1]
    else:
        return "No tengo un cronograma para darte. Pedile a unx admin que haga /cronogramear"


async def cancel(update, context):
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Has cancelado la carga de slots")
    return ConversationHandler.END


@admin_needed
async def define_slot_days(update, context):
    # TODO: filtrar proyectos por pycamp activo.
    if Slot.select().exists():
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="El cronograma ya existe."
        )
        return

    if not Project.select().exists():
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="No hay proyectos que cronogramear."
        )
        return

    if not Vote.select().exists():
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Todavia no se realizo la votacion."
        )
        return

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Cuantos dias tiene tu cronograma?"
    )
    return 1


async def define_slot_times(update, context):
    global DAY_LETTERS
    text = update.message.text
    if text not in ["1", "2", "3", "4", "5", "6", "7"]:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="mmm eso no parece un numero de dias razonable, de nuevo?"
        )
        return 1

    DAY_LETTERS = list(string.ascii_uppercase[0:int(text)])

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Cuantos slots tiene  tu dia {}".format(DAY_LETTERS[0])
    )
    return 2


async def create_slot(update, context):
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    text = update.message.text
    times = list(range(int(text)+1))[1:]
    starting_hour = 10

    while len(times) > 0:
        new_slot = Slot(code=str(DAY_LETTERS[0]+str(times[0])))
        new_slot.start = starting_hour

        pycampista = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]
        new_slot.current_wizzard = pycampista

        new_slot.save()
        times.pop(0)
        starting_hour += 1

    DAY_LETTERS.pop(0)

    if len(DAY_LETTERS) > 0:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Cuantos slots tiene tu dia {}".format(DAY_LETTERS[0])
        )
        return 2
    else:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Genial! Slots Asignados"
        )
        make_schedule(context.bot, update)
        return ConversationHandler.END


async def make_schedule(update, context):
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Generando el Cronograma..."
    )

    data_json = export_db_2_json()
    my_schedule = export_scheduled_result(data_json)

    for relationship in my_schedule:
        slot = Slot.get(Slot.code == relationship[1])
        project = Project.get(Project.name == relationship[0])
        project.slot = slot.id
        project.save()

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Cronograma Generado!"
    )


async def show_schedule(update, context):
    slots = Slot.select()
    projects = Project.select()
    cronograma = {}

    for slot in slots:
        cronograma[slot.code] = []
        for project in projects:
            if project.slot_id == slot.id:
                cronograma[slot.code].append(project.name)
                cronograma[slot.code].append('@' + project.owner.username)

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=_dictToString(cronograma)
    )


@admin_needed
async def change_slot(update, context):
    projects = Project.select()
    slots = Slot.select()
    text = update.message.text.split(' ')

    if not len(text) >= 3:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="""El formato de este comando es:
                /cambiar_slot NOMBRE_DEL_PROYECTO NUEVO_SLOT
            ej: /cambiar_slot fades AB
        """
        )
        return

    found = False
    project_name = " ".join(text[1:-1])
    for project in projects:
        if project.name == project_name:
            for slot in slots:
                if slot.code == text[-1]:
                    found = True
                    project.slot = slot.id
                    project.save()
    if found:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Exito"
        )
    else:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="O el slot o el nombre del proyecto no estan en la db"
        )


load_schedule_handler = ConversationHandler(
    entry_points=[CommandHandler('cronogramear', define_slot_days)],
    states={
        1: [MessageHandler(filters.TEXT, define_slot_times)],
        2: [MessageHandler(filters.TEXT, create_slot)]},
    fallbacks=[CommandHandler('cancel', cancel)])


def set_handlers(application):
    application.add_handler(CommandHandler('cronograma', show_schedule))
    application.add_handler(CommandHandler('cambiar_slot', change_slot))
    application.add_handler(load_schedule_handler)
