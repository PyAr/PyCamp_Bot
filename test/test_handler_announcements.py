from telegram.ext import ConversationHandler
from pycamp_bot.models import Pycampista, Pycamp, Project, Vote
from pycamp_bot.commands.announcements import (
    announce, get_project, meeting_place, message_project, cancel,
    user_is_admin, should_be_able_to_announce,
    AnnouncementState, state, ERROR_MESSAGES,
    PROYECTO, LUGAR, MENSAJE,
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


class TestUserIsAdmin:

    @use_test_database_async
    async def test_returns_true_for_admin(self):
        Pycampista.create(username="admin1", admin=True)
        assert await user_is_admin("admin1") is True

    @use_test_database_async
    async def test_returns_false_for_non_admin(self):
        Pycampista.create(username="regular", admin=False)
        assert await user_is_admin("regular") is False


class TestShouldBeAbleToAnnounce:

    @use_test_database_async
    async def test_owner_can_announce(self):
        owner = Pycampista.create(username="pepe")
        project = Project.create(name="MiProj", owner=owner, topic="test")
        assert await should_be_able_to_announce("pepe", project) is True

    @use_test_database_async
    async def test_admin_can_announce_any_project(self):
        owner = Pycampista.create(username="pepe")
        Pycampista.create(username="admin1", admin=True)
        project = Project.create(name="MiProj", owner=owner, topic="test")
        assert await should_be_able_to_announce("admin1", project) is True

    @use_test_database_async
    async def test_non_owner_non_admin_cannot_announce(self):
        owner = Pycampista.create(username="pepe")
        Pycampista.create(username="intruso", admin=False)
        project = Project.create(name="MiProj", owner=owner, topic="test")
        assert await should_be_able_to_announce("intruso", project) is False


class TestAnnouncementState:

    def test_initial_state(self):
        s = AnnouncementState()
        assert s.username is None
        assert s.p_name == ''
        assert s.current_project is False
        assert s.projects == []
        assert s.owner == ''
        assert s.lugar == ''
        assert s.mensaje == ''


class TestAnnounce:

    @use_test_database_async
    async def test_owner_with_projects_returns_proyecto_state(self):
        Pycamp.create(headquarters="Narnia", active=True)
        owner = Pycampista.create(username="pepe")
        Project.create(name="MiProj", owner=owner, topic="test")
        update = make_update(text="/anunciar", username="pepe")
        context = make_context()
        result = await announce(update, context)
        assert result == PROYECTO

    @use_test_database_async
    async def test_non_admin_no_projects_is_rejected(self):
        Pycamp.create(headquarters="Narnia", active=True)
        Pycampista.create(username="nadie", admin=False)
        update = make_update(text="/anunciar", username="nadie")
        context = make_context()
        result = await announce(update, context)
        assert result == ConversationHandler.END


class TestGetProject:

    @use_test_database_async
    async def test_valid_project_returns_lugar(self):
        owner = Pycampista.create(username="pepe")
        Project.create(name="MiProj", owner=owner, topic="test")
        state.username = "pepe"
        update = make_update(text="MiProj", username="pepe")
        context = make_context()
        result = await get_project(update, context)
        assert result == LUGAR

    @use_test_database_async
    async def test_nonexistent_project_returns_proyecto(self):
        Pycampista.create(username="pepe")
        state.username = "pepe"
        update = make_update(text="Fantasma", username="pepe")
        context = make_context()
        result = await get_project(update, context)
        assert result == PROYECTO


class TestMeetingPlace:

    @use_test_database_async
    async def test_sets_lugar_returns_mensaje(self):
        update = make_update(text="sala principal")
        context = make_context()
        result = await meeting_place(update, context)
        assert result == MENSAJE
        assert state.lugar == "Sala principal"


class TestMessageProject:

    @use_test_database_async
    async def test_sends_notifications_to_voters(self):
        owner = Pycampista.create(username="pepe")
        voter = Pycampista.create(username="juan", chat_id="111")
        project = Project.create(name="MiProj", owner=owner, topic="test")
        Vote.create(
            project=project, pycampista=voter, interest=True,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )
        state.username = "pepe"
        state.current_project = project
        state.p_name = "MiProj"
        state.owner = "pepe"
        state.lugar = "Sala 1"
        update = make_update(text="Arrancamos!", username="pepe")
        context = make_context()
        result = await message_project(update, context)
        assert result == ConversationHandler.END
        # Debe haber enviado mensajes al voter
        assert context.bot.send_message.call_count >= 1


class TestCancelAnnouncement:

    @use_test_database_async
    async def test_cancel_returns_end(self):
        update = make_update(text="/cancel")
        context = make_context()
        result = await cancel(update, context)
        assert result == ConversationHandler.END


class TestErrorMessages:

    def test_error_messages_dict_has_expected_keys(self):
        assert "format_error" in ERROR_MESSAGES
        assert "not_admin" in ERROR_MESSAGES
        assert "not_found" in ERROR_MESSAGES
        assert "no_admin" in ERROR_MESSAGES

    def test_not_found_formats_with_project_name(self):
        msg = ERROR_MESSAGES["not_found"].format(project_name="TestProj")
        assert "TestProj" in msg
