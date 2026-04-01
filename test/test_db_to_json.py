from datetime import datetime
from pycamp_bot.models import Pycampista, Project, Slot, Vote
from pycamp_bot.scheduler.db_to_json import export_db_2_json
from test.conftest import use_test_database, test_db, MODELS


def setup_module(module):
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()


def teardown_module(module):
    test_db.drop_tables(MODELS)
    test_db.close()


class TestExportDb2Json:

    @use_test_database
    def test_empty_projects_returns_empty_structure(self):
        result = export_db_2_json()
        assert result["projects"] == {}
        assert result["available_slots"] == []
        assert result["responsable_available_slots"] == {}

    @use_test_database
    def test_exports_project_with_votes(self):
        owner = Pycampista.create(username="pepe")
        voter = Pycampista.create(username="juan")
        slot = Slot.create(code="A1", start=datetime(2024, 6, 21, 10, 0), current_wizard=owner)
        project = Project.create(name="MiProyecto", owner=owner, topic="django", difficult_level=2)
        Vote.create(
            project=project, pycampista=voter, interest=True,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )

        result = export_db_2_json()
        assert "MiProyecto" in result["projects"]
        proj_data = result["projects"]["MiProyecto"]
        assert proj_data["responsables"] == ["pepe"]
        assert "juan" in proj_data["votes"]
        assert proj_data["difficult_level"] == 2
        assert proj_data["theme"] == "django"

    @use_test_database
    def test_exports_available_slots(self):
        owner = Pycampista.create(username="pepe")
        Slot.create(code="A1", start=datetime(2024, 6, 21, 10, 0), current_wizard=owner)
        Slot.create(code="A2", start=datetime(2024, 6, 21, 11, 0), current_wizard=owner)
        Slot.create(code="B1", start=datetime(2024, 6, 22, 10, 0), current_wizard=owner)

        result = export_db_2_json()
        assert "A1" in result["available_slots"]
        assert "A2" in result["available_slots"]
        assert "B1" in result["available_slots"]
        assert len(result["available_slots"]) == 3

    @use_test_database
    def test_responsable_available_slots_includes_all(self):
        owner = Pycampista.create(username="pepe")
        Slot.create(code="A1", start=datetime(2024, 6, 21, 10, 0), current_wizard=owner)
        Slot.create(code="A2", start=datetime(2024, 6, 21, 11, 0), current_wizard=owner)
        Project.create(name="MiProyecto", owner=owner)

        result = export_db_2_json()
        assert "pepe" in result["responsable_available_slots"]
        assert result["responsable_available_slots"]["pepe"] == ["A1", "A2"]

    @use_test_database
    def test_vote_interest_filter(self):
        owner = Pycampista.create(username="pepe")
        voter1 = Pycampista.create(username="juan")
        voter2 = Pycampista.create(username="maria")
        project = Project.create(name="MiProyecto", owner=owner)

        Vote.create(
            project=project, pycampista=voter1, interest=True,
            _project_pycampista_id=f"{project.id}-{voter1.id}",
        )
        Vote.create(
            project=project, pycampista=voter2, interest=False,
            _project_pycampista_id=f"{project.id}-{voter2.id}",
        )

        result = export_db_2_json()
        votes = result["projects"]["MiProyecto"]["votes"]
        assert "juan" in votes
        assert "maria" not in votes
