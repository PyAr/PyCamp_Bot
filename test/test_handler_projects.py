import peewee
from peewee import JOIN
from telegram.ext import ConversationHandler
from pycamp_bot.models import Pycampista, Pycamp, Project, Vote, Slot
from pycamp_bot.commands.projects import (
    load_project, naming_project, project_level, project_topic,
    save_project, ask_if_repository_exists, ask_if_group_exists,
    project_repository, project_group, cancel,
    ask_project_name, ask_repository_url, ask_group_url,
    add_repository, add_group,
    delete_project, show_projects, show_participants, show_my_projects,
    start_project_load, end_project_load,
    current_projects,
    NOMBRE, DIFICULTAD, TOPIC, CHECK_REPOSITORIO, REPOSITORIO, CHECK_GRUPO, GRUPO,
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


class TestLoadProject:

    @use_test_database_async
    async def test_starts_dialog_returns_nombre(self):
        Pycampista.create(username="admin1", admin=True)
        p = Pycamp.create(headquarters="Narnia", active=True, project_load_authorized=True)
        update = make_update(text="/cargar_proyecto", username="admin1")
        context = make_context()
        result = await load_project(update, context)
        assert result == NOMBRE

    @use_test_database_async
    async def test_blocked_when_not_authorized(self):
        Pycampista.create(username="user1")
        Pycamp.create(headquarters="Narnia", active=True, project_load_authorized=False)
        update = make_update(text="/cargar_proyecto", username="user1")
        context = make_context()
        result = await load_project(update, context)
        assert result is None
        assert "no está autorizada" in context.bot.send_message.call_args[1]["text"]


class TestNamingProject:

    @use_test_database_async
    async def test_sets_project_name_returns_dificultad(self):
        # chat_id debe coincidir con make_update() para que get_or_create encuentre al usuario
        Pycampista.create(username="pepe", chat_id=str(67890))
        update = make_update(text="Mi Proyecto Genial", username="pepe")
        context = make_context()
        result = await naming_project(update, context)
        assert result == DIFICULTAD
        assert "pepe" in current_projects
        assert current_projects["pepe"].name == "Mi Proyecto Genial"

    @use_test_database_async
    async def test_handles_cargar_proyecto_reentry(self):
        update = make_update(text="/cargar_proyecto", username="pepe")
        context = make_context()
        result = await naming_project(update, context)
        assert result == NOMBRE


class TestProjectLevel:

    @use_test_database_async
    async def test_valid_level_returns_topic(self):
        owner = Pycampista.create(username="pepe")
        proj = Project(name="Test", owner=owner)
        current_projects["pepe"] = proj
        update = make_update(text="2", username="pepe")
        context = make_context()
        result = await project_level(update, context)
        assert result == TOPIC
        assert current_projects["pepe"].difficult_level == "2"

    @use_test_database_async
    async def test_invalid_level_returns_dificultad(self):
        update = make_update(text="5", username="pepe")
        context = make_context()
        result = await project_level(update, context)
        assert result == DIFICULTAD


class TestProjectTopic:

    @use_test_database_async
    async def test_sets_topic_returns_check_repositorio(self):
        owner = Pycampista.create(username="pepe")
        proj = Project(name="Test", owner=owner)
        current_projects["pepe"] = proj
        update = make_update(text="django", username="pepe")
        context = make_context()
        result = await project_topic(update, context)
        assert result == CHECK_REPOSITORIO
        assert current_projects["pepe"].topic == "django"


class TestAskIfRepositoryExists:

    @use_test_database_async
    async def test_yes_returns_repositorio(self):
        update = make_callback_update(data="repoexists:si")
        context = make_context()
        result = await ask_if_repository_exists(update, context)
        assert result == REPOSITORIO

    @use_test_database_async
    async def test_no_returns_check_grupo(self):
        owner = Pycampista.create(username="testuser", chat_id=str(67890))
        proj = Project(name="ProjTmp", owner=owner, topic="test")
        current_projects["testuser"] = proj
        update = make_callback_update(data="groupexists:no", username="testuser")
        context = make_context()
        result = await ask_if_group_exists(update, context)
        assert result == ConversationHandler.END
        assert Project.select().where(Project.name == "ProjTmp").exists()


class TestAskIfGroupExists:

    @use_test_database_async
    async def test_yes_returns_grupo(self):
        update = make_callback_update(data="groupexists:si")
        context = make_context()
        result = await ask_if_group_exists(update, context)
        assert result == GRUPO

    @use_test_database_async
    async def test_no_saves_project_and_ends(self):
        owner = Pycampista.create(username="testuser")
        proj = Project(name="TestProj", owner=owner, topic="django")
        current_projects["testuser"] = proj
        update = make_callback_update(data="groupexists:no", username="testuser")
        context = make_context()
        result = await ask_if_group_exists(update, context)
        assert result == ConversationHandler.END
        assert Project.select().where(Project.name == "TestProj").exists()


class TestSaveProject:

    @use_test_database_async
    async def test_saves_project_successfully(self):
        owner = Pycampista.create(username="pepe")
        proj = Project(name="NuevoProj", owner=owner, topic="flask")
        current_projects["pepe"] = proj
        context = make_context()
        await save_project("pepe", 67890, context)
        assert Project.select().where(Project.name == "NuevoProj").exists()
        assert "cargado" in context.bot.send_message.call_args[1]["text"]

    @use_test_database_async
    async def test_handles_duplicate_name(self):
        owner = Pycampista.create(username="pepe")
        Project.create(name="Existente", owner=owner, topic="flask")
        proj = Project(name="Existente", owner=owner, topic="django")
        current_projects["pepe"] = proj
        context = make_context()
        await save_project("pepe", 67890, context)
        assert "ya fue cargado" in context.bot.send_message.call_args[1]["text"]


class TestProjectRepository:

    @use_test_database_async
    async def test_sets_repo_url_returns_check_grupo(self):
        owner = Pycampista.create(username="pepe")
        proj = Project(name="Test", owner=owner)
        current_projects["pepe"] = proj
        update = make_update(text="https://github.com/test", username="pepe")
        context = make_context()
        result = await project_repository(update, context)
        assert result == CHECK_GRUPO
        assert current_projects["pepe"].repository_url == "https://github.com/test"


class TestProjectGroup:

    @use_test_database_async
    async def test_sets_group_url_and_saves(self):
        owner = Pycampista.create(username="pepe")
        proj = Project(name="TestGrp", owner=owner, topic="flask")
        current_projects["pepe"] = proj
        update = make_update(text="https://t.me/grupo", username="pepe")
        context = make_context()
        result = await project_group(update, context)
        assert result == ConversationHandler.END
        assert Project.select().where(Project.name == "TestGrp").exists()


class TestDeleteProject:

    @use_test_database_async
    async def test_owner_can_delete_project(self):
        owner = Pycampista.create(username="pepe")
        Project.create(name="borrame", owner=owner, topic="test")
        update = make_update(text="/borrar_proyecto borrame", username="pepe")
        context = make_context()
        await delete_project(update, context)
        assert not Project.select().where(Project.name == "borrame").exists()
        assert "eliminado" in context.bot.send_message.call_args[1]["text"]

    @use_test_database_async
    async def test_admin_can_delete_project(self):
        owner = Pycampista.create(username="pepe")
        Pycampista.create(username="admin1", admin=True)
        Project.create(name="borrame", owner=owner, topic="test")
        update = make_update(text="/borrar_proyecto borrame", username="admin1")
        context = make_context()
        await delete_project(update, context)
        assert not Project.select().where(Project.name == "borrame").exists()

    @use_test_database_async
    async def test_non_owner_non_admin_cannot_delete(self):
        owner = Pycampista.create(username="pepe")
        Pycampista.create(username="intruso", admin=False)
        Project.create(name="borrame", owner=owner, topic="test")
        update = make_update(text="/borrar_proyecto borrame", username="intruso")
        context = make_context()
        await delete_project(update, context)
        assert Project.select().where(Project.name == "borrame").exists()
        assert "Careta" in context.bot.send_message.call_args[1]["text"]

    @use_test_database_async
    async def test_missing_project_name_shows_help(self):
        update = make_update(text="/borrar_proyecto", username="pepe")
        context = make_context()
        await delete_project(update, context)
        assert "nombre de proyecto" in context.bot.send_message.call_args[1]["text"]

    @use_test_database_async
    async def test_nonexistent_project_shows_error(self):
        update = make_update(text="/borrar_proyecto fantasma", username="pepe")
        context = make_context()
        await delete_project(update, context)
        assert "No se encontró" in context.bot.send_message.call_args[1]["text"]


class TestShowProjects:

    @use_test_database_async
    async def test_shows_projects_list(self):
        owner = Pycampista.create(username="pepe")
        Project.create(name="Proyecto1", owner=owner, topic="django", difficult_level=1)
        Project.create(name="Proyecto2", owner=owner, topic="flask", difficult_level=2)
        update = make_update(text="/proyectos")
        context = make_context()
        await show_projects(update, context)
        text = update.message.reply_text.call_args[1].get("text",
               update.message.reply_text.call_args[0][0] if update.message.reply_text.call_args[0] else "")
        assert "Proyecto1" in text or "Proyecto2" in text

    @use_test_database_async
    async def test_shows_no_projects_message(self):
        update = make_update(text="/proyectos")
        context = make_context()
        await show_projects(update, context)
        text = update.message.reply_text.call_args[0][0]
        assert "no hay" in text.lower()


class TestShowParticipants:

    @use_test_database_async
    async def test_shows_participants_for_project(self):
        owner = Pycampista.create(username="pepe")
        voter = Pycampista.create(username="juan", chat_id="111")
        project = Project.create(name="MiProyecto", owner=owner, topic="test")
        Vote.create(
            project=project, pycampista=voter, interest=True,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )
        update = make_update(text="/participantes MiProyecto")
        context = make_context()
        await show_participants(update, context)
        text = update.message.reply_text.call_args[0][0]
        assert "@juan" in text

    @use_test_database_async
    async def test_missing_project_name(self):
        update = make_update(text="/participantes")
        context = make_context()
        await show_participants(update, context)
        assert "nombre del proyecto" in context.bot.send_message.call_args[1]["text"]


class TestStartEndProjectLoad:

    @use_test_database_async
    async def test_start_project_load_opens_loading(self):
        Pycampista.create(username="admin1", admin=True)
        Pycamp.create(headquarters="Narnia", active=True, project_load_authorized=False)
        update = make_update(text="/empezar_carga_proyectos", username="admin1")
        context = make_context()
        await start_project_load(update, context)
        pycamp = Pycamp.get(Pycamp.active == True)
        assert pycamp.project_load_authorized is True

    @use_test_database_async
    async def test_end_project_load_closes_loading(self):
        Pycampista.create(username="admin1", admin=True)
        Pycamp.create(headquarters="Narnia", active=True, project_load_authorized=True)
        update = make_update(text="/terminar_carga_proyectos", username="admin1")
        context = make_context()
        await end_project_load(update, context)
        pycamp = Pycamp.get(Pycamp.active == True)
        assert pycamp.project_load_authorized is False


class TestShowMyProjects:

    @use_test_database_async
    async def test_shows_voted_projects(self):
        owner = Pycampista.create(username="pepe")
        voter = Pycampista.create(username="juan", chat_id="111")
        project = Project.create(name="MiProj", owner=owner, topic="test")
        Vote.create(
            project=project, pycampista=voter, interest=True,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )
        update = make_update(text="/mis_proyectos", username="juan")
        context = make_context()
        await show_my_projects(update, context)
        text = update.message.reply_text.call_args[0][0]
        assert "MiProj" in text

    @use_test_database_async
    async def test_no_votes_shows_message(self):
        Pycampista.create(username="pepe")
        update = make_update(text="/mis_proyectos", username="pepe")
        context = make_context()
        await show_my_projects(update, context)
        text = update.message.reply_text.call_args[0][0]
        assert "No votaste" in text

    @use_test_database_async
    async def test_shows_projects_with_assigned_slots(self):
        import datetime as dt
        Pycamp.create(
            headquarters="Narnia", active=True,
            init=dt.datetime(2024, 6, 20),
        )
        owner = Pycampista.create(username="pepe")
        voter = Pycampista.create(username="juan", chat_id="111")
        slot_a1 = Slot.create(code="A1", start=9)
        project = Project.create(
            name="MiProj", owner=owner, topic="test", slot=slot_a1,
        )
        Vote.create(
            project=project, pycampista=voter, interest=True,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )
        update = make_update(text="/mis_proyectos", username="juan")
        context = make_context()
        await show_my_projects(update, context)
        text = update.message.reply_text.call_args[0][0]
        assert "MiProj" in text
        assert "9:00" in text


class TestAskProjectName:

    @use_test_database_async
    async def test_shows_user_projects_for_selection(self):
        Pycamp.create(headquarters="Narnia", active=True)
        owner = Pycampista.create(username="pepe")
        Project.create(name="Proj1", owner=owner, topic="test")
        Project.create(name="Proj2", owner=owner, topic="test")
        update = make_update(text="/agregar_repositorio", username="pepe")
        context = make_context()
        result = await ask_project_name(update, context)
        assert result == 1
        assert "modificar" in context.bot.send_message.call_args[1]["text"]

    @use_test_database_async
    async def test_no_projects_shows_message(self):
        Pycamp.create(headquarters="Narnia", active=True)
        Pycampista.create(username="pepe")
        update = make_update(text="/agregar_repositorio", username="pepe")
        context = make_context()
        result = await ask_project_name(update, context)
        assert result == ConversationHandler.END
        assert "No cargaste" in context.bot.send_message.call_args[1]["text"]


class TestAskRepositoryUrl:

    @use_test_database_async
    async def test_stores_project_id_and_asks_url(self):
        update = make_callback_update(data="projectname:42", username="pepe")
        context = make_context()
        result = await ask_repository_url(update, context)
        assert result == 2
        assert current_projects["pepe"] == "42"
        assert "URL" in context.bot.send_message.call_args[1]["text"]


class TestAskGroupUrl:

    @use_test_database_async
    async def test_stores_project_id_and_asks_url(self):
        update = make_callback_update(data="projectname:42", username="pepe")
        context = make_context()
        result = await ask_group_url(update, context)
        assert result == 2
        assert current_projects["pepe"] == "42"
        assert "URL" in context.bot.send_message.call_args[1]["text"]


class TestAddRepository:

    @use_test_database_async
    async def test_adds_repository_url(self):
        owner = Pycampista.create(username="pepe")
        project = Project.create(name="Proj1", owner=owner, topic="test")
        current_projects["pepe"] = str(project.id)
        update = make_update(text="https://github.com/mi-repo", username="pepe")
        context = make_context()
        result = await add_repository(update, context)
        assert result == ConversationHandler.END
        proj = Project.get(Project.id == project.id)
        assert proj.repository_url == "https://github.com/mi-repo"
        assert "Repositorio agregado" in context.bot.send_message.call_args[1]["text"]


class TestAddGroup:

    @use_test_database_async
    async def test_adds_group_url(self):
        owner = Pycampista.create(username="pepe")
        project = Project.create(name="Proj1", owner=owner, topic="test")
        current_projects["pepe"] = str(project.id)
        update = make_update(text="https://t.me/grupo", username="pepe")
        context = make_context()
        result = await add_group(update, context)
        assert result == ConversationHandler.END
        proj = Project.get(Project.id == project.id)
        assert proj.group_url == "https://t.me/grupo"
        assert "Grupo agregado" in context.bot.send_message.call_args[1]["text"]


class TestCancelProject:

    @use_test_database_async
    async def test_cancel_returns_end(self):
        update = make_update(text="/cancel")
        context = make_context()
        result = await cancel(update, context)
        assert result == ConversationHandler.END
