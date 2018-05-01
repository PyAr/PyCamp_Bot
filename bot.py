import logging
import json
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler, ConversationHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from enum import Enum
import time
import token_secure
import itertools
from models import Pycampista, Project, ProjectOwner, Slot, Vote, Wizard


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
merge_projects = []
NOMBRE, DIFICULTAD, TOPIC = range(3)
PRIMER_PROYECTO, SEGUNDO_PROYECTO = range(2)

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

def conver_to_piglatin(words):
    words = str(words).split()
    print (words)
    for word in words:
        print(word[1:] + word[0] + "ay", end = " ")
    



def text_input(bot, update):
    '''This function handles text sent by the user'''
    username = update.message.from_user.username
    status = users_status.get(username, None)

    print ("---------------------------------------------------------------")
    print ("usuario: " + update.message.from_user.username)
    print ("texto: " + update.message.text )
    
    bot.send_message(chat_id= update.message.chat_id,
        text=conver_to_piglatin(str(update.message.chat_id))
        )
    
    
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

def load_project(bot, update):
    '''Command to start the cargar_proyectos dialog'''
    username = update.message.from_user.username
    if project_auth:    
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Usuario: " + username
        )

        bot.send_message(
            chat_id=update.message.chat_id,
            text="Ingresá el Nombre del Proyecto a proponer",
        )
        return NOMBRE
    else:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Carga de projectos Cerrada"
        )

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

def merge(bot, update):
    if update.message.from_user.username in autorizados:
        lista_proyectos = [p.name for p in Project.select()]
        dic_proyectos = dict(enumerate(lista_proyectos))
        #Asks for user input regarding first project
        bot.send_message(
            chat_id = update.message.chat_id,
            text = "Decime el primer proyecto que querés combinar (En número)"
        )
        for k,v in dic_proyectos.items():
            bot.send_message(
                chat_id = update.message.chat_id,
                text = "{}: {}".format(k,v)

            )
        bot.send_message(
            chat_id = update.message.chat_id,
            text = "------------------------------------------------------------------------------")
        return PRIMER_PROYECTO

    else:
        bot.send_message(
            chat_id = update.message.chat_id,
            text= 'No estás autorizadx para llevar a cabo esta acción. Este comando solo puede ser utilizado por Admins'
        )

def primer_proyecto(bot, update):
    #Grabs first response and asks for the second one
    username = update.message.from_user.username
    text = update.message.text
    chat_id = update.message.chat_id
    lista_proyectos = [p.name for p in Project.select()]
    dic_proyectos = dict(enumerate(lista_proyectos))
    proyecto_principal = dic_proyectos[int(text)]
    merge_projects.append(proyecto_principal)
    bot.send_message(
        chat_id = update.message.chat_id,
        text = "Decime el segundo proyecto que querés combinar (En número)"
        )
    return SEGUNDO_PROYECTO

def segundo_proyecto(bot,update):
    username = update.message.from_user.username
    text = update.message.text
    chat_id = update.message.chat_id
    #Grabs second reply

    lista_proyectos = [p.name for p in Project.select()]
    dic_proyectos = dict(enumerate(lista_proyectos))
    proyecto_secundario = dic_proyectos[int(text)]
    merge_projects.append(proyecto_secundario)

    # Queries data for both projects to be merged
    proyecto_primario_query = Project.get(Project.name==merge_projects[0])
    proyecto_secundario_query = Project.get(Project.name==merge_projects[1])

    # Queries for positive votes matching the project's ID
    query_votos_primario = Vote.select().where(Vote.project==proyecto_primario_query, Vote.interest==1)
    query_votos_secundario = Vote.select().where(Vote.project==proyecto_secundario_query, Vote.interest==1)

    # Creates list with user IDs from previous votes, combines them and creates a list with non repeating items
    lista_votos_primario = [voto.pycampista_id for voto in query_votos_primario]
    lista_votos_secundario = [voto.pycampista_id for voto in query_votos_secundario]
    lista_unica = lista_votos_primario.copy()
    lista_unica.extend(lista_votos_secundario)
    lista_unica = set(lista_unica)

    # Iterates through the unique list and any voter that is not present in the first project, gets its user ID loaded with a positive vote into the first project.
    for i in lista_unica:
        if i not in lista_votos_primario:
            Vote.get_or_create(project_id=proyecto_primario_query.id, pycampista_id=i,interest=1)

    # Queries for project owner ID and project ID matching the first and second project query
    project_owner_id_primario = ProjectOwner.select().where(ProjectOwner.project_id==proyecto_primario_query)
    project_owner_id_secundario = ProjectOwner.select().where(ProjectOwner.project_id==proyecto_secundario_query)

    # Creates list with user IDs from owners, combines them and creates a list with non repeating items
    lista_owner_primario = [proyecto.owner_id for proyecto in project_owner_id_primario]
    lista_owner_secundario = [proyecto.owner_id for proyecto in project_owner_id_secundario]

    lista_unica_owner = lista_owner_primario.copy()
    lista_unica_owner.extend(lista_owner_secundario)
    lista_unica_owner = set(lista_unica_owner)

    # Iterates through the unique list and any owner that is not present in the first project, gets its user ID loaded as an owner of the first project.    
    for i in lista_unica_owner:
        if i not in lista_owner_primario:
            ProjectOwner.get_or_create(project_id=proyecto_primario_query.id, owner_id=i)

    # Combines both names into the first project name
    nombre_primario=proyecto_primario_query.name
    nombre_secundario=proyecto_secundario_query.name
    nuevo_nombre_proyecto=nombre_primario + " / " + nombre_secundario
    proyecto_primario_query.name = nuevo_nombre_proyecto
    proyecto_primario_query.save()

    # Deletes second project data and allows the dev to insert Rage Against the Machine reference.
    killing_in_the_name_of = Project.delete().where(Project.id==proyecto_secundario_query.id)
    bulls_on_parade = Vote.delete().where(Vote.project_id==proyecto_secundario_query.id)
    calm_like_a_bomb = ProjectOwner.delete().where(ProjectOwner.project_id==proyecto_secundario_query.id)

    killing_in_the_name_of.execute()
    bulls_on_parade.execute()
    calm_like_a_bomb.execute()

    bot.send_message(
        chat_id=update.message.chat_id,
        text= "Los proyectos han sido combinados."
    )




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
        text="Has cancelado la carga del proyecto"
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
    bot.send_message(
        chat_id = update.message.chat_id,
        text = "------------------------------------------------------------------------------"

    )
    users_status[username] = UserStatus.OWNEO

