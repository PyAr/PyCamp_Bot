"""Tests para handlers de wizard.py: /ser_magx, /ver_magx, /evocar_magx, /agendar_magx, /ver_agenda_magx."""
from datetime import datetime
from freezegun import freeze_time
from pycamp_bot.models import Pycampista, Pycamp, PycampistaAtPycamp, WizardAtPycamp
from pycamp_bot.commands.wizard import (
    become_wizard, list_wizards, summon_wizard, schedule_wizards,
    show_wizards_schedule, format_wizards_schedule,
    persist_wizards_schedule_in_db, aux_resolve_show_all,
)
from test.conftest import (
    use_test_database, use_test_database_async, test_db, MODELS,
    make_update, make_message, make_context,
)


def setup_module(module):
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()


def teardown_module(module):
    test_db.drop_tables(MODELS)
    test_db.close()


class TestBecomeWizard:

    @use_test_database_async
    async def test_registers_user_as_wizard(self):
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        update = make_update(text="/ser_magx", username="gandalf")
        context = make_context()
        await become_wizard(update, context, pycamp=p)
        wizard = Pycampista.get(Pycampista.username == "gandalf")
        assert wizard.wizard is True
        assert "registrado como magx" in context.bot.send_message.call_args[1]["text"]


class TestListWizards:

    @use_test_database_async
    async def test_lists_registered_wizards(self):
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        p.add_wizard("gandalf", "111")
        p.add_wizard("merlin", "222")
        update = make_update(text="/ver_magx", username="admin1")
        context = make_context()
        await list_wizards(update, context, pycamp=p)
        text = context.bot.send_message.call_args[1]["text"]
        assert "@gandalf" in text
        assert "@merlin" in text

    @use_test_database_async
    async def test_empty_list(self):
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        update = make_update(text="/ver_magx", username="admin1")
        context = make_context()
        # list_wizards con msg vacío: BadRequest se ignora internamente
        await list_wizards(update, context, pycamp=p)


class TestSummonWizard:

    @use_test_database_async
    @freeze_time("2024-06-21 15:30:00")
    async def test_summons_current_wizard(self):
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        w = p.add_wizard("gandalf", "111")
        persist_wizards_schedule_in_db(p)

        update = make_update(text="/evocar_magx", username="pepe")
        context = make_context()
        await summon_wizard(update, context, pycamp=p)
        # Debe haber enviado un PING al wizard
        sent_texts = [call[1]["text"] for call in context.bot.send_message.call_args_list]
        assert any("PING" in t or "magx" in t.lower() for t in sent_texts)

    @use_test_database_async
    async def test_no_wizard_scheduled(self):
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        update = make_update(text="/evocar_magx", username="pepe")
        context = make_context()
        await summon_wizard(update, context, pycamp=p)
        text = context.bot.send_message.call_args[1]["text"]
        assert "No hay" in text

    @use_test_database_async
    @freeze_time("2024-06-21 15:30:00")
    async def test_wizard_summons_self(self):
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        w = p.add_wizard("gandalf", "111")
        persist_wizards_schedule_in_db(p)

        update = make_update(text="/evocar_magx", username="gandalf")
        context = make_context()
        await summon_wizard(update, context, pycamp=p)
        sent_texts = [call[1]["text"] for call in context.bot.send_message.call_args_list]
        assert any("sombrero" in t for t in sent_texts)


class TestScheduleWizards:

    @use_test_database_async
    async def test_schedules_and_persists(self):
        Pycampista.create(username="admin1", admin=True)
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        p.add_wizard("gandalf", "111")
        update = make_update(text="/agendar_magx", username="admin1")
        context = make_context()
        await schedule_wizards(update, context, pycamp=p)
        assert WizardAtPycamp.select().where(WizardAtPycamp.pycamp == p).count() > 0

    @use_test_database_async
    async def test_clears_previous_schedule(self):
        """Agendar de nuevo borra la agenda anterior."""
        Pycampista.create(username="admin1", admin=True)
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        w = p.add_wizard("gandalf", "111")
        # Primera agenda
        persist_wizards_schedule_in_db(p)
        count1 = WizardAtPycamp.select().where(WizardAtPycamp.pycamp == p).count()
        # Segunda agenda via handler
        update = make_update(text="/agendar_magx", username="admin1")
        context = make_context()
        await schedule_wizards(update, context, pycamp=p)
        count2 = WizardAtPycamp.select().where(WizardAtPycamp.pycamp == p).count()
        assert count2 == count1  # misma cantidad, no acumulada


