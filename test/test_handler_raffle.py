from unittest.mock import patch
from pycamp_bot.models import Pycampista
from pycamp_bot.commands.raffle import get_random_user
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


class TestGetRandomUser:

    @use_test_database_async
    async def test_returns_a_username(self):
        Pycampista.create(username="admin1", admin=True)
        Pycampista.create(username="pepe")
        Pycampista.create(username="juan")
        update = make_update(text="/rifar", username="admin1")
        context = make_context()
        await get_random_user(update, context)
        update.message.reply_text.assert_called_once()
        username = update.message.reply_text.call_args[0][0]
        assert username in ["admin1", "pepe", "juan"]

    @use_test_database_async
    @patch("pycamp_bot.commands.raffle.random.randint", return_value=1)
    async def test_returns_specific_user_with_mocked_random(self, mock_randint):
        Pycampista.create(username="admin1", admin=True)
        Pycampista.create(username="pepe")
        update = make_update(text="/rifar", username="admin1")
        context = make_context()
        await get_random_user(update, context)
        update.message.reply_text.assert_called_once()
        # Con randint=1, retorna el primer Pycampista creado
        username = update.message.reply_text.call_args[0][0]
        assert username == "admin1"
