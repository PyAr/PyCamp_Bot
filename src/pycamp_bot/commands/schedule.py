import string
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from pycamp_bot.models import Project, Slot, Pycampista, Vote
from pycamp_bot.commands.auth import admin_needed
from pycamp_bot.scheduler.db_to_json import export_db_2_json
from pycamp_bot.scheduler.schedule_calculator import export_scheduled_result


DAY_SLOT_TIME = {
    'day':[], # Guarda el codigo del dia ej: ['A','B']
    'slot':[], # Guarda la cantidad de slots del dia iterado ej [5] (se sobreescribe)
    'time':[], # Guarda la hora a la que empieza el dia iterado [15] (se sobreescribe)
}


DIAS = {
    'A':'Jueves',
    'B':'Viernes',
    'C':'Sabado',
    'D':'Domingo',
    'E':'Lunes',
    'F':'Martes',
    'G':'Miercoles',
    }


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


async def define_slot_ammount(update, context):
    global DAY_SLOT_TIME
    text = update.message.text
    if text not in ["1", "2", "3", "4", "5", "6", "7"]:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="mmm eso no parece un numero de dias razonable, de nuevo?"
        )
        return 1

    
    DAY_SLOT_TIME['day'] =list(string.ascii_uppercase[0:int(text)])

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Cuantos slots tiene  tu dia {}".format(DAY_SLOT_TIME['day'][0])
    )
    return 2


async def define_slot_times(update, context):
    text = update.message.text
    day = DAY_SLOT_TIME['day'][0]
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="A que hora empieza tu dia {}".format(day)
    )
    DAY_SLOT_TIME['slot'] = [text]
    return 3


async def create_slot(update, context):
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    text = update.message.text

    DAY_SLOT_TIME['time'] = [text]
    slot_amount = DAY_SLOT_TIME['slot'][0]
    times = list(range(int(slot_amount)+1))[1:]
    starting_hour = int(text)

    while len(times) > 0:
        new_slot = Slot(code=str(DAY_SLOT_TIME['day'][0]+str(times[0])))
        new_slot.start = starting_hour

        pycampista = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]
        new_slot.current_wizzard = pycampista

        new_slot.save()
        times.pop(0)
        starting_hour += 1

    DAY_SLOT_TIME['day'].pop(0)

    if len(DAY_SLOT_TIME['day']) > 0:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Cuantos slots tiene tu dia {}".format(DAY_SLOT_TIME['day'][0])
        )
        return 2
    else:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Genial! Slots Asignados"
        )
        make_schedule(update, context)
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


async def check_day_tab(day, slots, cronograma, i):
    try:
        if day != DIAS[slots[i-1].code[0]]:
            cronograma += f'\n*{day}:*\n'
    except Exception as e:
        print("ERROR       ", e)
    return cronograma


async def show_schedule(update, context):
    slots = Slot.select()
    projects = Project.select()
    cronograma = "*Cronograma:* \n"

    for i, slot in enumerate(slots):
        day = DIAS[slot.code[0]]
        cronograma = await check_day_tab(day, slots, cronograma, i)

        for project in projects:
            if project.slot_id == slot.id:
                cronograma += f'*-* {slot.start}:00hs = *{(project.name).capitalize()}.*\n'
                cronograma += f'A cargo de 👉🏼 {"@" + project.owner.username}\n'

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=cronograma,
        parse_mode='Markdown'
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
        1: [MessageHandler(filters.TEXT, define_slot_ammount)],
        2: [MessageHandler(filters.TEXT, define_slot_times)],
        3: [MessageHandler(filters.TEXT, create_slot)]},
    fallbacks=[CommandHandler('cancel', cancel)])


def set_handlers(application):
    application.add_handler(CommandHandler('cronograma', show_schedule))
    application.add_handler(CommandHandler('cambiar_slot', change_slot))
    application.add_handler(load_schedule_handler)
