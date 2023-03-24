import logging
import os
from telegram.ext import CommandHandler
from pycamp_bot.models import Pycampista


logger = logging.getLogger(__name__)


def get_admins_username():
    admins = []
    pycampistas = Pycampista.select()
    for user in pycampistas:
        if user.admin:
            admins.append(user.username)
    return admins


def is_admin(bot, update):
    """Checks if the user is authorized as admin"""
    username = update.message.from_user.username
    authorized = get_admins_username()

    if username not in authorized:
        logger.info("{} is not authorized as admin".format(username))
        return False
    else:
        logger.info("{} is authorized as admin".format(username))
        return True


def admin_needed(f):
    def wrap(*args, **kargs):
        logger.info('Admin nedeed wrapper')
        bot, update = args
        if is_admin(*args):
            return f(*args)
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="No estas Autorizadx para hacer esta acción"
            )
    return wrap


def grant_admin(bot, update):
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    text = update.message.text

    parameters = text.split(' ')
    if not len(parameters) == 2:
        bot.send_message(chat_id=chat_id,
                         text='Parametros incorrectos.')
        return

    passwrd = parameters[1]

    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]
    if 'PYCAMP_BOT_MASTER_KEY' in os.environ.keys():
        if passwrd == os.environ['PYCAMP_BOT_MASTER_KEY']:
            user.admin = True
            user.save()
            rply_msg = 'Ahora tenes el poder. Cuidado!'
        else:
            logger.info('Wrong attempt on getting admin privileges.')
            rply_msg = 'Ah ah ah, you didn\'t say the magic word.'
    else:
        logger.error('PYCAMP_BOT_MASTER_KEY env not set.')
        rply_msg = 'Hay un problema en el servidor, avisale a un admin.'

    bot.send_message(chat_id=chat_id, text=rply_msg)


@admin_needed
def revoke_admin(bot, update):
    chat_id = update.message.chat_id
    text = update.message.text

    parameters = text.split(' ')
    if not len(parameters) == 2:
        bot.send_message(chat_id=chat_id,
                         text='Parametros incorrectos.')
        return

    fallen_admin = parameters[1]

    user = Pycampista.select().where(Pycampista.username == fallen_admin)[0]
    user.admin = False
    user.save()
    bot.send_message(chat_id=chat_id,
                     text='Un admin a caido --{}--.'.format(fallen_admin))


def list_admins(bot, update):
    chat_id = update.message.chat_id

    admins = get_admins_username()
    rply_msg = 'Los administradores son:\n'

    for admin in admins:
        rply_msg += admin
        rply_msg += '\n'

    bot.send_message(chat_id=chat_id, text=rply_msg)


def set_handlers(updater):
    updater.dispatcher.add_handler(CommandHandler('su', grant_admin))
    updater.dispatcher.add_handler(CommandHandler('degradar', revoke_admin))
    updater.dispatcher.add_handler(CommandHandler('admins', list_admins))
