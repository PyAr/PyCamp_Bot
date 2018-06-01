import logging
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler, ConversationHandler)
import token_secure
from models import Pycampista, Project, ProjectOwner, Slot, Vote, Wizard

#Handlers
from merge import merge, merge_project_handler
from voting import vote, start_voting, end_voting, button
from load_project import load_project, start_project_load, end_project_load, load_project_handler
from wizard import become_wizard, summon_wizard
from own import own, own_project_handler
from utils import projects
from raffle import raffle

updater = Updater(token=token_secure.TOKEN)
dispatcher = updater.dispatcher

users_status = {}
current_projects = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


updater.start_polling()

# command /start give user a message
def start(bot, update):
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]
    bot.send_message(
        chat_id=chat_id,
        text='Hola ' + update.message.from_user.first_name + '! Bienvenidx')


def text_input(bot, update):
    '''This function handles text sent by the user'''
    username = update.message.from_user.username
    status = users_status.get(username, None)
    bot.send_message(chat_id=update.message.chat_id,
    chat="gabi gato")

    print ("---------------------------------------------------------------")
    print ("usuario: " + update.message.from_user.username)
    print ("texto: " + update.message.text )
    

def help(bot, update):
    bot.send_message(chat_id= update.message.chat_id,
        text=
        '''Este bot facilita la carga, administración y procesamiento de proyectos y votos durante el PyCamp
        
        El proceso se divide en 3 etapas:
        
        Primera etapa: Lxs responsables de los proyectos cargan sus proyectos mediante el comando /cargar_proyecto. Solo un responsable carga el proyecto, y luego si hay otrxs responsables adicionales, pueden agregarse con el comando /ownear.
        
        Segunda etapa: Mediante el comando /votar todxs lxs participantes votan los proyectos que se expongan. Esto se puede hacer a medida que se expone, o al haber finalizado todas las exposiciones. Si no se está segurx de un proyecto, conviene no votar nada, ya que luego podés volver a ejecutar el comando y votar aquellas cosas que no votaste. NO SE PUEDE CAMBIAR TU VOTO UNA VEZ HECHO.
        
        Tercera etapa: Lxs admins mergean los proyectos que se haya decidido mergear durante las exposiciones (Por tematica similar, u otros motivos), y luego se procesan los datos para obtener el cronograma final.
        
        Comandos adicionales: 
        /proyectos te muestra la informacion de todos los proyectos y sus responsables.
        /ser_magx te transforma en el/la Magx de turno. 
        /evocar_magx pingea a la/el Magx de turno, informando que necesitas su ayuda. Con un gran poder, viene una gran responsabilidad
        /sorteo realiza un sorteo entre todxs lxs Pycampistas.''')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

#HANDLERS
#handler that processes erros
updater.dispatcher.add_error_handler(error)

#Thread handlers 
updater.dispatcher.add_handler(load_project_handler)
updater.dispatcher.add_handler(merge_project_handler)
updater.dispatcher.add_handler(own_project_handler)

#Handlers that get activated using / 
updater.dispatcher.add_handler(CommandHandler('mergear', merge))


dispatcher.add_handler(CommandHandler('start', start))

updater.dispatcher.add_handler(CommandHandler('ayuda', help))

updater.dispatcher.add_handler(CommandHandler('evocar_magx', summon_wizard))
updater.dispatcher.add_handler(CommandHandler('ser_magx', become_wizard))

updater.dispatcher.add_handler(CommandHandler('empezar_votacion', start_voting))
updater.dispatcher.add_handler(CommandHandler('votar', vote))
updater.dispatcher.add_handler(CommandHandler('terminar_votacion', end_voting))

updater.dispatcher.add_handler(CommandHandler('empezar_carga_proyectos', start_project_load))
updater.dispatcher.add_handler(CommandHandler('cargar_projectos', start_project_load))
updater.dispatcher.add_handler(CommandHandler('terminar_carga_proyectos', end_project_load))

updater.dispatcher.add_handler(CommandHandler('ownear', own))

updater.dispatcher.add_handler(CommandHandler('proyectos', projects))

updater.dispatcher.add_handler(CommandHandler('sorteo', raffle))

updater.dispatcher.add_handler(CallbackQueryHandler(button))
