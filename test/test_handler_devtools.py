"""Tests para handlers de devtools.py: /mostrar_version."""
from unittest.mock import patch, MagicMock

from pycamp_bot.commands.devtools import show_version
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


class TestShowVersion:

    @use_test_database_async
    @patch("pycamp_bot.commands.devtools.subprocess.run")
    async def test_shows_version_info(self, mock_run):
        """Verifica que show_version envía info de commit, Python y deps."""
        # Simular los 4 subprocess.run: rev-parse, log, diff, pip freeze
        mock_run.side_effect = [
            MagicMock(stdout=b"abc1234\n", returncode=0),      # git rev-parse
            MagicMock(stdout=b"2024-06-20 10:00:00 -0300\n", returncode=0),  # git log
            MagicMock(returncode=0),                            # git diff (clean)
            MagicMock(stdout=b"python-telegram-bot==21.10\npeewee==3.17.0\n", returncode=0),  # pip freeze
        ]
        update = make_update(text="/mostrar_version")
        context = make_context()
        await show_version(update, context)
        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "abc1234" in text
        # escape_markdown escapa guiones y puntos; comprobar nombre y versión
        assert "python" in text and "21" in text and "telegram" in text

    @use_test_database_async
    @patch("pycamp_bot.commands.devtools.subprocess.run")
    async def test_dirty_worktree_shows_red(self, mock_run):
        """Verifica que worktree sucio muestra indicador rojo."""
        mock_run.side_effect = [
            MagicMock(stdout=b"abc1234\n", returncode=0),
            MagicMock(stdout=b"2024-06-20 10:00:00 -0300\n", returncode=0),
            MagicMock(returncode=1),  # git diff: dirty
            MagicMock(stdout=b"peewee==3.17.0\n", returncode=0),
        ]
        update = make_update(text="/mostrar_version")
        context = make_context()
        await show_version(update, context)
        text = update.message.reply_text.call_args[0][0]
        # Indicador rojo para worktree sucio
        assert "\U0001f534" in text  # 🔴

    @use_test_database_async
    @patch("pycamp_bot.commands.devtools.subprocess.run")
    @patch.dict("os.environ", {"SENTRY_DATA_SOURCE_NAME": "https://sentry.io/123"})
    async def test_sentry_env_set_shows_green(self, mock_run):
        """Verifica que con Sentry configurado muestra indicador verde."""
        mock_run.side_effect = [
            MagicMock(stdout=b"abc1234\n", returncode=0),
            MagicMock(stdout=b"2024-06-20 10:00:00 -0300\n", returncode=0),
            MagicMock(returncode=0),
            MagicMock(stdout=b"peewee==3.17.0\n", returncode=0),
        ]
        update = make_update(text="/mostrar_version")
        context = make_context()
        await show_version(update, context)
        text = update.message.reply_text.call_args[0][0]
        # Último indicador debe ser verde (Sentry definida)
        assert text.count("\U0001f7e2") >= 2  # 🟢 para clean worktree + sentry
