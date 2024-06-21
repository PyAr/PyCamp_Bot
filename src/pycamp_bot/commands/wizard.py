import random
from datetime import datetime, timedelta

from telegram.ext import CommandHandler
from pycamp_bot.models import Pycampista, WizardAtPycamp
from pycamp_bot.commands.auth import admin_needed
from pycamp_bot.commands.manage_pycamp import get_active_pycamp
from pycamp_bot.logger import logger


LUNCH_TIME_START_HOUR = 13
LUNCH_TIME_END_HOUR = 14
WIZARD_TIME_START_HOUR = 9
WIZARD_TIME_END_HOUR = 20


def is_wizard_time_slot(slot):
    return slot[0].hour in range(WIZARD_TIME_START_HOUR, WIZARD_TIME_END_HOUR)


def is_lunch_time_slot(slot):
    return slot[0].hour in range(LUNCH_TIME_START_HOUR, LUNCH_TIME_END_HOUR)


def is_after_first_lunch_slot(pycamp, slot):
    return slot[0].day != pycamp.start.day or slot[0].hour >= LUNCH_TIME_END_HOUR
            


def is_before_last_lunch_slot(pycamp, slot):
    return slot[0].day != pycamp.end.day or slot[0].hour < LUNCH_TIME_START_HOUR


def is_valid_wizard_slot(pycamp, slot):
    return (
        is_wizard_time_slot(slot)
        and not is_lunch_time_slot(slot)
        and is_after_first_lunch_slot(pycamp, slot)
        and is_before_last_lunch_slot(pycamp, slot)
    )


def clean_wizards_free_slots(pycamp, slots):
    return [slot for slot in slots if is_valid_wizard_slot(pycamp, slot)]


def compute_wizards_slots(pycamp):
    """
    * Magos trabajan de 9 a 19, sacando almuerzo (13 a 14).
    * Magos trabajan desde el mediodía del primer día, hasta el mediodía del último día.
    Slots son [start; end)
    """
    wizard_start = pycamp.init
    wizard_end = pycamp.end
    slots = []
    current_period = wizard_start
    while current_period < wizard_end:
        slot_start = current_period
        slot_end = current_period + timedelta(minutes=pycamp.wizard_slot_duration)
        slots.append(
            (slot_start, slot_end)
        )
        current_period = slot_end

    slots = clean_wizards_free_slots(pycamp, slots)

    return slots


def define_wizards_schedule(pycamp):
    """
    Returns a dict whose keys are times and values are wizards (Pycampistas instances).

    """
    slots_list = compute_wizards_slots(pycamp)
    wizards_list = pycamp.get_wizards()
    n_wizards = wizards_list.count()
    wizard_per_slot = {}
    idx = 0
    for slot in slots_list:
        wizard = wizards_list[idx%n_wizards]
        n_iter = 0  # railguard
        while wizard.is_busy(slot):
            logger.info('Mago {} con conflicto en el slot {}. Pruebo otro.'.format(wizard.username, slot))
            if n_iter == n_wizards:
                logger.warning('Queda el mago {} con conflicto en el slot {}'.format(wizard, slot))
                break
            idx += 1
            wizard = wizards_list[idx%n_wizards]
            n_iter += 1
        wizard_per_slot[slot] = wizard
        idx += 1
    return wizard_per_slot

async def become_wizard(update, context):
    current_wizards = Pycampista.select().where(Pycampista.wizard is True)

    for w in current_wizards:
        w.current = False
        w.save()

    username = update.message.from_user.username
    chat_id = update.message.chat_id

    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]
    user.wizard = True
    user.save()

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Felicidades! Eres el Magx de turno"
    )


async def summon_wizard(update, context):
    username = update.message.from_user.username
    wizard_list = list(Pycampista.select().where(Pycampista.wizard==True))
    if len(wizard_list) == 0:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="No hay ningunx magx todavia"
        )
    else:
        wizard = random.choice(wizard_list)
        await context.bot.send_message(
            chat_id=wizard.chat_id,
            text="PING PING PING MAGX! @{} te necesesita!".format(username)
        )
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Tu magx asignadx es: @{}".format(wizard.username)
        )


@admin_needed
async def schedule_wizards(update, context):
    _, pycamp = get_active_pycamp()
    logger.info(pycamp)

    schedule = define_wizards_schedule(pycamp)

    for slot, wizard in schedule.items():
        start, end = slot
        WizardAtPycamp.create(
            pycamp=pycamp,
            wizard=wizard,
            slot_ini=start,
            slot_end=end
        )
        logger.debug("From {} to {} the wizard is {}".format(start, end, wizard.username))

    # Mandar mensajes a los magos con su agenda propia
    msg = "Lista la agenda de magos."
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=msg
    )


def set_handlers(application):
    application.add_handler(
            CommandHandler('evocar_magx', summon_wizard))
    application.add_handler(
            CommandHandler('ser_magx', become_wizard))
    application.add_handler(
        CommandHandler('agendar_magos', schedule_wizards))
