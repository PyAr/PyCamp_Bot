# Este es el bot del Pycamp

Bot de Telegram para organizar y gestionar PyCamps: carga de proyectos, votación, cronogramas y asignación de magos.

---

## 📚 Documentación

Encontrá documentación más detallada para programadores en [https://pyar.github.io/PyCamp_Bot](https://pyar.github.io/PyCamp_Bot)

---

## 🚀 Desarrollo

### 1️⃣ Crear tu bot de prueba

Para contribuir necesitás tu propio bot de Telegram:

1. Hablale a [@BotFather](https://t.me/BotFather) en Telegram
2. Seguí las instrucciones para crear tu bot
3. Guardá el **TOKEN** que te da (lo vas a necesitar)

### 2️⃣ Instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e '.[dev]'
```

### 3️⃣ Ejecutar el bot

#### Opción 1: Variables inline (más rápido para probar)

```bash
TOKEN='TU_TOKEN_AQUI' PYCAMP_BOT_MASTER_KEY='TU_CLAVE' python bin/run_bot.py
```

#### Opción 2: Con archivo .env (recomendado)

1. Crear el archivo de configuración:
   ```bash
   cp .env.example .env
   ```

2. Editar `.env` con tus valores:
   ```
   TOKEN=tu_token_aqui
   PYCAMP_BOT_MASTER_KEY=tu_clave_secreta
   SENTRY_DATA_SOURCE_NAME=tu_sentry_dsn  # Opcional
   ```

3. Ejecutar:
   ```bash
   python bin/run_bot.py
   ```

#### Opción 3: Con Docker

```bash
make    # Construye la imagen (si no existe) y ejecuta el bot
```

**¡Listo!** Tu bot está corriendo. Probalo mandándole `/start` por Telegram.

---

## 🧪 Testing

### Opción 1: Local en tu máquina

Ejecutar todos los tests:

```bash
pytest
```

Ejecutar un test específico:

```bash
pytest test/test_wizard.py
```

Con variables de entorno inline:

```bash
TOKEN='TOKEN_TEST' PYCAMP_BOT_MASTER_KEY='KEY_TEST' pytest
```

### Opción 2: Con Docker

```bash
make test
```

---

## 🔧 Variables de entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `TOKEN` | Token del bot generado con BotFather | ✅ Sí |
| `PYCAMP_BOT_MASTER_KEY` | Password para comandos de admin | ✅ Sí |
| `SENTRY_DATA_SOURCE_NAME` | ID de proyecto de Sentry para monitoreo | ❌ No |

---

## 🎯 ¿Cómo usar el bot en un nuevo PyCamp?

### Preparación inicial

1. Configurar las variables de entorno (ver tabla arriba)
2. Ejecutar el bot: `python bin/run_bot.py`
3. Verificar que funciona enviándole `/start`

---

## 👥 Comandos del bot

### 🔐 Para Admins

#### Inicialización (al comienzo de cada PyCamp)

| Comando | Descripción |
|---------|-------------|
| `/su <password>` | Reclamar permisos de admin con la clave de `PYCAMP_BOT_MASTER_KEY` |
| `/empezar_pycamp <nombre>` | Crear el PyCamp (pide fecha de inicio y duración) |
| `/activar_pycamp <nombre>` | Activar un PyCamp específico (si hace falta) |

#### Gestión de Proyectos

| Comando | Descripción |
|---------|-------------|
| `/empezar_carga_proyectos` | Habilitar la carga de proyectos |
| `/terminar_carga_proyectos` | Cerrar la carga de proyectos |
| `/empezar_votacion_proyectos` | Activar la votación |
| `/terminar_votacion_proyectos` | Cerrar la votación |
| `/cronogramear` | Generar el cronograma (pide días y slots) |
| `/cambiar_slot <proyecto> <slot>` | Mover un proyecto de horario |

#### Gestión de Magxs

| Comando | Descripción |
|---------|-------------|
| `/agendar_magx` | Asignar magos automáticamente (9-13 y 14-19hs) |

> **Nota:** Los magos deben registrarse primero con `/ser_magx`

---

### 🙋 Para Pycampistas

#### Proyectos

| Comando | Descripción |
|---------|-------------|
| `/cargar_proyecto` | Cargar tu proyecto (si la carga está habilitada) |
| `/votar` | Votar proyectos de tu interés |
| `/ver_cronograma` | Ver el cronograma del evento |

#### Sistema de Magxs

| Comando | Descripción |
|---------|-------------|
| `/ser_magx` | Registrarte como mago |
| `/ver_magx` | Ver la lista de magos registrados |
| `/evocar_magx` | Llamar al mago de turno para pedir ayuda |
| `/ver_agenda_magx [completa]` | Ver la agenda de magos (usa `completa` para ver todos los turnos) |

---

