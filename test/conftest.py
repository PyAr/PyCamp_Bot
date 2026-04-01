import os
import asyncio
from datetime import datetime
from functools import wraps
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from peewee import SqliteDatabase

from pycamp_bot.models import (
    Pycampista, Slot, Pycamp, WizardAtPycamp, PycampistaAtPycamp, Project, Vote
)

# -----------------------------------------------------------------------------
# Causa raíz de fallos en tests de handlers (PTB v21):
# En python-telegram-bot v21 los objetos Telegram (Message, CallbackQuery, etc.)
# son inmutables ("frozen"): no se puede asignar msg.reply_text = AsyncMock().
# Doc oficial (v20.0+): "Objects of this class (or subclasses) are now immutable.
# This means that you can't set or delete attributes anymore."
# https://docs.python-telegram-bot.org/en/v21.10/telegram.telegramobject.html
# Por eso los builders de updates usan dobles mutables (SimpleNamespace) que
# exponen la misma interfaz que los handlers (message.text, message.reply_text,
# callback_query.answer, etc.) sin tocar objetos reales de la librería.
# -----------------------------------------------------------------------------

# use an in-memory SQLite for tests.
test_db = SqliteDatabase(':memory:')

MODELS = [Pycampista, Slot, Pycamp, WizardAtPycamp, PycampistaAtPycamp, Project, Vote]


def use_test_database(fn):
    """Bind the given models to the db for the duration of wrapped block."""
    @wraps(fn)
    def inner(self):
        with test_db.bind_ctx(MODELS):
            test_db.create_tables(MODELS)
            try:
                fn(self)
            finally:
                test_db.drop_tables(MODELS)
    return inner


def use_test_database_async(fn):
    """Bind the given models to the db for the duration of an async test."""
    @wraps(fn)
    def inner(self):
        with test_db.bind_ctx(MODELS):
            test_db.create_tables(MODELS)
            try:
                asyncio.get_event_loop().run_until_complete(fn(self))
            finally:
                test_db.drop_tables(MODELS)
    return inner


def make_user(username="testuser", user_id=12345, first_name="Test"):
    """Doble mutable de telegram.User para tests (PTB v21 usa objetos congelados)."""
    return SimpleNamespace(
        id=user_id,
        first_name=first_name,
        is_bot=False,
        username=username,
    )


def make_chat(chat_id=67890, chat_type="private"):
    """Doble mutable de telegram.Chat para tests."""
    return SimpleNamespace(id=chat_id, type=chat_type)


def make_message(text="/start", username="testuser", chat_id=67890,
                 user_id=12345, message_id=1):
    """Doble mutable de telegram.Message: misma interfaz que usan los handlers."""
    user = make_user(username=username, user_id=user_id)
    chat = make_chat(chat_id=chat_id)
    msg = SimpleNamespace(
        message_id=message_id,
        date=datetime.now(),
        chat=chat,
        from_user=user,
        text=text,
        chat_id=chat_id,
        reply_text=AsyncMock(),
    )
    return msg


def make_update(text="/start", username="testuser", chat_id=67890,
                user_id=12345, update_id=1):
    """Doble mutable de telegram.Update con message; interfaz usada por handlers."""
    message = make_message(
        text=text, username=username, chat_id=chat_id,
        user_id=user_id,
    )
    return SimpleNamespace(update_id=update_id, message=message)


def make_callback_update(data="vote:si", username="testuser", chat_id=67890,
                         user_id=12345, message_text="Proyecto1", update_id=1):
    """Doble mutable de Update con callback_query para botones inline."""
    user = make_user(username=username, user_id=user_id)
    chat = make_chat(chat_id=chat_id)
    message = SimpleNamespace(
        message_id=1,
        date=datetime.now(),
        chat=chat,
        text=message_text,
        chat_id=chat_id,
        reply_text=AsyncMock(),
    )
    callback_query = SimpleNamespace(
        id="test_callback_1",
        from_user=user,
        chat_instance="test_instance",
        data=data,
        message=message,
        answer=AsyncMock(),
    )
    return SimpleNamespace(update_id=update_id, callback_query=callback_query)


def make_context():
    """Crea un mock de CallbackContext con bot mockeado según la API v21."""
    context = MagicMock()
    context.bot = AsyncMock()
    context.bot.send_message = AsyncMock()
    context.bot.edit_message_text = AsyncMock()
    return context
