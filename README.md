# Este es el bot del Pycamp!

## Development

Si queres contribuir en este proyecto lo primero que vas a necesitar es crearte un bot para hacer
las pruebas.

Esto lo podes hacer hablandole a [@BotFather](https:/t.me/botfather) que es el *Bot padre de todos los bots* de Telegram.
Él te a va guiar para que puedas hacer tu propio bot.

Una vez creado el bot, deberías tener un TOKEN\_PERSONAL (BotFather te lo da en el mismo proceso de
creación). 

Despues instalá el paquete en modo desarrollo en un virtualenv

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -e .
```

y estas listo para trabajar.

Para correr el bot ejecutá (dentro el virtualenv):

```
TOKEN='TOKEN_PERSONAL' python bin/run_bot.py
```

### Usando `pipenv`

> Si no tenés `pipenv` podés instalarlo consultando la [Documentación Oficial](https://pipenv.readthedocs.io/en/latest/)

Copiá el `.env.dist` en un `.env` y poné ahí la `TOKEN` que te dió el [@BotFather](https:/t.me/botfather).
Luego creá el entorno virtual.
Finalmente ejecutá el bot.

```bash
cp .env.dist .env                   # Copiá el .env y modificá tu TOKEN
pipenv install                      # Creá el entorno virtual
pipenv run python bin/run_bot.py    # Ejecutá tu bot
```

## Usando el Bot

Listo! Tu bot está corriendo en tu máquina, esperando que alguien le escriba por Telegram.

Ahora sólo te resta crear un usuario **admin**. Para eso iniciá un chat con él y mandandale un `/start`.
Esto sirve para que el Bot te registre y sepa quién sos y se establezca un *chat_id*.
Ejecutá `bin/create_admin.py`, te va a pedir tu nombre de usuario y con eso el Bot te va a reconocer como
administrador.

```bash
$ python bin/create_admin.py
Ingresá tu Alias de Telegram para ser admin: lecovi                                                                          
El usuario lecovi fue habilitado como admin! 
```

> con `pipenv` el comando a ejecutar es: `pipenv run python bin/create_admin.py`
