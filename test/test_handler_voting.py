import peewee
from pycamp_bot.models import Pycampista, Pycamp, Project, Vote
from pycamp_bot.commands.voting import (
    start_voting, end_voting, vote, button, vote_count,
)
from test.conftest import (
    use_test_database_async, test_db, MODELS,
    make_update, make_callback_update, make_context,
)


def setup_module(module):
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()


def teardown_module(module):
    test_db.drop_tables(MODELS)
    test_db.close()


class TestStartVoting:

    @use_test_database_async
    async def test_opens_voting(self):
        Pycampista.create(username="admin1", admin=True)
        Pycamp.create(headquarters="Narnia", active=True, vote_authorized=False)
        update = make_update(text="/empezar_votacion_proyectos", username="admin1")
        context = make_context()
        await start_voting(update, context)
        pycamp = Pycamp.get(Pycamp.active == True)
        assert pycamp.vote_authorized is True

    @use_test_database_async
    async def test_already_open_voting(self):
        Pycampista.create(username="admin1", admin=True)
        Pycamp.create(headquarters="Narnia", active=True, vote_authorized=True)
        update = make_update(text="/empezar_votacion_proyectos", username="admin1")
        context = make_context()
        await start_voting(update, context)
        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "ya estaba abierta" in text


class TestEndVoting:

    @use_test_database_async
    async def test_closes_voting(self):
        Pycampista.create(username="admin1", admin=True)
        Pycamp.create(headquarters="Narnia", active=True, vote_authorized=True)
        update = make_update(text="/terminar_votacion_proyectos", username="admin1")
        context = make_context()
        await end_voting(update, context)
        pycamp = Pycamp.get(Pycamp.active == True)
        assert pycamp.vote_authorized is False


class TestVote:

    @use_test_database_async
    async def test_vote_sends_project_list(self):
        Pycamp.create(headquarters="Narnia", active=True, vote_authorized=True)
        owner = Pycampista.create(username="pepe")
        Project.create(name="Proyecto1", owner=owner, topic="django")
        Project.create(name="Proyecto2", owner=owner, topic="flask")
        update = make_update(text="/votar", username="pepe")
        context = make_context()
        await vote(update, context)
        # Debe enviar reply_text por cada proyecto + el mensaje inicial
        assert update.message.reply_text.call_count >= 2

    @use_test_database_async
    async def test_vote_creates_test_project_if_empty(self):
        Pycamp.create(headquarters="Narnia", active=True, vote_authorized=True)
        update = make_update(text="/votar", username="pepe")
        context = make_context()
        await vote(update, context)
        assert Project.select().where(Project.name == "PROYECTO DE PRUEBA").exists()


class TestButton:

    @use_test_database_async
    async def test_vote_si_saves_interest_true(self):
        owner = Pycampista.create(username="owner1", chat_id="11111")
        voter = Pycampista.create(username="voter1", chat_id="67890")
        project = Project.create(name="Proyecto1", owner=owner, topic="test")
        update = make_callback_update(
            data="vote:si", username="voter1",
            message_text="Proyecto1",
        )
        context = make_context()
        await button(update, context)
        vote_obj = Vote.get(Vote.pycampista == voter)
        assert vote_obj.interest is True
        text = context.bot.edit_message_text.call_args[1]["text"]
        assert "Sumade" in text

    @use_test_database_async
    async def test_vote_no_saves_interest_false(self):
        owner = Pycampista.create(username="owner1", chat_id="11111")
        voter = Pycampista.create(username="voter1", chat_id="67890")
        project = Project.create(name="Proyecto1", owner=owner, topic="test")
        update = make_callback_update(
            data="vote:no", username="voter1",
            message_text="Proyecto1",
        )
        context = make_context()
        await button(update, context)
        vote_obj = Vote.get(Vote.pycampista == voter)
        assert vote_obj.interest is False

    @use_test_database_async
    async def test_duplicate_vote_shows_warning(self):
        owner = Pycampista.create(username="owner1", chat_id="11111")
        voter = Pycampista.create(username="voter1", chat_id="67890")
        project = Project.create(name="Proyecto1", owner=owner, topic="test")
        Vote.create(
            project=project, pycampista=voter, interest=True,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )
        update = make_callback_update(
            data="vote:si", username="voter1",
            message_text="Proyecto1",
        )
        context = make_context()
        await button(update, context)
        text = context.bot.edit_message_text.call_args[1]["text"]
        assert "Ya te habías sumado" in text


class TestVoteCount:

    @use_test_database_async
    async def test_counts_unique_voters(self):
        Pycampista.create(username="admin1", admin=True)
        owner = Pycampista.create(username="owner1")
        v1 = Pycampista.create(username="voter1")
        v2 = Pycampista.create(username="voter2")
        p1 = Project.create(name="P1", owner=owner, topic="test")
        p2 = Project.create(name="P2", owner=owner, topic="test")
        Vote.create(project=p1, pycampista=v1, interest=True, _project_pycampista_id=f"{p1.id}-{v1.id}")
        Vote.create(project=p2, pycampista=v1, interest=True, _project_pycampista_id=f"{p2.id}-{v1.id}")
        Vote.create(project=p1, pycampista=v2, interest=True, _project_pycampista_id=f"{p1.id}-{v2.id}")

        update = make_update(text="/contar_votos", username="admin1")
        context = make_context()
        await vote_count(update, context)
        text = context.bot.send_message.call_args[1]["text"]
        assert "2" in text

    @use_test_database_async
    async def test_zero_votes(self):
        Pycampista.create(username="admin1", admin=True)
        update = make_update(text="/contar_votos", username="admin1")
        context = make_context()
        await vote_count(update, context)
        text = context.bot.send_message.call_args[1]["text"]
        assert "0" in text

    @use_test_database_async
    async def test_contar_votos_rejects_non_admin(self):
        Pycampista.create(username="user1", admin=False)
        update = make_update(text="/contar_votos", username="user1")
        context = make_context()
        await vote_count(update, context)
        context.bot.send_message.assert_called_once()
        text = context.bot.send_message.call_args[1]["text"]
        assert "No estas Autorizadx" in text
