import datetime
import logging

from telegram.ext import CommandHandler

from pycamp_bot.models import Pycamp
from pycamp_bot.models import Pycampista
from pycamp_bot.models import PycampistaAtPycamp
from pycamp_bot.commands.auth import admin_needed

logger = logging.getLogger(__name__)


def get_pycamp_by_name(name):
    pycamps = Pycamp.select().where(Pycamp.headquarters == name)
    count = pycamps.count()
    if count == 1:
        return pycamps[0]
    logger.info('There is some error. Pycamps with name {} has count != 1 ({})'.format(name, count))
    return None


def get_active_pycamp():
    active = Pycamp.select().where(Pycamp.active == True)
    if active.count() == 0:
        return False, None
    else:
        return True, active[0]


def active_needed(f):
    def wrap(*args, **kargs):
        bot, update = args
        is_active, _ = get_active_pycamp()
        if is_active:
            f(*args)
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="No hay un PyCamp activo.")
    return wrap


@admin_needed
def set_active_pycamp(bot, update):
    is_active, pycamp = get_active_pycamp()
    parameters = update.message.text.split(' ')

    if is_active:
        pycamp.active = False
        pycamp.save()

    if not len(parameters) == 2:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="El comando necesita un parametro (pycamp name)")
        return

    pycamp = get_pycamp_by_name(parameters[1])
    if pycamp is None:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="El Pycamp {} no existe".format(parameters[1]))
        return

    pycamp.active = True
    pycamp.save()

    bot.send_message(
        chat_id=update.message.chat_id,
        text="El Pycamp {} ahora esta activo".format(pycamp.headquarters))


@admin_needed
def add_pycamp(bot, update):
    parameters = update.message.text.split(' ')
    if not len(parameters) == 2:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="El comando necesita un parametro (pycamp name)")
        return

    pycamp = Pycamp.get_or_create(headquarters=parameters[1])[0]

    bot.send_message(
        chat_id=update.message.chat_id,
        text="El Pycamp {} fue creado.".format(pycamp.headquarters))


@active_needed
@admin_needed
def start_pycamp(bot, update):
    parameters = update.message.text.split(' ')
    if len(parameters) == 2:
        date = datetime.datetime.fromisoformat(parameters[1])
    else:
        date = datetime.datetime.now()

    is_active, pycamp = get_active_pycamp()
    pycamp.init = date
    pycamp.save()

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Empezó Pycamp :) ! {}".format(date))


@active_needed
@admin_needed
def end_pycamp(bot, update):
    parameters = update.message.text.split(' ')
    if len(parameters) == 2:
        date = datetime.datetime.fromisoformat(parameters[1])
    else:
        date = datetime.datetime.now()

    is_active, pycamp = get_active_pycamp()
    pycamp.end = date
    pycamp.save()

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Terminó Pycamp :( ! {}".format(date))


def add_pycampista_to_pycamp(bot, update):
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    pycampista = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]

    parameters = update.message.text.split(' ')
    if len(parameters) == 2:
        pycamp = get_pycamp_by_name(parameters[1])
    else:
        is_active, pycamp = get_active_pycamp()
    PycampistaAtPycamp.get_or_create(pycamp=pycamp, pycampista=pycampista)

    bot.send_message(
        chat_id=update.message.chat_id,
        text="El pycampista {} fue agregado al pycamp {}".format(username,
                                                                 pycamp.headquarters))


def list_pycamps(bot, update):
    pycamps = Pycamp.select()
    text = ['Pycamps:']
    for pycamp in pycamps:
        text.append(str(pycamp))

    text = "\n\n".join(text)
    update.message.reply_text(text)


@active_needed
def list_pycampistas(bot, update):
    is_active, pycamp = get_active_pycamp()

    pycampistas_at_pycamp = PycampistaAtPycamp.select().where(
        PycampistaAtPycamp.pycamp == pycamp)

    text = ['Pycampistas:']
    for pap in pycampistas_at_pycamp:
        text.append(str(pap.pycampista))

    text = "\n\n".join(text)
    update.message.reply_text(text)


def set_handlers(updater):
    updater.dispatcher.add_handler(
        CommandHandler('empezar_pycamp', start_pycamp))
    updater.dispatcher.add_handler(
        CommandHandler('terminar_pycamp', end_pycamp))
    updater.dispatcher.add_handler(
        CommandHandler('activar_pycamp', set_active_pycamp))
    updater.dispatcher.add_handler(
        CommandHandler('agregar_pycamp', add_pycamp))
    updater.dispatcher.add_handler(
        CommandHandler('pycamps', list_pycamps))
    updater.dispatcher.add_handler(
        CommandHandler('voy_al_pycamp', add_pycampista_to_pycamp))
    updater.dispatcher.add_handler(
        CommandHandler('pycampistas', list_pycampistas))
