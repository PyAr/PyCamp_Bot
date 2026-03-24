import string
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from pycamp_bot.models import Project, Slot, Pycampista, Vote
from pycamp_bot.commands.auth import admin_needed
from pycamp_bot.scheduler.db_to_json import export_db_2_json
from pycamp_bot.scheduler.schedule_calculator import export_scheduled_result
from pycamp_bot.utils import escape_markdown, get_slot_weekday_name


DAY_SLOT_TIME = {
    'day': [],  # Guarda el codigo del dia ej: ['A','B']
    'slot': [],  # Guarda la cantidad de slots del dia iterado ej [5] (se sobreescribe)
    'time': [],  # Guarda la hora a la que empieza el dia iterado [15] (se sobreescribe)
    'meals': []  # Guarda los horarios de las comidas (strings, hora entera)
}

COMIDAS = ['Desayuno', 'Almuerzo', 'Merienda', 'Cena']


def _slot_sort_key(slot):
    """
    Ordena los slots por día y número de slot.
    Ej: A1, A2, A10, B1, B2, B3, etc.
    """
    code = slot.code
    letra_dia = code[0]
    if len(code) == 1:
        return (letra_dia, 0)
    numero = int(code[1:])
    return (letra_dia, numero)


def _slots_ordered_query():
    """Ordena los slots por día y número de slot.
    Ej: A1, A2, A10, B1, B2, B3, etc.
    """
    return sorted(Slot.select(), key=_slot_sort_key)


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


async def define_meal_times(update, context):
    global DAY_SLOT_TIME
    text = update.message.text
    if text not in ["1", "2", "3", "4", "5", "6", "7"]:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="mmm eso no parece un numero de dias razonable, de nuevo?"
        )
        return 1
    DAY_SLOT_TIME['day'] = list(string.ascii_uppercase[0:int(text)])
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Ingresa los horarios de comidas\nEj: 9, 13, 17, 21")
    return 2


async def define_slot_ammount(update, context):
    global DAY_SLOT_TIME
    raw = [item.strip() for item in update.message.text.split(',') if item.strip()]
    try:
        DAY_SLOT_TIME['meals'] = [str(int(h)) for h in raw]
    except ValueError:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Cada horario debe ser un número entero, ej: 9, 13, 17, 21",
        )
        return 2
    day_name = get_slot_weekday_name(DAY_SLOT_TIME['day'][0])
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Cuantos slots tiene  tu dia {}?".format(day_name)
    )
    return 3


async def define_slot_times(update, context):
    text = update.message.text

    day_name = get_slot_weekday_name(DAY_SLOT_TIME['day'][0])
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="A que hora empieza tu dia {}?".format(day_name)
    )
    DAY_SLOT_TIME['slot'] = [text]
    return 4


async def create_slot(update, context):
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    text = update.message.text

    DAY_SLOT_TIME['time'] = [text]
    slot_amount = int(DAY_SLOT_TIME['slot'][0])
    times = list(range(slot_amount + 1))[1:]
    starting_hour = int(text)
    meals = DAY_SLOT_TIME['meals']

    pycampista = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]

    for t in times:
        new_slot = Slot(code=str(DAY_SLOT_TIME['day'][0] + str(t)))
        new_slot.start = starting_hour
        new_slot.current_wizard = pycampista

        hkey = str(starting_hour)
        if hkey in meals:
            idx = meals.index(hkey)
            new_slot.meal_type = COMIDAS[idx]
        else:
            new_slot.meal_type = None

        new_slot.save()
        starting_hour += 1

    DAY_SLOT_TIME['day'].pop(0)

    if len(DAY_SLOT_TIME['day']) > 0:
        day_name = get_slot_weekday_name(DAY_SLOT_TIME['day'][0])
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Cuantos slots tiene tu dia {}?".format(day_name)
        )
        return 3
    else:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Genial! Slots Asignados"
        )
        await make_schedule(update, context)
        return ConversationHandler.END


async def make_schedule(update, context):
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Generando el Cronograma..."
    )

    data_json = export_db_2_json()
    my_schedule = export_scheduled_result(data_json)

    for project_name, slot_code in my_schedule:
        slot = Slot.get(Slot.code == slot_code)
        if slot.meal_type:
            continue
        project = Project.get(Project.name == project_name)
        project.slot = slot.id
        project.save()

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Cronograma Generado!"
    )


async def check_day_tab(slot, prev_slot, cronograma):
    def append_day_name():
        cronograma.append(f'*{escape_markdown(get_slot_weekday_name(slot.code[0]))}:*')

    if prev_slot is None:
        append_day_name()
    elif slot.code[0] != prev_slot.code[0]:
        cronograma.append('')
        append_day_name()


async def show_schedule(update, context):
    slots = _slots_ordered_query()
    projects = list(Project.select())
    cronograma = []

    prev_slot = None

    for slot in slots:
        await check_day_tab(slot, prev_slot, cronograma)

        if slot.meal_type:
            h = slot.start_hour_display()
            cronograma.append(
                f'*{h}:00hs* — *{escape_markdown(slot.meal_type)}*'
            )
        else:
            for project in projects:
                if project.slot_id == slot.id:
                    h = slot.start_hour_display()
                    cronograma.append(
                        f'*{h}:00hs* — *{escape_markdown(project.name.capitalize())}*'
                    )
                    cronograma.append(
                        f'A cargo de @{escape_markdown(project.owner.username)}'
                    )

        prev_slot = slot

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text='\n'.join(cronograma),
        parse_mode='MarkdownV2'
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
                    if slot.meal_type:
                        await context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text="Ese slot está reservado para comidas; elegí otro código."
                        )
                        return
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
        1: [MessageHandler(filters.TEXT, define_meal_times)],
        2: [MessageHandler(filters.TEXT, define_slot_ammount)],
        3: [MessageHandler(filters.TEXT, define_slot_times)],
        4: [MessageHandler(filters.TEXT, create_slot)]},
    fallbacks=[CommandHandler('cancel', cancel)])


def set_handlers(application):
    application.add_handler(CommandHandler('cronograma', show_schedule))
    application.add_handler(CommandHandler('cambiar_slot', change_slot))
    application.add_handler(load_schedule_handler)
