import os
from unittest.mock import patch, AsyncMock
from pycamp_bot.commands.base import start, msg_to_active_pycamp_chat
from pycamp_bot.commands.help_msg import get_help, HELP_MESSAGE, HELP_MESSAGE_ADMIN
from pycamp_bot.models import Pycampista
from test.conftest import (
    use_test_database_async, test_db, MODELS,
    make_update, make_context,
)


def setup_module(module):
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()


def teardown_module(module):
    test_db.drop_tables(MODELS)
    test_db.close()


class TestStart:

    @use_test_database_async
    async def test_welcomes_user_with_username(self):
        update = make_update(text="/start", username="pepe")
        context = make_context()
        await start(update, context)
        text = context.bot.send_message.call_args[1]["text"]
        assert "pepe" in text
        assert "Bienvenidx" in text

    @use_test_database_async
    async def test_asks_for_username_when_missing(self):
        update = make_update(text="/start", username=None)
        context = make_context()
        await start(update, context)
        text = context.bot.send_message.call_args[1]["text"]
        assert "username" in text.lower()


class TestMsgToActivePycampChat:

    @use_test_database_async
    @patch.dict(os.environ, {"TEST_CHAT_ID": "12345"})
    async def test_sends_message_when_env_set(self):
        bot = AsyncMock()
        await msg_to_active_pycamp_chat(bot, "Test message")
        bot.send_message.assert_called_once()
        assert bot.send_message.call_args[1]["text"] == "Test message"

    @use_test_database_async
    async def test_does_nothing_when_env_not_set(self):
        os.environ.pop("TEST_CHAT_ID", None)
        bot = AsyncMock()
        await msg_to_active_pycamp_chat(bot, "Test message")
        bot.send_message.assert_not_called()


class TestGetHelp:

    @use_test_database_async
    async def test_returns_admin_help_for_admin(self):
        Pycampista.create(username="admin1", admin=True)
        update = make_update(username="admin1")
        context = make_context()
        result = get_help(update, context)
        assert result == HELP_MESSAGE_ADMIN

    @use_test_database_async
    async def test_returns_normal_help_for_user(self):
        Pycampista.create(username="regular", admin=False)
        update = make_update(username="regular")
        context = make_context()
        result = get_help(update, context)
        assert result == HELP_MESSAGE
