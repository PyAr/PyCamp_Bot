
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

