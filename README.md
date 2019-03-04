# Este es el bot del Pycamp!

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

### Usando `pipenv`

> Si no tenés `pipenv` podés instalarlo consultando la [Documentación Oficial](https://pipenv.readthedocs.io/en/latest/)

Copiá el `.env.dist` en un `.env` y poné ahí la `TOKEN` que te dió el [@BotFather](https:/t.me/botfather).
Luego creá el entorno virtual.
Finalmente ejecutá el bot.

```bash
cp .env.dist .env
pipenv install
pipenv run python bin/run_bot.py
```

## Testeo

Para correr el bot ejecutá (desde el virtualenv):
```
TOKEN='TOKEN_PERSONAL' python bint/run_bot.py
```

Y listo! Tu bot está corriendo en tu máquina, esperando que alguien le escriba por telegram.
Podés probarlo mandandole un `/start`