class TestShowWizardsSchedule:

    @use_test_database_async
    @freeze_time("2024-06-21 10:00:00")
    async def test_shows_remaining_schedule(self):
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        w = p.add_wizard("gandalf", "111")
        persist_wizards_schedule_in_db(p)

        update = make_update(text="/ver_agenda_magx", username="pepe")
        context = make_context()
        await show_wizards_schedule(update, context, pycamp=p)
        text = context.bot.send_message.call_args[1]["text"]
        assert "Agenda" in text or "magx" in text.lower()

    @use_test_database_async
    @freeze_time("2024-06-21 10:00:00")
    async def test_shows_complete_schedule_with_flag(self):
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        w = p.add_wizard("gandalf", "111")
        persist_wizards_schedule_in_db(p)

        update = make_update(text="/ver_agenda_magx completa", username="pepe")
        context = make_context()
        await show_wizards_schedule(update, context, pycamp=p)
        text = context.bot.send_message.call_args[1]["text"]
        assert "Agenda" in text or "magx" in text.lower()

    @use_test_database_async
    async def test_wrong_parameter_shows_error(self):
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        update = make_update(text="/ver_agenda_magx basura", username="pepe")
        context = make_context()
        context.args = ["basura"]
        await show_wizards_schedule(update, context, pycamp=p)
        text = context.bot.send_message.call_args[1]["text"]
        assert "parámetro" in text.lower() or "completa" in text.lower()

    @use_test_database_async
    async def test_empty_agenda_sends_hint_without_parse_mode(self):
        """Sin turnos se envía hint en texto plano (sin MarkdownV2) para evitar BadRequest por '.'."""
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        # Sin magxs ni /agendar_magx no hay WizardAtPycamp
        update = make_update(text="/ver_agenda_magx", username="pepe")
        context = make_context()
        await show_wizards_schedule(update, context, pycamp=p)
        kwargs = context.bot.send_message.call_args[1]
        assert "No hay turnos cargados" in kwargs["text"]
        assert kwargs.get("parse_mode") is None

    @use_test_database_async
    @freeze_time("2024-06-21 10:00:00")
    async def test_empty_futuros_sends_hint_without_parse_mode(self):
        """Con 'futuros' y sin turnos futuros, hint en texto plano."""
        p = Pycamp.create(
            headquarters="Narnia", active=True,
            init=datetime(2020, 1, 1), end=datetime(2020, 1, 2),
        )
        update = make_update(text="/ver_agenda_magx futuros", username="pepe")
        context = make_context()
        context.args = ["futuros"]
        await show_wizards_schedule(update, context, pycamp=p)
        kwargs = context.bot.send_message.call_args[1]
        assert "No hay turnos futuros" in kwargs["text"]
        assert kwargs.get("parse_mode") is None


class TestFormatWizardsSchedule:

    @use_test_database
    def test_formats_agenda(self):
        p = Pycamp.create(
            headquarters="Narnia",
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        w = Pycampista.create(username="gandalf", wizard=True)
        WizardAtPycamp.create(
            pycamp=p, wizard=w,
            init=datetime(2024, 6, 21, 9, 0),
            end=datetime(2024, 6, 21, 10, 0),
        )
        agenda = WizardAtPycamp.select().where(WizardAtPycamp.pycamp == p)
        msg = format_wizards_schedule(agenda)
        assert "Agenda de magxs" in msg
        assert "@gandalf" in msg
        assert "09:00" in msg

    @use_test_database
    def test_empty_agenda(self):
        p = Pycamp.create(
            headquarters="Narnia",
            init=datetime(2024, 6, 20), end=datetime(2024, 6, 23),
        )
        agenda = WizardAtPycamp.select().where(WizardAtPycamp.pycamp == p)
        msg = format_wizards_schedule(agenda)
        assert "Agenda de magxs" in msg


class TestAuxResolveShowAll:
    """aux_resolve_show_all recibe context (con context.args)."""

    def test_no_parameter_returns_true(self):
        context = make_context()
        context.args = []
        assert aux_resolve_show_all(context) is True  # por defecto se muestra agenda completa

    def test_completa_returns_true(self):
        context = make_context()
        context.args = ["completa"]
        assert aux_resolve_show_all(context) is True

    def test_futuros_returns_false(self):
        context = make_context()
        context.args = ["futuros"]
        assert aux_resolve_show_all(context) is False

    def test_wrong_parameter_raises(self):
        import pytest
        context = make_context()
        context.args = ["basura"]
        with pytest.raises(ValueError):
            aux_resolve_show_all(context)

    def test_too_many_parameters_raises(self):
        import pytest
        context = make_context()
        context.args = ["completa", "extra"]
        with pytest.raises(ValueError):
            aux_resolve_show_all(context)
