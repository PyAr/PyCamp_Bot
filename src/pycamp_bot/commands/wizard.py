import random
from collections import defaultdict
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
    return slot[0].day != pycamp.init.day or slot[0].hour >= LUNCH_TIME_END_HOUR
            

def is_before_last_lunch_slot(pycamp, slot):
    """Must be False if slot starts after lunch the last day"""
    return slot[0].day != pycamp.end.day or slot[0].hour < LUNCH_TIME_START_HOUR


def is_valid_wizard_slot(pycamp, slot):
    """If True the slot is kept."""
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
        text="¡Felicidades! Has sido registrado como magx."
    )


async def summon_wizard(update, context):
    _, pycamp = get_active_pycamp()
    wizard = pycamp.get_current_wizard()
    if wizard is None:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="No hay ningunx magx agendado a esta hora :-("
        )
        return

    username = update.message.from_user.username
    if username == wizard.username:
        await context.bot.send_message(
            chat_id=wizard.chat_id,
            text="🧙"
        )
        await context.bot.send_message(
            chat_id=wizard.chat_id,
            text="Checkeá tu cabeza: si no ténes el sombrero de magx ¡deberías!\n(soltá la compu)"
        )
    else:
        await context.bot.send_message(
            chat_id=wizard.chat_id,
            text="PING PING PING MAGX! @{} te necesesita!".format(username)
        )
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Tu magx asignadx es: @{}".format(wizard.username)
        )

async def notify_scheduled_slots_to_wizard(update, context, pycamp, wizard, agenda):
    per_day = defaultdict(list)
    for entry in agenda:
        k = entry.init.strftime("%a %d de %b")
        per_day[k].append(entry)

    msg = "Esta es tu agenda de mago para el PyCamp {}".format(pycamp.headquarters)
    for day, items in per_day.items():
        msg += "\nEl día _{}_:\n".format(day)
        for i in items:
            msg += "\t \\- {} a {}\n".format(
                i.init.strftime("%H:%M"),
                i.end.strftime("%H:%M"),
            )

    await context.bot.send_message(
        chat_id=wizard.chat_id,
        text=msg,
        parse_mode="MarkdownV2"
    )


async def notify_schedule_to_wizards(update, context, pycamp):
    for wizard in pycamp.get_wizards():
        wizard_agenda = WizardAtPycamp.select().where(
            (WizardAtPycamp.pycamp == pycamp) & (WizardAtPycamp.wizard == wizard)
        ).order_by(WizardAtPycamp.init)

        await notify_scheduled_slots_to_wizard(update, context, pycamp, wizard, wizard_agenda)


def persist_wizards_schedule_in_db(pycamp):
    """
    Aux function to generate the wizards schedule and persist WizardAtPycamp instances in the DB.
    
    """
    schedule = define_wizards_schedule(pycamp)

    for slot, wizard in schedule.items():
        start, end = slot
        WizardAtPycamp.create(
            pycamp=pycamp,
            wizard=wizard,
            init=start,
            end=end
        )
        logger.debug("From {} to {} the wizard is {}".format(start, end, wizard.username))


@admin_needed
async def schedule_wizards(update, context):
    _, pycamp = get_active_pycamp()

    n = pycamp.clear_wizards_schedule()
    logger.info("Deleted wizards schedule ({} records)".format(n))

    persist_wizards_schedule_in_db(pycamp)

    await notify_schedule_to_wizards(update, context, pycamp)

    agenda = WizardAtPycamp.select().where(WizardAtPycamp.pycamp == pycamp)
    
    msg = format_wizards_schedule(agenda)
    
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=msg,
        parse_mode="MarkdownV2"
    )



def format_wizards_schedule(agenda):
    """Aux function to render the wizards schedule as a friendly  message."""
    per_day = defaultdict(list)
    for entry in agenda:
        k = entry.init.strftime("%a %d de %b")
        per_day[k].append(entry)

    msg = "Agenda de magos:"
    for day, items in per_day.items():
        msg += "\nEl día _{}_:\n".format(day)
        for i in items:
            msg += "\t \\- {} a {}:\t*{}* \n".format(
                i.init.strftime("%H:%M"), 
                i.end.strftime("%H:%M"), 
                "@" + i.wizard.username
            )
    return msg

async def show_wizards_schedule(update, context):
    show_all = False
    parameters = update.message.text.strip().split(' ', 1)
    if len(parameters) == 2:
        flag = parameters[1].strip().lower()
        show_all = (flag == "completa")
        if not show_all:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="El comando solo acepta un parámetro (opcional): 'completa'. ¿Probás de nuevo?",
            )
            return
    elif len(parameters) > 2:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="El comando solo acepta un parámetro (opcional): 'completa'. ¿Probás de nuevo?",
        )
        return
    
    _, pycamp = get_active_pycamp()

    agenda = WizardAtPycamp.select().where(WizardAtPycamp.pycamp == pycamp)
    if not show_all:
        agenda = agenda.where(WizardAtPycamp.end > datetime.now())
    agenda = agenda.order_by(WizardAtPycamp.init)
    msg = format_wizards_schedule(agenda)
    
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=msg,
        parse_mode="MarkdownV2"
    )
    logger.debug("Wizards schedule delivered to {}".format(update.message.from_user.username))



def set_handlers(application):
    application.add_handler(
            CommandHandler('evocar_magx', summon_wizard))
    application.add_handler(
            CommandHandler('ser_magx', become_wizard))
    application.add_handler(
        CommandHandler('agendar_magx', schedule_wizards))
    application.add_handler(
        CommandHandler('ver_agenda_magx', show_wizards_schedule))
