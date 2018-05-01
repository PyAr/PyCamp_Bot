import logging
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler, ConversationHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import token_secure
from models import Pycampista, Project, ProjectOwner, Slot, Vote, Wizard


updater = Updater(token=token_secure.TOKEN)
dispatcher = updater.dispatcher


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


updater.start_polling()

# command /start give user a message
def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Hola ' + update.message.from_user.first_name + '! Bienvenidx')


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def text_input(bot, update):
    '''This function handles text sent by the user'''
    username = update.message.from_user.username
    status = users_status.get(username, None)

    print ("---------------------------------------------------------------")
    print ("usuario: " + update.message.from_user.username)
    print ("texto: " + update.message.text )
    
    if status:
        print ("status:", status)
    else:
        print("User without status")
    action = status_reference.get(status, None)

    if action:
        action(bot, update)


def ayuda(bot, update):
    bot.send_message(chat_id= update.message.chat_id,
        text=
        '''Este bot facilita la carga, administración y procesamiento de proyectos y votos durante el PyCamp
        
        El proceso se divide en 3 etapas:
        
        Primera etapa: Lxs responsables de los proyectos cargan sus proyectos mediante el comando /cargar_proyecto. Solo un responsable carga el proyecto, y luego si hay otrxs responsables adicionales, pueden agregarse con el comando /ownear.
        
        Segunda etapa: Mediante el comando /votar todxs lxs participantes votan los proyectos que se expongan. Esto se puede hacer a medida que se expone, o al haber finalizado todas las exposiciones. Si no se está segurx de un proyecto, conviene no votar nada, ya que luego podés volver a ejecutar el comando y votar aquellas cosas que no votaste. NO SE PUEDE CAMBIAR TU VOTO UNA VEZ HECHO.
        
        Tercera etapa: Lxs admins mergean los proyectos que se haya decidido mergear durante las exposiciones (Por tematica similar, u otros motivos), y luego se procesan los datos para obtener el cronograma final.
        
        Comandos adicionales: /ser_magx te transforma en el/la Magx de turno. /evocar_magx pingea a la/el Magx de turno que necesitas su ayuda. Con un gran poder, viene una gran responsabilidad''')


# asociate functions with user status
status_reference = {
    UserStatus.NAMING_PROJECT: naming_project,
    UserStatus.ASSIGNING_PROJECT_TOPIC: project_topic,
    UserStatus.ASSIGNING_PROJECT_LEVEL: project_level,
    UserStatus.OWNEO: owneo,
}


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


updater.dispatcher.add_handler(load_project_handler)
updater.dispatcher.add_handler(merge_project_handler)
updater.dispatcher.add_handler(CommandHandler('merge', merge  ))
updater.dispatcher.add_handler(CommandHandler('empezar_votacion', start_voting  ))
updater.dispatcher.add_handler(CommandHandler('ayuda', ayuda))
updater.dispatcher.add_handler(CommandHandler('votar', vote))
updater.dispatcher.add_handler(CommandHandler('evocar_magx', summon_wizard))
updater.dispatcher.add_handler(CommandHandler('ser_magx', become_wizard))
updater.dispatcher.add_handler(CommandHandler('terminar_votacion', end_voting))
updater.dispatcher.add_handler(CommandHandler('empezar_carga_proyectos', start_project_load))
updater.dispatcher.add_handler(CommandHandler('terminar_carga_proyectos', end_project_load))
updater.dispatcher.add_handler(CommandHandler('ownear', ownear))
updater.dispatcher.add_handler(CommandHandler('proyectos', projects))
updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.dispatcher.add_error_handler(error)
dispatcher.add_handler(MessageHandler(Filters.text, text_input))