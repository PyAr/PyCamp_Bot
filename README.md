# Este es el bot del Pycamp!

## Variables de entorno

* TOKEN: Token del bot generado con BotFather.
* PYCAMP_BOT_MASTER_KEY: Password para agregar nuevos admins.

## Development

Si queres contribuir en este proyecto lo primero que vas a necesitar es crearte un bot para hacer
las pruebas.

Esto lo podes hacer hablandole a @BotFather que es el "Bot padre de todos los bots" de telegram.
Él te a a guiar para que puedas hacer tu propio bot.

Una vez creado el bot, deberías tener un TOKEN\_PERSONAL (BotFather te lo da en el mismo proceso de
creación). 

Despues instala el paquete en modo desarrollo en un virtualenv

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -e .
```

y estas listo para trabajar.

## Testeo

Para correr el bot ejecutá (desde el virtualenv):
```
TOKEN='TOKEN_PERSONAL' python bin/run_bot.py
```

Y listo! Tu bot está corriendo en tu máquina, esperando que alguien le escriba por telegram.
Podés probarlo mandandole un `/start`
