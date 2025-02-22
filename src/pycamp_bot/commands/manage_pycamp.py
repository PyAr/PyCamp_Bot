import datetime
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from pycamp_bot.models import Pycamp
from pycamp_bot.models import Pycampista
from pycamp_bot.models import PycampistaAtPycamp
from pycamp_bot.commands.auth import admin_needed
from pycamp_bot.logger import logger
from pycamp_bot.utils import escape_markdown


SET_DATE_STATE = "set_fate"
SET_DURATION_STATE = "set_duration"
WRAP_UP_STATE = "wrap_up"


def get_pycamp_by_name(name):
    pycamps = Pycamp.select().where(Pycamp.headquarters == name)
    count = pycamps.count()
    if count == 1:
        return pycamps[0]
    logger.info('There is some error. Pycamps with name {} has count != 1 ({})'.format(name, count))
    return None


def get_active_pycamp():
    active = Pycamp.select().where(Pycamp.active)
    if active.count() == 0:
        return False, None
    return True, active[0]


def active_needed(f):
    def wrap(*args, **kargs):
        bot, update = args
        is_active, _ = get_active_pycamp()
        if is_active:
            return f(*args)
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="No hay un PyCamp activo.")
    return wrap


@admin_needed
async def set_active_pycamp(update, context):
    is_active, pycamp = get_active_pycamp()
    parameters = update.message.text.split(' ')

    if is_active:
        pycamp.active = False
        pycamp.save()

    if not len(parameters) == 2:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="El comando necesita un parametro (pycamp name)")
        return

    pycamp = get_pycamp_by_name(parameters[1])
    if pycamp is None:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="El Pycamp {} no existe".format(parameters[1]))
        return

    pycamp.active = True
    pycamp.save()

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="El Pycamp {} ahora esta activo".format(pycamp.headquarters))


@admin_needed
async def add_pycamp(update, context):
    parameters = update.message.text.split(' ', 1)
    if len(parameters) < 2:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="El comando necesita un parametro (headquarters)")
        return
    hq = parameters[1].strip()
    if not hq:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="El parámetro headquarters no puede ser vacío")
        return

    pycamp = Pycamp.get_or_create(headquarters=hq, active=True)[0]
    pycamp.set_as_only_active()
    logger.info('Creado: {}'.format(pycamp))

    msg = "El Pycamp {} fue creado.\n¿Cuándo empieza? (formato yyyy-mm-dd)"
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=msg.format(pycamp.headquarters)
    )
    return SET_DATE_STATE


async def define_start_date(update, context):
    text = update.message.text
    try:
        start_date = datetime.datetime.fromisoformat(text)
    except ValueError:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="mmm no entiendo esa fecha\\. El formato esperado es `yyyy-mm-dd`\\. ¿De nuevo?",
            parse_mode="MarkdownV2"
        )
        return SET_DATE_STATE
    
    _, pycamp = get_active_pycamp()
    pycamp.init = start_date
    pycamp.save()

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="¿Cuantos días dura el PyCamp?"
    )
    return SET_DURATION_STATE


async def define_duration(update, context):
    text = update.message.text.strip()
    try:
        duration = int(text)
    except ValueError:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="mmm no entiendo. Poné un número entero porfa."
        )
        return SET_DURATION_STATE

    _, pycamp = get_active_pycamp()
    pycamp.end = pycamp.init + datetime.timedelta(
        days=duration - 1, 
        hours=23,
        minutes=59, 
        seconds=59,
        milliseconds=99
    )
    pycamp.save()

    msg = "Listo, el PyCamp '{}' está activo, desde el {} hasta el {}".format(
        pycamp.headquarters,
        pycamp.init.date(),
        pycamp.end.date()
    )
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=msg
    )
    return ConversationHandler.END


async def cancel(update, context):
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Se canceló la carga del PyCamp...")
    return ConversationHandler.END


load_start_pycamp = ConversationHandler(
    entry_points=[CommandHandler('empezar_pycamp', add_pycamp)],
    states={
        SET_DATE_STATE: [MessageHandler(filters.TEXT, define_start_date)],
        SET_DURATION_STATE: [MessageHandler(filters.TEXT, define_duration)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


@active_needed
@admin_needed
async def end_pycamp(update, context):
    parameters = update.message.text.split(' ')
    if len(parameters) == 2:
        date = datetime.datetime.fromisoformat(parameters[1])
    else:
        date = datetime.datetime.now()

    is_active, pycamp = get_active_pycamp()
    pycamp.active = False
    pycamp.end = date
    pycamp.save()

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Terminó Pycamp :( ! {}".format(date))


async def add_pycampista_to_pycamp(update, context):
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    pycampista = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]

    parameters = update.message.text.split(' ')
    if len(parameters) == 2:
        pycamp = get_pycamp_by_name(parameters[1])
    else:
        is_active, pycamp = get_active_pycamp()
    PycampistaAtPycamp.get_or_create(pycamp=pycamp, pycampista=pycampista)

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="El pycampista {} fue agregado al pycamp {}".format(username,
                                                                 pycamp.headquarters))


async def list_pycamps(update, context):
    pycamps = Pycamp.select()
    text = ['Pycamps:']
    for pycamp in pycamps:
        text.append(str(pycamp))

    text = "\n\n".join(text)
    await update.message.reply_text(text)


@active_needed
async def list_pycampistas(update, context):
    is_active, pycamp = get_active_pycamp()

    pycampistas_at_pycamp = PycampistaAtPycamp.select().where(
        PycampistaAtPycamp.pycamp == pycamp)

    text = ['Pycampistas:']
    for pap in pycampistas_at_pycamp:
        text.append(str(pap.pycampista))

    text = "\n\n".join(text)
    await update.message.reply_text(text)


def set_handlers(application):
    application.add_handler(load_start_pycamp)
    application.add_handler(
        CommandHandler('terminar_pycamp', end_pycamp))
    application.add_handler(
        CommandHandler('activar_pycamp', set_active_pycamp))
    application.add_handler(
        CommandHandler('pycamps', list_pycamps))
    application.add_handler(
        CommandHandler('voy_al_pycamp', add_pycampista_to_pycamp))
    application.add_handler(
        CommandHandler('pycampistas', list_pycampistas))
