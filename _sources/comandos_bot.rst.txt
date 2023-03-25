Comandos del Bot del Pycamp
===========================

Comandos básicos
----------------
- ``/start``: Sirve para comenzar la interacción con el bot

Comandos de Administrador
-------------------------

- ``/su <password>``: Reclama permisos de admin, la contraseña es la usada en la variable de entorno ``PYCAMP_BOT_MASTER_KEY``.
- ``/agregar_pycamp <pycamp_name>``: Crea el PyCamp en la DB.
- ``/activar_pycamp <pycamp_name>``: Activa un Pycamp.
- ``/empezar_pycamp``: Setea la fecha de inicio del pycamp activo.
- ``/empezar_carga_proyectos``: Habilita la carga de los proyectos. En este punto los pycampistas pueden cargar sus proyectos, enviandole al bot el comando ``/cargar_proyecto``.
- ``/terminar_carga_proyectos``: Termina carga proyectos.
- ``/empezar_votacion``: Activa la votacion (a partir de ahora los pycampistas pueden votar con ``/votar``).
- ``/terminar_votacion``: Termina la votacion.
- ``/cronogramear``: Pregunta los dias y slot por día para poder crear el cronograma.
- ``/cambiar_slot``: Toma un nombre de proyecto y un slot; y te cambia ese proyecto a ese slot.

Compandos Pycampista
--------------------

- ``/cargar_proyecto``: Carga un proyecto (si está habilitada la carga).
- ``/votar``: Envia opciones para votar (si está habilitada la votacion).
- ``/ver_cronograma``: Te muestra el cronograma!.