def owneo(bot, update):
    '''Dialog to set project responsable'''
    username = update.message.from_user.username
    text = update.message.text
    chat_id = update.message.chat_id

    lista_proyectos = [p.name for p in Project.select()]
    dic_proyectos = dict(enumerate(lista_proyectos))
    # proyecto_usado = dic_proyectos.values(text|)

    project_name =dic_proyectos[int(text)]
    new_project = Project.get(Project.name == project_name)
    
    user = Pycampista.get_or_create(username=username, chat_id=chat_id)[0]
    project_owner = ProjectOwner.get_or_create(project=new_project, owner=user)

    
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Perfecto. Chauchi"
    )

def become_wizard(bot , update):

    username = update.message.from_user.username
    chat_id = update.message.chat_id
    Wizard.get_or_create(username=username, chat_id=chat_id, current=True)[0]
    
    bot.send_message(
        chat_id = update.message.chat_id,
        text="Felicidades! Eres el Magx de turno" 
    )

def summon_wizard(bot , update):
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    wizard = Wizard.get(Wizard.current == True)
    bot.send_message(
        chat_id = wizard.chat_id,
        text="PING PING PING MAGX! @{} te necesesita!".format(username)
    )
    




# asociate functions with user status
status_reference = {
    UserStatus.NAMING_PROJECT: naming_project,
    UserStatus.ASSIGNING_PROJECT_TOPIC: project_topic,
    UserStatus.ASSIGNING_PROJECT_LEVEL: project_level,
    UserStatus.OWNEO: owneo,
}


def start_voting(bot, update):
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
    username = update.message.from_user.username


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

def end_voting(bot, update):
    if update.message.from_user.username in autorizados:
        with open('data.json', 'w') as f:
            json.dump(DATA, f, indent=2)
        update.message.reply_text("Autorizado")
        update.message.reply_text("Información Cargada, votación cerrada")
        vote_auth = False
    else:
        update.message.reply_text("No estas Autorizadx para hacer esta ación")


def start_project_load(bot, update):
    """Allow people to upload projects"""
    global project_auth
    if not project_auth:
        if update.message.from_user.username in autorizados:
            update.message.reply_text("Autorizado")
            update.message.reply_text("Carga de proyectos Abierta")
            project_auth = True
        else:
            update.message.reply_text("No estas Autorizadx para hacer esta acción")
    else:
        update.message.reply_text("La carga de proyectos ya estaba abierta")


def end_project_load(bot, update):
    """Prevent people for keep uploading projects"""
    if update.message.from_user.username in autorizados:
        with open('data.json', 'w') as f:
            json.dump(DATA, f, indent=2)
        update.message.reply_text("Autorizado")
        update.message.reply_text("Información Cargada, carga de proyectos cerrada")
        project_auth = False
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

merge_project_handler = ConversationHandler(
       entry_points=[CommandHandler('merge', merge)],
       states={
           PRIMER_PROYECTO: [MessageHandler(Filters.text, primer_proyecto)],
           SEGUNDO_PROYECTO : [MessageHandler(Filters.text, segundo_proyecto)],
       },
       fallbacks=[CommandHandler('cancel', cancel)]
   )

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