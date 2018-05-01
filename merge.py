from telegram.ext import (ConversationHandler, CommandHandler, MessageHandler, Filters)
from models import Pycampista, Project, ProjectOwner, Slot, Vote, Wizard
from manage_pycamp import is_auth

merge_projects = []
PRIMER_PROYECTO, SEGUNDO_PROYECTO = range(2)

def merge(bot, update):
    if not is_auth(bot, update.message.from_user.username):
        bot.send_message(
            chat_id = update.message.chat_id,
            text= 'No estás autorizadx para llevar a cabo esta acción. Este comando solo puede ser utilizado por Admins'
        )
        return CommandHandler.END

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

def cancel(bot, update):
    bot.send_message(
    chat_id=update.message.chat_id,
    text="Has cancelado la carga del proyecto"
    )
    return ConversationHandler.END


merge_project_handler = ConversationHandler(
       entry_points=[CommandHandler('merge', merge)],
       states={
           PRIMER_PROYECTO: [MessageHandler(Filters.text, primer_proyecto)],
           SEGUNDO_PROYECTO : [MessageHandler(Filters.text, segundo_proyecto)],
       },
       fallbacks=[CommandHandler('cancel', cancel)]
   )
