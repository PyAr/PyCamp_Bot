# =============================================================================
# PyCamp Bot — Makefile
# =============================================================================
# Todos los comandos (bot, tests, etc.) se ejecutan dentro del contenedor.
# El código se monta como volumen para que los cambios locales se reflejen
# sin necesidad de reconstruir la imagen (rebuild).
#
# Requiere: imagen construida (make build) y archivo .env para run/test.
# =============================================================================

.PHONY: build run test test-cov all

# Ruta del proyecto en el host; se monta en el contenedor para evitar rebuild.
PROJECT_PATH := $(shell pwd)
# Ruta dentro del contenedor (debe coincidir con WORKDIR del Dockerfile).
CONTAINER_PATH := /pycamp/telegram_bot

build:
	docker build --rm -t pycamp_bot .

# Ejecuta el bot. Código montado en rw para que pycamp_projects.db pueda
# crearse/actualizarse en el directorio del proyecto.
run:
	docker run --rm --env-file .env \
		-v "$(PROJECT_PATH):$(CONTAINER_PATH)" \
		pycamp_bot

# Tests: código montado en solo lectura (:ro). Los tests usan DB en memoria,
# así que no se escribe nada en el árbol del proyecto.
test:
	docker run --rm --env-file .env \
		-v "$(PROJECT_PATH):$(CONTAINER_PATH):ro" \
		pycamp_bot pytest

# Tests con reporte de cobertura. Código :ro; el reporte se escribe en /tmp
# para no necesitar escritura en el árbol del proyecto.
test-cov:
	docker run --rm --env-file .env \
		-e COVERAGE_FILE=/tmp/.coverage \
		-v "$(PROJECT_PATH):$(CONTAINER_PATH):ro" \
		pycamp_bot pytest --cov=pycamp_bot --cov-report=term-missing

all: build run

.DEFAULT_GOAL := all
