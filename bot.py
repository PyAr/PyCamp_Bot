import logging
import json
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler, ConversationHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from enum import Enum
import time
import token_secure
import itertools
from models import Pycampista, Project, ProjectOwner, Slot, Vote


updater = Updater(token=token_secure.TOKEN)
dispatcher = updater.dispatcher


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


updater.start_polling()

#Global info
vote_auth = False
project_auth = False
DATA = json.load(open('data.json'))
autorizados = ["WinnaZ","sofide", "ArthurMarduk"]
users_status = {}
current_projects = {}

NOMBRE, DIFICULTAD, TOPIC = range(3)

class UserStatus(Enum):
    NAMING_PROJECT = 1
    ASSIGNING_PROJECT_TOPIC = 2
    ASSIGNING_PROJECT_LEVEL = 3
    OWNEO = 4


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
    username = update.message.from_user.username

    bot.send_message(
        '''Este bot facilita la carga, administración y procesamiento de proyectos y votos durante el PyCamp
        
        El proceso se divide en 3 etapas:
        
        Primera etapa: Los responsables de los proyectos cargan sus proyectos mediante el comando /cargar_proyecto. Solo un responsable carga el proyecto, y luego si hay un responsable adicional, puede agregarse con el comando /ownear.
        
        Segunda etapa: Mediante el comando /votar todxs lxs participantes votan los proyectos que se expongan. Esto se puede hacer a medida que se expone, o al haber finalizado todas las exposiciones.
        
        Tercera etapa: Lxs admins mergean los proyectos que se haya decidido mergear durante las exposiciones (Por tematica similar, u otros motivos), y luego se procesan los datos para obtener el cronograma final.''')

def load_project(bot, update):
    '''Command to start the cargar_proyectos dialog'''
    username = update.message.from_user.username

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Usuario: " + username
    )

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Ingresá el Nombre del Proyecto a proponer",
    )
    return NOMBRE


def naming_project(bot, update):
    '''Dialog to set project name'''
    username = update.message.from_user.username
    text = update.message.text

    new_project = Project(name=text)
    current_projects[username] = new_project

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Estamos cargando tu proyecto {}!".format(username)
    )
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Tu proyecto se llama: {}".format(text)
    )
    bot.send_message(
        chat_id=update.message.chat_id,
        text="""Cual es el nivel de dificultad?
            1 = newbie friendly
            2 = intermedio
            3 = python avanzado"""
    )
    return DIFICULTAD

def project_level(bot, update):
    '''Dialog to set project level'''
    username = update.message.from_user.username
    text = update.message.text

    if text in ["1", "2", "3"]:
        new_project = current_projects[username]
        new_project.difficult_level = text

        bot.send_message(
            chat_id=update.message.chat_id,
            text="Ok! Tu proyecto es nivel {}".format(text)
        )
        bot.send_message(
            chat_id=update.message.chat_id,
            text="""Ahora necesitamos que nos digas la temática de tu proyecto.
            Algunos ejemplos pueden ser:
            - flask
            - django
            - telegram
            - inteligencia artificial
            - recreativo"""
        )
        return TOPIC
    else:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Nooooooo input no válido, por favor ingresá 1, 2 o 3".format(text)
        )
        return DIFICULTAD


def project_topic(bot, update):
    '''Dialog to set project topic'''
    username = update.message.from_user.username
    text = update.message.text
    chat_id = update.message.chat_id

    new_project = current_projects[username]
    new_project.topic = text

    new_project.save()

    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]

    project_owner = ProjectOwner.get_or_create(project=new_project, owner=user)

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Excelente {}! La temática de tu proyecto es {}.".format(username, text)
    )
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Tu proyecto ha sido cargado".format(username, text)
    )
    return ConversationHandler.END

def cancel(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Has cancelado la carga del proyecto".format(username, text)
        )
    return ConversationHandler.END


def ownear(bot, update):

    username = update.message.from_user.username
    lista_proyectos = [p.name for p in Project.select()]
    dic_proyectos = dict(enumerate(lista_proyectos))
    bot.send_message(
        chat_id = update.message.chat_id,
        text="¿A qué proyecto querés agregarte como responsable? (Dar número)" 
    )
    for k,v in dic_proyectos.items():
        bot.send_message(
            chat_id = update.message.chat_id,
            text = "{}: {}".format(k,v)

        )
    users_status[username] = UserStatus.OWNEO

def owneo(bot, update):
    '''Dialog to set project responsable'''
    username = update.message.from_user.username
    text = update.message.text
    chat_id = update.message.chat_id
    lista_proyectos = [p.name for p in Project.select()]
    dic_proyectos = dict(enumerate(lista_proyectos))
    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]
    project_owner = ProjectOwner(project=dic_proyectos[int(text)], owner=user)
    project_owner.save()
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Perfecto. Chauchi"
    )


