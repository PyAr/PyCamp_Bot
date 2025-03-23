# Guía ultra amigable para usar el bot del PyCamp 

Bienvenidx al PyCamp! 🎉 Si estás leyendo esto, seguramente querés aprovechar al máximo el bot de Telegram que nos ayuda a organizar todo. No te preocupes, es más fácil de lo que parece. Vamos paso a paso. 

---

## 🔍 Primeros pasos

Antes que nada, asegurate de que el bot está funcionando:

1. Hablale al bot en @PyCamp_bot.
2. Escribí `/start` la primera vez que le hablás para activarlo.
3. Dependiendo de tu rol (admin o pycampista), hay diferentes comandos que te pueden interesar.

---

## 🤖 Para lxs admins: Poné en marcha el PyCamp

Antes de empezar, necesitás configurar algunas cosas:

1. Seteá estas variables de entorno:
   - `TOKEN`: El token del bot (lo conseguís con BotFather en Telegram).
   - `PYCAMP_BOT_MASTER_KEY`: Una clave secreta para los comandos de admin.
   - `SENTRY_DATA_SOURCE_NAME`: El ID de Sentry para trackear errores.
2. Iniciá el bot con: `python bin/run_bot.py`.

Listo, ahora podemos empezar con la magia. 

### 🌟 Inicialización del PyCamp

- `/su <password>` ✨ Reclamá tus poderes de admin (reemplazá `<password>` por la clave secreta).
- `/empezar_pycamp <nombre>` 🏢 Creá el PyCamp y definí su inicio y duración.
- `/activar_pycamp <nombre>` ⚡ Activalo (si hace falta).
- `/terminar_pycamp` 🌚 Cierra oficialmente el PyCamp.

### 🤠 Organizando los proyectos

- `/empezar_carga_proyectos` ✏️ Habilitá la carga de proyectos.
- `/terminar_carga_proyectos` ❌ Cerrá la carga de proyectos.
- `/empezar_votacion_proyectos` 🗳️ Arrancá la votación.
- `/terminar_votacion_proyectos` ❌ Cerrá la votación.
- `/contar_votos` 📊 Muestra cuánta gente votó.
- `/anunciar` 📢 Notifica a les interesades sobre el inicio de una actividad (solo admins y dueñxs del proyecto).

### 🗓 Armando el cronograma

- `/cronogramear` ⏳ Creá el cronograma con los días y slots que quieras.
- `/cambiar_slot <proyecto> <slot>` ✏️ Mové un proyecto de horario.

### 🎩 Agendando lxs magxs

Los magos son personas geniales que ayudan durante el evento. Para organizarlos:

- `/agendar_magx` 🌟 Asigna un mago por hora durante el PyCamp.
- Los magos se registran con `/ser_magx`.

### 🔒 Administración del PyCamp

- `/admins` 👤 Lista a todos los admins.
- `/agregar_pycamp <nombre>` ✅ Agrega un nuevo PyCamp.
- `/degradar <usuario>` ❌ Le saca los permisos de admin a un usuario.

---

## 🥳 Para lxs Pycampistas: Cómo usar el bot

Si no sos admin, igual podés usar el bot para participar activamente. 

### 💪 Participando en el PyCamp
- `/voy_al_pycamp <nombre>` 🌟 Avisá que vas al PyCamp.
- `/pycampistas` 👥 Mirá info sobre los pycampistas.
- `/pycamps` 📓 Lista todos los PyCamps.

### 💡 Para los proyectos:
- `/cargar_proyecto` 📑 Cargá tu proyecto (si la carga está habilitada).
- `/proyectos` 📝 Muestra todos los proyectos y sus responsables.
- `/mis_proyectos` 📰 Muestra tus proyectos cargados.
- `/participantes <proyecto>` 👥 Muestra la gente interesada en un proyecto.
- `/borrar_proyecto` ⛔️ Borra un proyecto.
- `/votar` 🗳️ Votá por los proyectos que te interesen.
- `/cronograma` 🗓 Mirá el cronograma de actividades.
- `/rifar` 🎯 Elegí un pycampista al azar.

### 🤠 Para la magia del evento:
- `/ser_magx` 🎩 Registrate como mago.
- `/ver_magx` 🦄 Mirá quién es mago.
- `/evocar_magx` ✨ Llamá al mago de turno si necesitás ayuda.
- `/ver_agenda_magx` 🔍 Consultá la agenda de magos.

---

### 🔧 Otros comandos 

- `/ayuda` ❓ Muestra esta ayuda.
- `/mostrar_version` 🔄 Muestra la versión del bot que está corriendo.

---

Eso es todo! Si tenés dudas, preguntale a alguien del equipo o probá los comandos sin miedo. 😉

¡Que tengas un PyCamp genial! 🎉

