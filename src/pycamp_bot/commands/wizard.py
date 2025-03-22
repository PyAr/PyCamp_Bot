import random
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import cycle
from telegram.ext import CommandHandler
from telegram.error import BadRequest
from pycamp_bot.models import Pycampista, WizardAtPycamp
from pycamp_bot.commands.auth import admin_needed
from pycamp_bot.commands.manage_pycamp import get_active_pycamp
from pycamp_bot.logger import logger
from pycamp_bot.utils import escape_markdown, active_pycamp_needed


LUNCH_TIME_START_HOUR = 13
LUNCH_TIME_END_HOUR = 14
WIZARD_TIME_START_HOUR = 9
WIZARD_TIME_END_HOUR = 20

MSG_MAX_LEN = 4096


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
    * Magxs trabajan de 9 a 19, sacando almuerzo (13 a 14).
    * Magxs trabajan desde el mediodía del primer día, hasta el mediodía del último día.

    Slots son [start; end)
    """
    wizard_start = pycamp.init
    wizard_end = pycamp.end
    slots = []
    current_period = wizard_start
    while current_period < wizard_end:  # TODO: check fields None
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
    all_wizards = pycamp.get_wizards()
    if len(all_wizards) == 0:
        return {}
    
    wizard_per_slot = {}
    wizards_iter = cycle(all_wizards)
    for slot in compute_wizards_slots(pycamp):
        # Cycle through the wizards, asigning them to slots.
        wizard = next(wizards_iter)
        if wizard.is_busy(*slot):
            # If the target wizard is busy in this time slot, try to find another available wizard
            if all(w.is_busy(*slot) for w in all_wizards):
                # Nada que hacer, todos ocupados. Queda
                logger.warning(
                    'Queda el magx {} con conflicto en el slot {}'.format(wizard.username, slot)
                )
            else:
                # Sigo hasta el próximo que esté disponible
                continue
        wizard_per_slot[slot] = wizard
    
    return wizard_per_slot


@active_pycamp_needed
async def become_wizard(update, context, pycamp=None):
    username = update.message.from_user.username
    chat_id = update.message.chat_id

    pycamp.add_wizard(username, chat_id)

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="¡Felicidades! Has sido registrado como magx."
    )


@active_pycamp_needed
async def list_wizards(update, context, pycamp=None):
    msg = ""
    for i, wizard in enumerate(pycamp.get_wizards()):
        msg += "{}) @{}\n".format(i+1, wizard.username)
    try:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=msg
        )
    except BadRequest as e:
        logger.exception("Coulnd't deliver the Wizards list to {}".format(update.message.from_user.username))


@active_pycamp_needed
async def summon_wizard(update, context, pycamp=None):
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
        try:
            await context.bot.send_message(
                chat_id=wizard.chat_id,
                text="PING PING PING MAGX! @{} te necesita!".format(username)
            )
            text="Tu magx asignadx es: @{}".format(wizard.username)
        except BadRequest:
            text="No se pudo notificar al magx asignadx: @{} Andá a buscarlo...".format(wizard.username)
            logger.warn("Coulnd't notify the wizard {}".format(wizard.username))
        finally:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=text
            )

async def notify_scheduled_slots_to_wizard(update, context, pycamp, wizard, agenda):
    per_day = defaultdict(list)
    for entry in agenda:
        k = entry.init.strftime("%a %d de %b")
        per_day[k].append(entry)

    msg = "Esta es tu agenda de magx para el PyCamp {}".format(pycamp.headquarters)
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

        try:
            await notify_scheduled_slots_to_wizard(update, context, pycamp, wizard, wizard_agenda)
            logger.debug("Notified wizard schedule to {}".format(wizard.username))
        except BadRequest:
            logger.warn("Coulnd't notify its wizard schedule to {}".format(wizard.username))


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


@admin_needed
@active_pycamp_needed
async def schedule_wizards(update, context, pycamp=None):
    n = pycamp.clear_wizards_schedule()
    logger.info("Deleted wizards schedule ({} records)".format(n))

    persist_wizards_schedule_in_db(pycamp)
    logger.info("Wizards schedule persisted in the DB.")


    await notify_schedule_to_wizards(update, context, pycamp)

    agenda = WizardAtPycamp.select().where(WizardAtPycamp.pycamp == pycamp)
    
    msg = format_wizards_schedule(agenda)
    try:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=msg,
            parse_mode="MarkdownV2"
        )  
    except BadRequest as e:
        m = "Coulnd't return the Wizards list to the admin. ".format(update.message.from_user.username)
        if len(msg) >= MSG_MAX_LEN:
            m += "The message is too long. Check the data in the DB ;-)"
        logger.exception(m)


def format_wizards_schedule(agenda):
    """Aux function to render the wizards schedule as a friendly  message."""
    per_day = defaultdict(list)
    for entry in agenda:
        k = entry.init.strftime("%a %d de %b")
        per_day[k].append(entry)

    msg = "Agenda de magxs:"
    for day, items in per_day.items():
        msg += "\nEl día _{}_:\n".format(day)
        for i in items:
            msg += "\t \\- {} a {}:\t*{}* \n".format(
                i.init.strftime("%H:%M"), 
                i.end.strftime("%H:%M"), 
                "@" + escape_markdown(i.wizard.username)
            )
    return msg

def aux_resolve_show_all(message):
    show_all = False
    parameters = message.text.strip().split(' ', 1)
    if len(parameters) == 2:
        flag = parameters[1].strip().lower()
        show_all = (flag == "completa")  # Once here, the only parameter must be valid
        if not show_all:
            # The parameter was something else...
            raise ValueError("Wrong parameter")
    elif len(parameters) > 2:
        # Too many parameters...
        raise ValueError("Wrong parameter")
    return show_all


@active_pycamp_needed
async def show_wizards_schedule(update, context, pycamp=None):
    try:
        show_all = aux_resolve_show_all(update.message)
    except ValueError:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="El comando solo acepta un parámetro (opcional): 'completa'. ¿Probás de nuevo?",
        )
        return

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
            CommandHandler('ver_magx', list_wizards))
    application.add_handler(
        CommandHandler('agendar_magx', schedule_wizards))
    application.add_handler(
        CommandHandler('ver_agenda_magx', show_wizards_schedule))