# asociate functions with user status
status_reference = {
    UserStatus.NAMING_PROJECT: naming_project,
    UserStatus.ASSIGNING_PROJECT_TOPIC: project_topic,
    UserStatus.ASSIGNING_PROJECT_LEVEL: project_level,
    UserStatus.OWNEO: owneo,
}


def empezar_votacion(bot, update):
    global vote_auth
    if vote_auth == False:
        if update.message.from_user.username in autorizados:
            update.message.reply_text("Autorizado")
            update.message.reply_text("Votación Abierta")
            vote_auth = True
        else:
            update.message.reply_text("No estas Autorizadx para hacer esta acción")
    else:
        update.message.reply_text("La votacion ya estaba abierta")


def vote(bot, update):
    """"""
    if vote_auth:
        update.message.reply_text(
            'Te interesa el proyecto:'
        )

        # if there is not project in the database, create a new project
        if not Project.select().exists():
            Project.create(name='PROYECTO DE PRUEBA')

        # ask user for each project in the database
        for project in Project.select():
            keyboard = [[InlineKeyboardButton("Si!" , callback_data="si"),
                        InlineKeyboardButton("Nop", callback_data="no")]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            update.message.reply_text(
                text=project.name,
                reply_markup=reply_markup
            )
    else:
            update.message.reply_text("Votación Cerrada")


def button(bot, update):
    '''Save user vote in the database'''
    query = update.callback_query
    username = query.message['chat']['username']
    chat_id = query.message.chat_id
    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]
    project_name = query.message['text']

    # Get project from the database
    project = Project.get(Project.name == project_name)

    # create a new vote object
    new_vote = Vote(pycampista=user, project=project)

    # Save vote in the database and send a message
    if query.data == "si":
        result = 'Interesadx en: ' + project_name + ' 👍'
        new_vote.interest = True
        new_vote.save()
    else:
        new_vote.interest = False
        new_vote.save()
        result = 'No te interesa el proyecto ' + project_name

    bot.edit_message_text(text=result,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

def terminar_votacion(bot, update):
    if update.message.from_user.username in autorizados:
        with open('data.json', 'w') as f:
            json.dump(DATA, f, indent=2)
        update.message.reply_text("Autorizado")
        update.message.reply_text("Información Cargada, votación cerrada")
        vote_auth = False
    else:
        update.message.reply_text("No estas Autorizadx para hacer esta ación")


def empezar_carga_proyectos(bot, update):
    """Allow people to upload projects"""
    global project_auth
    if not project_auth:
        if update.message.from_user.username in autorizados:
            update.message.reply_text("Autorizado")
            update.message.reply_text("Carga de proyectos Abierta")
            vote_auth = True
        else:
            update.message.reply_text("No estas Autorizadx para hacer esta acción")
    else:
        update.message.reply_text("La carga de proyectos ya estaba abierta")


def terminar_carga_proyectos(bot, update):
    """Prevent people for keep uploading projects"""
    if update.message.from_user.username in autorizados:
        with open('data.json', 'w') as f:
            json.dump(DATA, f, indent=2)
        update.message.reply_text("Autorizado")
        update.message.reply_text("Información Cargada, carga de proyectos cerrada")
        vote_auth = False
    else:
        update.message.reply_text("No estas Autorizadx para hacer esta ación")


def projects(bot, update):
    """Prevent people for keep uploading projects"""
    projects = Project.select()
    text = []
    for project in projects:
        owners = map(lambda po: po.owner.username, project.projectowner_set.iterator())
        project_text = "{} \n owner: {} \n topic: {} \n level: {}".format(
            project.name,
            ', '.join(owners),
            project.topic,
            project.difficult_level
        )
        text.append(project_text)

    text = "\n\n".join(text)

    update.message.reply_text(text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


load_project_handler = ConversationHandler(
       entry_points=[CommandHandler('cargar_proyecto', load_project)],
       states={
           NOMBRE: [MessageHandler(Filters.text, naming_project)],
           DIFICULTAD : [MessageHandler(Filters.text, project_level)],
           TOPIC: [MessageHandler(Filters.text, project_topic )],
       },
       fallbacks=[CommandHandler('cancel', cancel)]
   )

updater.dispatcher.add_handler(load_project_handler)
updater.dispatcher.add_handler(CommandHandler('empezar_votacion', empezar_votacion))
updater.dispatcher.add_handler(CommandHandler('ayuda', ayuda))
updater.dispatcher.add_handler(CommandHandler('votar', vote))
updater.dispatcher.add_handler(CommandHandler('terminar_votacion', terminar_votacion))
updater.dispatcher.add_handler(CommandHandler('empezar_carga_proyectos', empezar_carga_proyectos))
updater.dispatcher.add_handler(CommandHandler('terminar_carga_proyectos', terminar_carga_proyectos))
updater.dispatcher.add_handler(CommandHandler('ownear', ownear))
updater.dispatcher.add_handler(CommandHandler('proyectos', projects))
updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.dispatcher.add_error_handler(error)
dispatcher.add_handler(MessageHandler(Filters.text, text_input))
