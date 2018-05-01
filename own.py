from bot import bot, update

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
