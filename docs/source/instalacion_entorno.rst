Instalación del entorno de desarrollo
=====================================

Para poder colaborar con este desarrollo vas a necesitar 4 cosas:

- Obtener el token de telegram
- Setear las variables de entorno
- Instalar las dependencias
- Ejecutar el bot

Obtención del token de telegram
-------------------------------

Hace click en `este link <https://telegram.me/BotFather>`_ para hablar con **BotFather** y seguí los pasos:

- ``/start``
- ``/newbot``
- Dale un nombre
- Dale un username
- Copia el token de acceso

Variables de entorno
--------------------
=====================    =======    =========    =======
Variable                 Ejemplo    Requerida    Default
=====================    =======    =========    =======
TOKEN                    {TOKEN}       True
PYCAMP_BOT_MASTER_KEY     {KEY}        True
=====================    =======    =========    =======

El ``PYCAMP_BOT_MASTER_KEY`` es una clave que tenes que inventar para poder ser admin con el bot.

Instalación de dependencias
---------------------------

.. code-block:: bash

    python setup.py install

Ejecutar el bot
---------------

Para correr el bot ejecutá:

.. code-block:: bash

    TOKEN='TOKEN_PERSONAL' PYCAMP_BOT_MASTER_KEY='KEY' python bin/run_bot.py

Y listo! Tu bot está corriendo en tu máquina, esperando que alguien le escriba por telegram.
Para probarlo buscalo en telegram y mandale el comando `/start`

Ejecutar en un entorno dockerizado
__________________________________

Para ejecutar el bot primero contruya la imagen:

.. code-block:: bash

    docker build -t pycamp_bot:latest .

Ahora inicie el contenedor:

.. code-block:: bash

    docker run -e "TOKEN=TOKEN_PERSONAL" -e "PYCAMP_BOT_MASTER_KEY=KEY" -v ./:/pycamp/telegram_bot --name pycamp_telegram_bot pycamp_bot
