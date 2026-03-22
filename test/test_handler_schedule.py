from pycamp_bot.models import Pycampista, Slot, Project
from pycamp_bot.commands.schedule import borrar_cronograma, borrar_cronograma_confirm
from test.conftest import (
    use_test_database_async,
    test_db,
    MODELS,
    make_update,
    make_callback_update,
    make_context,
)


def setup_module(module):
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()


def teardown_module(module):
    test_db.drop_tables(MODELS)
    test_db.close()


class TestBorrarCronograma:

    @use_test_database_async
    async def test_borrar_cronograma_shows_confirmation(self):
        Pycampista.create(username="admin1", chat_id="1", admin=True)
        slot_a1 = Slot.create(code="A1", start=9)
        owner = Pycampista.get(Pycampista.username == "admin1")
        Project.create(name="ProyectoX", owner=owner, slot=slot_a1)
        update = make_update(text="/borrar_cronograma", username="admin1")
        context = make_context()
        await borrar_cronograma(update, context)
        assert Slot.select().count() == 1
        assert "¿Borrar el cronograma?" in context.bot.send_message.call_args[1]["text"]
        assert context.bot.send_message.call_args[1]["reply_markup"]

    @use_test_database_async
    async def test_borrar_cronograma_confirm_si_clears_slots_and_assignments(self):
        Pycampista.create(username="admin1", chat_id="1", admin=True)
        slot_a1 = Slot.create(code="A1", start=9)
        slot_a2 = Slot.create(code="A2", start=10)
        owner = Pycampista.get(Pycampista.username == "admin1")
        Project.create(name="ProyectoX", owner=owner, slot=slot_a1)
        Project.create(name="ProyectoY", owner=owner, slot=slot_a2)
        update = make_callback_update(
            data="borrarcronograma:si", username="admin1", chat_id="1"
        )
        context = make_context()
        await borrar_cronograma_confirm(update, context)
        assert Slot.select().count() == 0
        for p in Project.select():
            assert p.slot_id is None
        assert context.bot.send_message.called
        text = context.bot.send_message.call_args[1]["text"]
        assert "Cronograma borrado" in text
        assert "/cronogramear" in text

    @use_test_database_async
    async def test_borrar_cronograma_confirm_no_cancels(self):
        Pycampista.create(username="admin1", chat_id="1", admin=True)
        slot_a1 = Slot.create(code="A1", start=9)
        owner = Pycampista.get(Pycampista.username == "admin1")
        Project.create(name="ProyectoX", owner=owner, slot=slot_a1)
        update = make_callback_update(
            data="borrarcronograma:no", username="admin1", chat_id="1"
        )
        context = make_context()
        await borrar_cronograma_confirm(update, context)
        assert Slot.select().count() == 1
        assert "Operación cancelada" in context.bot.send_message.call_args[1]["text"]

    @use_test_database_async
    async def test_borrar_cronograma_confirm_rejects_non_admin(self):
        Pycampista.create(username="admin1", chat_id="1", admin=True)
        Pycampista.create(username="user1", chat_id="2", admin=False)
        slot_a1 = Slot.create(code="A1", start=9)
        owner = Pycampista.get(Pycampista.username == "admin1")
        Project.create(name="ProyectoX", owner=owner, slot=slot_a1)
        update = make_callback_update(
            data="borrarcronograma:si", username="user1", chat_id="1"
        )
        context = make_context()
        await borrar_cronograma_confirm(update, context)
        assert Slot.select().count() == 1
        assert "No estas Autorizadx" in context.bot.send_message.call_args[1]["text"]

    @use_test_database_async
    async def test_borrar_cronograma_when_no_schedule(self):
        Pycampista.create(username="admin1", chat_id="1", admin=True)
        update = make_update(text="/borrar_cronograma", username="admin1")
        context = make_context()
        await borrar_cronograma(update, context)
        assert "No hay cronograma para borrar" in context.bot.send_message.call_args[1]["text"]
        assert Slot.select().count() == 0

    @use_test_database_async
    async def test_borrar_cronograma_rejects_non_admin(self):
        Pycampista.create(username="user1", chat_id="1", admin=False)
        slot_a1 = Slot.create(code="A1", start=9)
        owner = Pycampista.get(Pycampista.username == "user1")
        Project.create(name="ProyectoX", owner=owner, slot=slot_a1)
        update = make_update(text="/borrar_cronograma", username="user1")
        context = make_context()
        await borrar_cronograma(update, context)
        assert "No estas Autorizadx" in context.bot.send_message.call_args[1]["text"]
        assert Slot.select().count() == 1
        proj = Project.get(Project.name == "ProyectoX")
        assert proj.slot_id is not None
