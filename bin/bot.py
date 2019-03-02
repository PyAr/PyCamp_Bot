import logging
import sys
import os
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler, ConversationHandler)


from pycamp_bot.models import (Pycampista, Project, ProjectOwner, Slot, Vote,
                               Wizard, models_db_connection)
from pycamp_bot.merge import merge, merge_project_handler
from pycamp_bot.voting import vote, start_voting, end_voting, button
from pycamp_bot.load_project import (load_project, start_project_load,
                                     end_project_load, load_project_handler)
from pycamp_bot.wizard import become_wizard, summon_wizard
from pycamp_bot.own import own, own_project_handler
from pycamp_bot.utils import projects
from pycamp_bot.raffle import raffle
from pycamp_bot.help_msg import HELP_MESSAGE


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


# command /start give user a message
def start(bot, update):
    logger.info('Start command')
    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text='Hola ' + update.message.from_user.first_name + '! Bienvenidx')


def text_input(bot, update):
    '''This function handles text sent by the user'''
    bot.send_message(chat_id=update.message.chat_id, chat="gabi gato")

    print ("---------------------------------------------------------------")
    print ("usuario: " + update.message.from_user.username)
    print ("texto: " + update.message.text)


def help(bot, update):
    logger.info('Returning help message')
    bot.send_message(chat_id=update.message.chat_id, text=HELP_MESSAGE)


def error(bot, update, error):
    '''Log Errors caused by Updates.'''
    logger.warning('Update {} caused error {}'.format(update, error))


def set_handlers(updater, dispatcher):
    # HANDLERS
    # handler that processes erros
    updater.dispatcher.add_error_handler(error)

    # Thread handlers
    updater.dispatcher.add_handler(load_project_handler)
    updater.dispatcher.add_handler(merge_project_handler)
    updater.dispatcher.add_handler(own_project_handler)

    # Handlers that get activated using /
    updater.dispatcher.add_handler(CommandHandler('mergear', merge))

    dispatcher.add_handler(CommandHandler('start', start))

    updater.dispatcher.add_handler(CommandHandler('ayuda', help))

    updater.dispatcher.add_handler(
            CommandHandler('evocar_magx', summon_wizard))
    updater.dispatcher.add_handler(CommandHandler('ser_magx', become_wizard))

    updater.dispatcher.add_handler(
            CommandHandler('empezar_votacion', start_voting))
    updater.dispatcher.add_handler(CommandHandler('votar', vote))
    updater.dispatcher.add_handler(
            CommandHandler('terminar_votacion', end_voting))

    updater.dispatcher.add_handler(
            CommandHandler('empezar_carga_proyectos', start_project_load))
    updater.dispatcher.add_handler(
            CommandHandler('cargar_projectos', start_project_load))
    updater.dispatcher.add_handler(
            CommandHandler('terminar_carga_proyectos', end_project_load))

    updater.dispatcher.add_handler(CommandHandler('ownear', own))

    updater.dispatcher.add_handler(CommandHandler('proyectos', projects))

    updater.dispatcher.add_handler(CommandHandler('sorteo', raffle))

    updater.dispatcher.add_handler(CallbackQueryHandler(button))


if __name__ == '__main__':
    logger.info('Starting PyCamp Bot')

    if 'TOKEN' in os.environ.keys():
        updater = Updater(token=os.environ['TOKEN'])
        dispatcher = updater.dispatcher

        users_status = {}
        current_projects = {}

        updater.start_polling()

        set_handlers(updater, dispatcher)
        models_db_connection(eval(sys.argv[1]))
    else:
        logger.info('Token not defined. Exiting.')
