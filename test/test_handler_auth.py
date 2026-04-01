import os
from unittest.mock import patch
from pycamp_bot.models import Pycampista
from pycamp_bot.commands.auth import (
    grant_admin, revoke_admin, list_admins, is_admin, admin_needed,
)
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


class TestIsAdmin:

    @use_test_database_async
    async def test_returns_true_for_admin_user(self):
        Pycampista.create(username="admin1", admin=True)
        update = make_update(username="admin1")
        context = make_context()
        assert is_admin(update, context) is True

    @use_test_database_async
    async def test_returns_false_for_non_admin_user(self):
        Pycampista.create(username="regular", admin=False)
        update = make_update(username="regular")
        context = make_context()
        assert is_admin(update, context) is False

    @use_test_database_async
    async def test_returns_false_for_unknown_user(self):
        update = make_update(username="unknown")
        context = make_context()
        assert is_admin(update, context) is False


class TestAdminNeeded:

    @use_test_database_async
    async def test_allows_admin_to_proceed(self):
        Pycampista.create(username="admin1", admin=True)
        update = make_update(username="admin1")
        context = make_context()

        called = False
        async def handler(update, context):
            nonlocal called
            called = True

        wrapped = admin_needed(handler)
        await wrapped(update, context)
        assert called is True

    @use_test_database_async
    async def test_blocks_non_admin(self):
        Pycampista.create(username="regular", admin=False)
        update = make_update(username="regular")
        context = make_context()

        called = False
        async def handler(update, context):
            nonlocal called
            called = True

        wrapped = admin_needed(handler)
        await wrapped(update, context)
        assert called is False
        context.bot.send_message.assert_called_once()
        call_kwargs = context.bot.send_message.call_args[1]
        assert "No estas Autorizadx" in call_kwargs["text"]


class TestGrantAdmin:

    @use_test_database_async
    @patch.dict(os.environ, {"PYCAMP_BOT_MASTER_KEY": "secreto123"})
    async def test_grants_admin_with_correct_password(self):
        update = make_update(text="/su secreto123", username="pepe")
        context = make_context()
        await grant_admin(update, context)
        user = Pycampista.get(Pycampista.username == "pepe")
        assert user.admin is True
        context.bot.send_message.assert_called_once()
        assert "poder" in context.bot.send_message.call_args[1]["text"]

    @use_test_database_async
    @patch.dict(os.environ, {"PYCAMP_BOT_MASTER_KEY": "secreto123"})
    async def test_rejects_wrong_password(self):
        update = make_update(text="/su wrongpass", username="pepe")
        context = make_context()
        await grant_admin(update, context)
        user = Pycampista.get(Pycampista.username == "pepe")
        assert user.admin is not True
        assert "magic word" in context.bot.send_message.call_args[1]["text"]

    @use_test_database_async
    async def test_rejects_missing_parameter(self):
        update = make_update(text="/su", username="pepe")
        context = make_context()
        await grant_admin(update, context)
        assert "Parametros incorrectos" in context.bot.send_message.call_args[1]["text"]

    @use_test_database_async
    @patch.dict(os.environ, {}, clear=True)
    async def test_error_when_env_not_set(self):
        # Limpiar PYCAMP_BOT_MASTER_KEY si existe
        os.environ.pop("PYCAMP_BOT_MASTER_KEY", None)
        update = make_update(text="/su algo", username="pepe")
        context = make_context()
        await grant_admin(update, context)
        assert "problema en el servidor" in context.bot.send_message.call_args[1]["text"]


class TestRevokeAdmin:

    @use_test_database_async
    async def test_revokes_admin_privileges(self):
        Pycampista.create(username="admin1", admin=True)
        Pycampista.create(username="fallen", admin=True)
        update = make_update(text="/degradar fallen", username="admin1")
        context = make_context()
        await revoke_admin(update, context)
        fallen = Pycampista.get(Pycampista.username == "fallen")
        assert fallen.admin is False

    @use_test_database_async
    async def test_revoke_rejects_missing_parameter(self):
        Pycampista.create(username="admin1", admin=True)
        update = make_update(text="/degradar", username="admin1")
        context = make_context()
        await revoke_admin(update, context)
        assert "Parametros incorrectos" in context.bot.send_message.call_args[1]["text"]


class TestListAdmins:

    @use_test_database_async
    async def test_lists_all_admins(self):
        Pycampista.create(username="admin1", admin=True)
        Pycampista.create(username="admin2", admin=True)
        update = make_update(username="admin1")
        context = make_context()
        await list_admins(update, context)
        text = context.bot.send_message.call_args[1]["text"]
        assert "@admin1" in text
        assert "@admin2" in text
