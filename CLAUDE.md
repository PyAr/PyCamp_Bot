# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Descripción del Proyecto

PyCamp_Bot es un bot de Telegram diseñado para organizar y gestionar PyCamps (eventos de Python Argentina). Maneja la carga de proyectos, votación, cronogramas, y asignación de magos (ayudantes) durante el evento.

## Configuración de Desarrollo

### Variables de entorno requeridas
- `TOKEN`: Token del bot de Telegram (obtener de @BotFather)
- `PYCAMP_BOT_MASTER_KEY`: Password para comandos de admin
- `SENTRY_DATA_SOURCE_NAME`: (Opcional) ID de Sentry para monitoreo

### Instalación Local
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e '.[dev]'
```

### Ejecutar el bot

#### Opción 1: Variables inline (rápido para pruebas)
```bash
TOKEN='tu_token' PYCAMP_BOT_MASTER_KEY='tu_clave' python bin/run_bot.py
```

#### Opción 2: Con archivo .env (recomendado)
1. Crear archivo de configuración:
   ```bash
   cp .env.example .env
   ```
2. Editar `.env` con tus valores
3. Ejecutar:
   ```bash
   python bin/run_bot.py  # Lee automáticamente .env
   ```

#### Opción 3: Con Docker (producción/testing aislado)
```bash
make           # Construye imagen (si no existe) y ejecuta el bot
make build     # Solo construir la imagen
make run       # Solo ejecutar (requiere .env)
```

El Dockerfile usa `python:3.10-slim` para balance óptimo entre tamaño (~150MB) y compatibilidad.

### Testing

**Los comandos del proyecto (bot, tests) se ejecutan dentro del contenedor** cuando se usa el Makefile.

#### Con Docker (recomendado)
```bash
make test     # Ejecuta pytest en el contenedor
make test-cov # pytest con reporte de cobertura (--cov=pycamp_bot)
```

#### Local (con venv activo)
```bash
pytest                     # Todos los tests
pytest test/test_wizard.py  # Test específico
pytest -v                   # Modo verbose
```

### Linting
```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

## Arquitectura del Código

### Estructura de Comandos
Los comandos del bot están organizados modularmente en `src/pycamp_bot/commands/`:
- `auth.py`: Autenticación y manejo de admins (`/su`, `/admins`, `/degradar`)
- `manage_pycamp.py`: Gestión de PyCamps (`/empezar_pycamp`, `/activar_pycamp`, `/terminar_pycamp`)
- `projects.py`: CRUD de proyectos (`/cargar_proyecto`, `/proyectos`, `/borrar_proyecto`)
- `voting.py`: Sistema de votación (`/votar`, `/empezar_votacion_proyectos`, `/terminar_votacion_proyectos`)
- `schedule.py`: Generación de cronogramas (`/cronogramear`, `/cambiar_slot`)
- `wizard.py`: Sistema de magos (`/ser_magx`, `/agendar_magx`, `/evocar_magx`)
- `announcements.py`: Anuncios (`/anunciar`)
- `raffle.py`: Sorteo de pycampistas (`/rifar`)
- `base.py`: Comandos básicos (`/start`, `/ayuda`)

Cada módulo de comandos tiene su función `set_handlers(application)` que registra los CommandHandler en el bot.

### Modelos de Base de Datos (Peewee ORM)
En `src/pycamp_bot/models.py`:
- `Pycamp`: Representa un evento PyCamp
- `Pycampista`: Usuario del bot con info de llegada/salida, wizard status, admin status
- `PycampistaAtPycamp`: RelaciónMany-to-Many entre Pycampistas y Pycamps
- `WizardAtPycamp`: Asignación de magos en slots de tiempo específicos
- `Project`: Proyectos presentados con nombre, dificultad, tema, slot, owner
- `Slot`: Slots de tiempo para presentaciones de proyectos
- `Vote`: Votos de pycampistas sobre proyectos (con campo `interest`)

La base de datos es SQLite (`pycamp_projects.db`).

### Sistema de Scheduling
El algoritmo de scheduling (`src/pycamp_bot/scheduler/schedule_calculator.py`) usa **random restart hill climbing** para optimizar el cronograma basándose en múltiples factores:
- Colisiones de responsables y participantes
- Disponibilidad de responsables
- Proyectos más votados
- Distribución de población en slots
- Balance de niveles de dificultad y temas

### Flujo de Trabajo Típico de un PyCamp
1. Admin hace `/su <password>` para obtener permisos
2. Admin ejecuta `/empezar_pycamp <nombre>` para crear el PyCamp
3. Admin ejecuta `/empezar_carga_proyectos`
4. Pycampistas cargan proyectos con `/cargar_proyecto`
5. Admin ejecuta `/terminar_carga_proyectos` y `/empezar_votacion_proyectos`
6. Pycampistas votan con `/votar`
7. Admin ejecuta `/terminar_votacion_proyectos` y `/cronogramear` para generar el schedule
8. Pycampistas se registran como magos con `/ser_magx`
9. Admin ejecuta `/agendar_magx` para asignar turnos de magos
10. Durante el evento: `/evocar_magx` para llamar al mago de turno

### Sistema de Magos (Wizards)
Los magos son pycampistas que ayudan durante el evento. El bot:
- Permite registro con `/ser_magx`
- Asigna automáticamente turnos de 9-13 y 14-19 con `/agendar_magx`
- Identifica al mago de turno actual usando timezone de Córdoba, Argentina
- Usa `Pycampista.is_busy()` para evitar conflictos con presentaciones de proyectos

## Convenciones de Código

- Mensajes de commit en español: formato `{tipo}({alcance}): {Resumen}\n\nDetalles.`
- Sin co-author en commits
- Logging con el módulo `pycamp_bot.logger`
- Comandos usan async/await (python-telegram-bot v21)
- Tests con pytest y freezegun para mocking de fechas

## Base de Datos

La DB se inicializa automáticamente al ejecutar `bin/run_bot.py` mediante `models_db_connection()`. El archivo `pycamp_projects.db` persiste entre ejecuciones.

Para migraciones, ver directorio `migrations/` con scripts de migración manual.

## Docker y Makefile

### Makefile
El proyecto incluye un Makefile para simplificar el uso de Docker:
- `make` o `make all`: Construye la imagen y ejecuta el contenedor
- `make build`: Solo construye la imagen Docker
- `make run`: Solo ejecuta el contenedor (requiere imagen existente)
- `make test`: Ejecuta pytest dentro del contenedor

Todos los comandos usan el archivo `.env` para las variables de entorno.

### Dockerfile
- Usa `python:3.10-slim` como base (~150MB)
- Instala el paquete en modo editable
- CMD por defecto: `python bin/run_bot.py`
- El archivo `.env` debe existir para `make run` y `make test`

## Notas Importantes

- El bot requiere que usuarios tengan username de Telegram configurado
- Zona horaria por defecto: `America/Argentina/Cordoba`
- Duración de slots por defecto: 60 minutos (`DEFAULT_SLOT_PERIOD`)
- Un solo PyCamp puede estar "activo" a la vez
- Los votos previenen duplicados usando el campo `_project_pycampista_id`
- El archivo `.env` está en `.gitignore` (nunca commitear credenciales)
- `.env.example` contiene el template de configuración
