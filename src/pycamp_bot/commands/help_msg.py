from pycamp_bot.commands.auth import is_admin

user_commands_help = '''
Comandos de usuario:
/voy\\_al\\_pycamp \\(pycamp name\\): avisá que vas al pycamp\\! si no especificas un\
    pycamp por default es el que esta activo\\.
/pycamps: lista todos los pycamps\\.
/cargar\\_proyecto: empieza la conversacion de carga de proyecto\\.
/proyectos: te muestra la informacion de todos los proyectos y sus responsables\\.
/mis\\_proyectos: te muestra día y horario de los proyectos que votaste\\.
/agregar\\_repositorio: para cargar o modificar la URL del repositorio de un proyecto\\.
/agregar\\_grupo: para cargar o modificar la URL del grupo de Telegram de un proyecto\\.
/ser\\_magx: te agrega la lista de Magx\\.
/evocar\\_magx: pingea a la/el Magx de turno, informando que necesitas su\
    ayuda\\. Con un gran poder, viene una gran responsabilidad\\.
/elegir\\_proyectos: te muestra los proyectos presentados para que digas cuales te gustan\\.
/cronograma: te muestra el cronograma del PyCamp\\.
/anunciar: te pide el nombre de un proyecto y pingea por privado a les \
    interesades avisando que esta por empezar \\(solo para admins u owners del proyecto\\)\\.
/su \\(passwrd\\): convierte al usuario en admin\\. Si sabe el password :P
/mostrar\\_version: te muestra qué versión del bot está corriendo y otros detalles
/admins: lista a todos los admins\\.
/ayuda: esta ayuda\\.
'''

HELP_MESSAGE = '''
Este bot facilita la carga, administración y procesamiento de magues, \
proyectos y votos durante el PyCamp

El proceso se divide en 3 etapas:

*Primera etapa*: Iniciar el PyCamp. Algún admin del Bot 

*Primera etapa*: Lxs responsables de los proyectos cargan sus proyectos \
mediante el comando */cargar\\_proyecto*\\. Solo un responsable carga el \
proyecto, y luego si hay otrxs responsables adicionales, pueden \
agregarse con el comando */ownear*\\.

*Segunda etapa*: Mediante el comando */elegir\\_proyectos* todxs lxs participantes \
seleccionan los proyectos que se expongan\\. Esto se puede hacer a medida que \
se expone, o al haber finalizado todas las exposiciones\\. Si no se está \
segurx de un proyecto, conviene no seleccionar nada, ya que luego podés \
volver a ejecutar el comando y darle que si aquellas cosas que no tocaste\\. NO \
SE PUEDE CAMBIAR TU RESPUESTA UNA VEZ HECHO\\.

*Tercera etapa*: Lxs admins mergean los proyectos que se haya decidido \
mergear durante las exposiciones \\(Por tematica similar, u otros \
motivos\\), y luego se procesan los datos para obtener el cronograma \
final\\.
''' + user_commands_help

HELP_MESSAGE_ADMIN = '''
Be AWARE, you have sudo\\.\\.\\.

Pycamp:
/activar\\_pycamp \\(pycamp\\): Setea un pycamp como activo \\(si ya hay uno activo lo \
desactiva\\)\\.

/empezar\\_carga\\_proyectos: Habilita la carga de proyectos en el pycamp activo\\.
/terminar\\_carga\\_proyectos: Deshabilita la carga de proyectos en el pycamp activo\\.
/empezar\\_seleccion\\_proyectos: Habilita la seleccion sobre los proyectos del pycamp activo\\.
/terminar\\_seleccion\\_proyectos: Deshabilita la seleccion sobre los proyectos del pycamp activo\\.
/empezar\\_pycamp: Setea el tiempo de inicio del pycamp activo\\. \
Por default usa datetime\\.now\\(\\)
/terminar\\_pycamp: Setea el timepo de fin del pycamp activo\\. \
Por default usa datetime\\.now\\(\\)
/cronogramear: Te pregunta cuantos dias y que slot tiene tu pycamp \
    y genera el cronograma\\.
/cambiar\\_slot: Toma el nombre de un proyecto y el nuevo slot \
    y lo cambia en el cronograma\\.

**Gestión de magxs**

/ser\\_magx Tienen que ejecutar los candidatos, al inicio del PyCamp\\.
/agendar\\_magx Genera una agenda de magxs para todo el evento\\.
/ver\\_agenda\\_magx Para conocer la agenda magos de todo el evento\\.
/ver\\_magx Para conocer el magx actual\\.
/evocar\\_magx Para llamar al mago actual\\.

Pycampista:
/degradar \\(username\\): Le saca los permisos de admin a un usuario\\.
''' + user_commands_help


def get_help(update, context):
    if is_admin(update, context):
        return HELP_MESSAGE_ADMIN
    return HELP_MESSAGE
