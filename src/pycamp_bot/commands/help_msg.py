from pycamp_bot.commands.auth import is_admin

user_commands_help = '''
Comandos de usuario:
/voy_al_pycamp (pycamp name): avisá que vas al pycamp! si no especificas un\
    pycamp por default es el que esta activo.
/pycamps: lista todos los pycamps.
/cargar_proyecto: empieza la conversacion de carga de proyecto.
/proyectos: te muestra la informacion de todos los proyectos y sus responsables.
/ser_magx: te agrega la lista de Magx.
/evocar_magx: pingea a la/el Magx de turno, informando que necesitas su\
    ayuda. Con un gran poder, viene una gran responsabilidad.
/elegir_proyectos: te muestra los proyectos presentados para que digas cuales te gustan.
/cronograma: te muestra el cronograma del PyCamp.
/anunciar: te pide el nombre de un proyecto y pingea por privado a les \
    interesades avisando que esta por empezar (solo para admins u owners del proyecto).
/su (passwrd): convierte al usuario en admin. Si sabe el password :P
/admins: lista a todos los admins.
/ayuda: esta ayuda.'''

HELP_MESSAGE = '''
Este bot facilita la carga, administración y procesamiento de\
proyectos y votos durante el PyCamp

El proceso se divide en 3 etapas:

*Primera etapa*: Lxs responsables de los proyectos cargan sus proyectos\
mediante el comando **/cargar_proyecto**. Solo un responsable carga el\
proyecto, y luego si hay otrxs responsables adicionales, pueden\
agregarse con el comando /ownear.

*Segunda etapa*: Mediante el comando **/elegir_proyectos** todxs lxs participantes\
seleccionan los proyectos que se expongan. Esto se puede hacer a medida que\
se expone, o al haber finalizado todas las exposiciones. Si no se está\
segurx de un proyecto, conviene no seleccionar nada, ya que luego podés\
volver a ejecutar el comando y darle que si aquellas cosas que no tocaste. NO\
SE PUEDE CAMBIAR TU RESPUESTA UNA VEZ HECHO.

*Tercera etapa*: Lxs admins mergean los proyectos que se haya decidido\
mergear durante las exposiciones (Por tematica similar, u otros\
motivos), y luego se procesan los datos para obtener el cronograma\
final.

''' + user_commands_help

HELP_MESSAGE_ADMIN = '''
Be AWARE, you have sudo...

Pycamp
------
/agregar_pycamp (pycamp): Agrega un pycamp.
/activar_pycamp (pycamp): Setea un pycamp como activo (si ya hay uno activo lo\
desactiva).
/empezar_carga_proyectos: Habilita la carga de proyectos en el pycamp activo.
/terminar_carga_proyectos: Deshabilita la carga de proyectos en el pycamp activo.
/empezar_seleccion_proyectos: Habilita la seleccion sobre los proyectos del pycamp activo.
/terminar_seleccion_proyectos: Deshabilita la seleccion sobre los proyectos del pycamp activo.
/empezar_pycamp: Setea el tiempo de inicio del pycamp activo.\
Por default usa datetime.now()
/terminar_pycamp: Setea el timepo de fin del pycamp activo.\
Por default usa datetime.now()
/cronogramear: Te pregunta cuantos dias y que slot tiene tu pycamp \
    y genera el cronograma.
/cambiar_slot: Toma el nombre de un proyecto y el nuevo slot \
    y lo cambia en el cronograma.

Pycampista
----------
/degradar (username): Le saca los permisos de admin a un usuario.

''' + user_commands_help


def get_help(bot, update):
    if is_admin(bot, update):
        return HELP_MESSAGE_ADMIN
    return HELP_MESSAGE
