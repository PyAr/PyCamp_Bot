# Este es el bot del Pycamp

## Documentación del módulo

Puede encontrar una documentación mas detallada para programadores en [https://pyar.github.io/PyCamp_Bot](https://pyar.github.io/PyCamp_Bot)

## Variables de entorno

* TOKEN: Token del bot generado con BotFather.
* PYCAMP_BOT_MASTER_KEY: Password para agregar nuevos admins.
* SENTRY_DATA_SOURCE_NAME: ID de proyecto de Sentry para habilitar el monitoreo.

## Development

Si queres contribuir en este proyecto lo primero que vas a necesitar es crearte un bot para hacer
las pruebas.

Esto lo podes hacer hablandole a @BotFather que es el "Bot padre de todos los bots" de telegram.
Él te a a guiar para que puedas hacer tu propio bot.

Una vez creado el bot, deberías tener un TOKEN\_PERSONAL (BotFather te lo da en el mismo proceso de
creación).

Despues instala el paquete en modo desarrollo en un virtualenv

~~~bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -e '.[dev]'
~~~

y estas listo para trabajar.

`pip install freezegun` para correr los tests.

## Testeo

Para correr el bot ejecutá (desde el virtualenv):

~~~bash
TOKEN='TOKEN_PERSONAL' PYCAMP_BOT_MASTER_KEY='KEY' python bin/run_bot.py
~~~

Y listo! Tu bot está corriendo en tu máquina, esperando que alguien le escriba por telegram.
Podés probarlo mandandole un `/start`

## ¿Cómo usar el bot en un nuevo pycamp?

Primero es necesario setear las siguientes variables de entorno:

* `TOKEN`: token del bot que se usará durante el pycamp (gestionar desde telegram con BotFather)
* `PYCAMP_BOT_MASTER_KEY`: con alguna password secreta que se va a usar para acceder a comandos de superuser
* `SENTRY_DATA_SOURCE_NAME`: ID del proyecto de Sentry "telegrambot" de la cuenta de PyAr

Una vez creadas las variables de entorno, correr el bot con el comando `python bin/run_bot.py`

En este momento ya se puede hablar con el bot. ¿Qué le digo?

* `/start` para chequear que esté andando bien

### Flujo admin

* `/su <password>` para reclamar permisos de admin, reemplazando `<password>` por la contraseña que hayamos
elegido en la envvar `PYCAMP_BOT_MASTER_KEY`
* `/empezar_pycamp <pycamp_name>` inicia el flujo de creación de un pycamp. Lo carga en la db, pide fecha de inicio y duración. Lo deja activo.
* `/activar_pycamp <pycamp_name>` activa un pycamp
* `/empezar_carga_proyectos` habilita la carga de los proyectos. En este punto los pycampistas pueden cargar sus proyectos,
enviandole al bot el comando `/cargar_proyecto`
* `/terminar_carga_proyectos` termina carga proyectos
* `/empezar_votacion_proyectos`  activa la votacion (a partir de ahora los pycampistas pueden votar con `/votar`)
* `/terminar_votacion_proyectos` termina la votacion

Para generar el schedule:

* `/cronogramear` te va a preguntar cuantos dias queres cronogramear y cuantos slots por dia tenes y hacer el cronograma.
* `/cambiar_slot` toma un nombre de proyecto y un slot; y te cambia ese proyecto a ese slot.

Para agendar los magos:

1. Todos los candidatos tienen que haberse registrado con `/ser_magx`
2. Tiene que estar creado el schedule de presentaciones de proyectos (`/cronogramear`)

* `/agendar_magx` Asigna un mago por hora durante todo el PyCamp.
    * De 9 a 13 y de 14 a 19.
    * El primer día arranca después del almuerzo (14hs).
    * El último día termina al almuerzo (13hs).

### Flujo pycampista

* `/cargar_proyecto` carga un proyecto (si está habilitada la carga)
* `/votar` envia opciones para votar (si está habilitada la votacion)
* `/ver_cronograma` te muestra el cronograma!
* `/ser_magx` te registra como mago.
* `/ver_magx` Lista los magos registrados.
* `/evocar_magx` llama al mago de turno para pedirle ayuda.
* `/ver_agenda_magx completa` te muestra la agenda de magos del PyCamp. El parámetro `completa` es opcional, si se omite solo muestra los turnos pendientes.
