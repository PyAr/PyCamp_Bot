from datetime import datetime, timedelta
import peewee
from pycamp_bot.models import (
    Pycamp, Pycampista, PycampistaAtPycamp, WizardAtPycamp,
    Slot, Project, Vote, DEFAULT_SLOT_PERIOD,
)
from test.conftest import use_test_database, test_db, MODELS


def setup_module(module):
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()


def teardown_module(module):
    test_db.drop_tables(MODELS)
    test_db.close()


class TestPycampSetAsOnlyActive:

    @use_test_database
    def test_activates_pycamp(self):
        p = Pycamp.create(headquarters="Narnia")
        assert not p.active
        p.set_as_only_active()
        p = Pycamp.get_by_id(p.id)
        assert p.active

    @use_test_database
    def test_deactivates_other_pycamps(self):
        p1 = Pycamp.create(headquarters="Narnia", active=True)
        p2 = Pycamp.create(headquarters="Mordor")
        p2.set_as_only_active()
        p1 = Pycamp.get_by_id(p1.id)
        assert not p1.active
        p2 = Pycamp.get_by_id(p2.id)
        assert p2.active

    @use_test_database
    def test_single_pycamp_active(self):
        p = Pycamp.create(headquarters="Narnia")
        p.set_as_only_active()
        active_count = Pycamp.select().where(Pycamp.active).count()
        assert active_count == 1

    @use_test_database
    def test_multiple_active_pycamps_resolved(self):
        p1 = Pycamp.create(headquarters="Narnia", active=True)
        p2 = Pycamp.create(headquarters="Mordor", active=True)
        p3 = Pycamp.create(headquarters="Rivendel")
        p3.set_as_only_active()
        active_count = Pycamp.select().where(Pycamp.active).count()
        assert active_count == 1
        p3 = Pycamp.get_by_id(p3.id)
        assert p3.active


class TestPycampClearWizardsSchedule:

    @use_test_database
    def test_clears_all_wizard_assignments(self):
        p = Pycamp.create(
            headquarters="Narnia",
            init=datetime(2024, 6, 20),
            end=datetime(2024, 6, 23),
        )
        w = Pycampista.create(username="gandalf", wizard=True)
        WizardAtPycamp.create(
            pycamp=p, wizard=w,
            init=datetime(2024, 6, 21, 9, 0),
            end=datetime(2024, 6, 21, 10, 0),
        )
        WizardAtPycamp.create(
            pycamp=p, wizard=w,
            init=datetime(2024, 6, 21, 10, 0),
            end=datetime(2024, 6, 21, 11, 0),
        )
        assert WizardAtPycamp.select().where(WizardAtPycamp.pycamp == p).count() == 2
        p.clear_wizards_schedule()
        assert WizardAtPycamp.select().where(WizardAtPycamp.pycamp == p).count() == 0

    @use_test_database
    def test_returns_count_of_deleted(self):
        p = Pycamp.create(headquarters="Narnia")
        w = Pycampista.create(username="gandalf", wizard=True)
        WizardAtPycamp.create(
            pycamp=p, wizard=w,
            init=datetime(2024, 6, 21, 9, 0),
            end=datetime(2024, 6, 21, 10, 0),
        )
        deleted = p.clear_wizards_schedule()
        assert deleted == 1

    @use_test_database
    def test_no_wizards_returns_zero(self):
        p = Pycamp.create(headquarters="Narnia")
        deleted = p.clear_wizards_schedule()
        assert deleted == 0


class TestSlotGetEndTime:

    @use_test_database
    def test_returns_start_plus_60_minutes(self):
        pycamper = Pycampista.create(username="pepe")
        slot = Slot.create(code="A1", start=datetime(2024, 6, 21, 10, 0), current_wizard=pycamper)
        expected = datetime(2024, 6, 21, 11, 0)
        assert slot.get_end_time() == expected

    @use_test_database
    def test_end_time_crosses_hour_boundary(self):
        pycamper = Pycampista.create(username="pepe")
        slot = Slot.create(code="A1", start=datetime(2024, 6, 21, 10, 30), current_wizard=pycamper)
        expected = datetime(2024, 6, 21, 11, 30)
        assert slot.get_end_time() == expected

    @use_test_database
    def test_default_slot_period_is_60(self):
        assert DEFAULT_SLOT_PERIOD == 60


class TestProjectModel:

    @use_test_database
    def test_create_project(self):
        owner = Pycampista.create(username="pepe")
        project = Project.create(name="Mi Proyecto", owner=owner)
        assert project.name == "Mi Proyecto"
        assert project.owner.username == "pepe"

    @use_test_database
    def test_unique_name_constraint(self):
        owner = Pycampista.create(username="pepe")
        Project.create(name="Mi Proyecto", owner=owner)
        with self._raises_integrity_error():
            Project.create(name="Mi Proyecto", owner=owner)

    @use_test_database
    def test_project_with_slot_assignment(self):
        owner = Pycampista.create(username="pepe")
        slot = Slot.create(code="A1", start=datetime(2024, 6, 21, 10, 0), current_wizard=owner)
        project = Project.create(name="Mi Proyecto", owner=owner, slot=slot)
        assert project.slot.code == "A1"

    @use_test_database
    def test_project_optional_fields_null(self):
        owner = Pycampista.create(username="pepe")
        project = Project.create(name="Mi Proyecto", owner=owner)
        assert project.topic is None
        assert project.repository_url is None
        assert project.group_url is None
        assert project.slot_id is None

    @use_test_database
    def test_project_with_all_fields(self):
        owner = Pycampista.create(username="pepe")
        project = Project.create(
            name="Mi Proyecto",
            owner=owner,
            difficult_level=2,
            topic="django",
            repository_url="https://github.com/test",
            group_url="https://t.me/test",
        )
        assert project.difficult_level == 2
        assert project.topic == "django"
        assert project.repository_url == "https://github.com/test"

    @staticmethod
    def _raises_integrity_error():
        import contextlib
        return contextlib.suppress(peewee.IntegrityError) if False else __import__('pytest').raises(peewee.IntegrityError)


class TestVoteModel:

    @use_test_database
    def test_create_vote_with_interest(self):
        owner = Pycampista.create(username="pepe")
        voter = Pycampista.create(username="juan")
        project = Project.create(name="Proyecto1", owner=owner)
        vote = Vote.create(
            project=project,
            pycampista=voter,
            interest=True,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )
        assert vote.interest is True

    @use_test_database
    def test_unique_constraint_prevents_duplicate(self):
        owner = Pycampista.create(username="pepe")
        voter = Pycampista.create(username="juan")
        project = Project.create(name="Proyecto1", owner=owner)
        Vote.create(
            project=project,
            pycampista=voter,
            interest=True,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )
        import pytest
        with pytest.raises(peewee.IntegrityError):
            Vote.create(
                project=project,
                pycampista=voter,
                interest=False,
                _project_pycampista_id=f"{project.id}-{voter.id}",
            )

    @use_test_database
    def test_vote_interest_false(self):
        owner = Pycampista.create(username="pepe")
        voter = Pycampista.create(username="juan")
        project = Project.create(name="Proyecto1", owner=owner)
        vote = Vote.create(
            project=project,
            pycampista=voter,
            interest=False,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )
        assert vote.interest is False

    @use_test_database
    def test_vote_interest_null(self):
        owner = Pycampista.create(username="pepe")
        voter = Pycampista.create(username="juan")
        project = Project.create(name="Proyecto1", owner=owner)
        vote = Vote.create(
            project=project,
            pycampista=voter,
            interest=None,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )
        assert vote.interest is None
