import logging
import json
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from enum import Enum

import token_secure


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


class UserStatus(Enum):
    NAMING_PROJECT = 1
    ASSIGNING_PROJECT_TOPIC = 2
    ASSIGNING_PROJECT_LEVEL = 3




# command /start give user a message
def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Hola ' + update.message.from_user.first_name + '! Bienvenidx')


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def text_input(bot, update):
    '''This function handle text send by user'''
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


def cargar_proyectos(bot, update):
    '''Command to start cargar_proyectos dialog'''
    username = update.message.from_user.username

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Usuario: " + username
    )

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Ingresá el Nombre del Proyecto a proponer",
    )
    users_status[username] = UserStatus.NAMING_PROJECT


def naming_project(bot, update):
    '''Dialog to set project name'''
    username = update.message.from_user.username
    text = update.message.text

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
    users_status[username] = UserStatus.ASSIGNING_PROJECT_LEVEL


def project_level(bot, update):
    '''Dialog to set project level'''
    username = update.message.from_user.username
    text = update.message.text

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
    users_status[username] = UserStatus.ASSIGNING_PROJECT_TOPIC


def project_topic(bot, update):
    '''Dialog to set project topic'''
    username = update.message.from_user.username
    text = update.message.text

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Excelente {}! La temática de tu proyecto es {}".format(username, text)
    )

    users_status.pop(username, None)


# asociate functions with user status
status_reference = {
    UserStatus.NAMING_PROJECT: naming_project,
    UserStatus.ASSIGNING_PROJECT_TOPIC: project_topic,
    UserStatus.ASSIGNING_PROJECT_LEVEL: project_level,
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
        for project_name, project in DATA['projects'].items():
            keyboard = [[InlineKeyboardButton("Si!" , callback_data="si"),
                        InlineKeyboardButton("Nop", callback_data="no")]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            update.message.reply_text(
                text= project_name,
                reply_markup=reply_markup
            )
    else:
        update.message.reply_text("Votación Cerrada")



def bardo(bot, update):
    """Ninguna de uds hizo un Docstring para sus funciones y eso esta muy mal.
        Marduk esta decepcionado.
        Marduk usa este Docstring para desquitarse."""
    def checkYesNo(question):
        bot.send_message(chat_id=update.message.chat_id, text=question)
        resp = str(update.message.text).lower
        while resp != "si" and resp != "no":
            update.message.reply_text("Por favor responde con 'Si' o 'No'  ")
            update.message.reply_text(question)
            resp = str(update.message.text).lower
        return resp

    update.message.reply_text("Marduk tiene un pequeño juego. Si ganás, te doy un meme")
    respuesta = checkYesNo("¿Querés jugar?")
    if respuesta == "si":
        update.message.reply_text('Elegí un número del 1 al 5')
        ejercicio = str(update.message.text)
        while ejercicio not in range(1, 6):
            update.message.reply_text('Respuesta no valida. Elegí un numero del 1 al 5')
            ejercicio = str(update.message.text)
        if ejercicio == '1':
            bot.send_photo(update.message.chat_id, "https://github.com/PyAr/votcamp/blob/master/img/ej%201.jpg", "Resolve este limite!")
            solucion = str(update.message.text)
            if solucion == '0':
                update.message.reply_text('Excelente! Aca tenes tu premio! Hay 4 otros problemas que resolver y 4 otros memes que ganar! Acerca tu resolucion a Marduk si tenes dudas!')
                bot.send_photo(update.message.chat_id, "https://github.com/PyAr/votcamp/blob/master/img/meme%201.jpg")
            if solucion != '0':
                update.message.reply_text('Mal! Segui participando y si seguis sin poder resolverlo, pedile ayuda a Marduk!')
                bot.send_photo(update.message.chat_id, "https://github.com/PyAr/votcamp/blob/master/img/no%20mi%20ciela.jpg")
        if ejercicio == '2':
            bot.send_photo(update.message.chat_id, "https://github.com/PyAr/votcamp/blob/master/img/ej%202.jpg", "Resolve este limite!")
            solucion = str(update.message.text)
            if solucion == '1/8':
                update.message.reply_text('Excelente! Aca tenes tu premio! Hay 4 otros problemas que resolver y 4 otros memes que ganar! Acerca tu resolucion a Marduk si tenes dudas!')
                bot.send_photo(update.message.chat_id, "https://github.com/PyAr/votcamp/blob/master/img/meme%202.jpg")
            if solucion != '1/8':
                update.message.reply_text('Mal! Segui participando y si seguis sin poder resolverlo, pedile ayuda a Marduk!')
                bot.send_photo(update.message.chat_id, "https://github.com/PyAr/votcamp/blob/master/img/no%20mi%20ciela.jpg")
        if ejercicio == '3':
            bot.send_photo(update.message.chat_id, "https://github.com/PyAr/votcamp/blob/master/img/ej%203.jpg", "Halla la derivada en el punto!")
            solucion = str(update.message.text)
            if solucion == '1':
                update.message.reply_text('Excelente! Aca tenes tu premio! Hay 4 otros problemas que resolver y 4 otros memes que ganar! Acerca tu resolucion a Marduk si tenes dudas!')
                bot.send_photo(update.message.chat_id, "https://github.com/PyAr/votcamp/blob/master/img/meme%203.jpg")
            if solucion != '1':
                update.message.reply_text('Mal! Segui participando y si seguis sin poder resolverlo, pedile ayuda a Marduk!')
                bot.send_photo(update.message.chat_id, "https://github.com/PyAr/votcamp/blob/master/img/no%20mi%20ciela.jpg")



def button(bot, update):
    query = update.callback_query
    print (query)
    if query.data == "si":
        project = query.message['text']
        user = query.message['chat']['username']
        result = 'Interesadx en: ' + project
        print (project,user)
        DATA['projects'][project]['votes'].append(user)
    else:
        result = 'No te interesa el proyecto'


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


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


updater.dispatcher.add_handler(CommandHandler('empezar_votacion', empezar_votacion))
updater.dispatcher.add_handler(CommandHandler('vote', vote))
updater.dispatcher.add_handler(CommandHandler('terminar_votacion', terminar_votacion))
updater.dispatcher.add_handler(CommandHandler('cargar_proyectos', cargar_proyectos))
updater.dispatcher.add_handler(CommandHandler('empezar_carga_proyectos', empezar_carga_proyectos))
updater.dispatcher.add_handler(CommandHandler('terminar_carga_proyectos', terminar_carga_proyectos))
updater.dispatcher.add_handler(CommandHandler('bardo', bardo))
updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.dispatcher.add_error_handler(error)
dispatcher.add_handler(MessageHandler(Filters.text, text_input))
