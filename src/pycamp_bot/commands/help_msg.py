from pycamp_bot.commands.auth import is_admin


HELP_MESSAGE = '''
Este bot facilita la carga, administración y procesamiento de\
proyectos y votos durante el PyCamp

El proceso se divide en 3 etapas:

*Primera etapa*: Lxs responsables de los proyectos cargan sus proyectos\
mediante el comando /cargar_proyecto. Solo un responsable carga el\
proyecto, y luego si hay otrxs responsables adicionales, pueden\
agregarse con el comando /ownear.

*Segunda etapa*: Mediante el comando /votar todxs lxs participantes\
votan los proyectos que se expongan. Esto se puede hacer a medida que\
se expone, o al haber finalizado todas las exposiciones. Si no se está\
segurx de un proyecto, conviene no votar nada, ya que luego podés\
volver a ejecutar el comando y votar aquellas cosas que no votaste. NO\
SE PUEDE CAMBIAR TU VOTO UNA VEZ HECHO.

*Tercera etapa*: Lxs admins mergean los proyectos que se haya decidido\
mergear durante las exposiciones (Por tematica similar, u otros\
motivos), y luego se procesan los datos para obtener el cronograma\
final.

Comandos adicionales:
/proyectos: te muestra la informacion de todos los proyectos y sus responsables.
/ser_magx: te transforma en el/la Magx de turno.
/evocar_magx: pingea a la/el Magx de turno, informando que necesitas su\
ayuda. Con un gran poder, viene una gran responsabilidad.
/su (passwrd): convierte al usuario en admin. Si sabe el password :P
/amins: lista a todos los admins.
/ayuda: esta ayuda.'''

HELP_MESSAGE_ADMIN = '''
Be AWARE, you have sudo...

/start_project_load: Habilita la carga de proyectos.
/end_project_load: Deshabilita la carga de proyectos.
/sorteo: Realiza un sorteo entre todos los participantes del pycamp\
actual.
/start_voting: Habilita la votacion sobre los proyectos.
/end_voting: Deshabilita la votacion sobre los proyectos.
/start_pycamp: Inicia un nuevo pycamp.
/end_pycamp: Termina el pycamp.
/degrdar (username): Le saca los permisos de admin a un usuario.'''


def get_help(bot, update):
    if is_admin(bot, update):
        return HELP_MESSAGE_ADMIN
    return HELP_MESSAGE
