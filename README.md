# Este es el bot del Pycamp!

Si queres contribuir en este proyecto lo primero que vas a necesitar es crearte un bot para hacer
las pruebas.

Esto lo podes hacer hablandole a @BotFather que es el "Bot padre de todos los bots" de telegram.
Él te a a guiar para que puedas hacer tu propio bot.


Una vez creado el bot, deberías tener un TOKEN (BotFather te lo da en el mismo proceso de
creación). Vas a necesitar crear un archivo llamado `token_secure.py` en la raíz de este repo.
Dentro del mismo colocá este contenido:
```
TOKEN = '<YOUR_BOT_TOKEN>'
```
Para correr el bot ejecutá (desde el virtualenv):
```
python bot.py
```
Y listo! Tu bot está corriendo en tu máquina, esperando que alguien le escriba por telegram.
Podés probarlo mandandole un `/start`
