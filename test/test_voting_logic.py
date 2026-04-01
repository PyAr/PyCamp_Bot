import peewee
import pytest
from pycamp_bot.models import Pycampista, Project, Vote
from test.conftest import use_test_database, test_db, MODELS


def setup_module(module):
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()


def teardown_module(module):
    test_db.drop_tables(MODELS)
    test_db.close()


class TestVoteCreation:

    @use_test_database
    def test_create_vote_with_interest_true(self):
        owner = Pycampista.create(username="owner1")
        voter = Pycampista.create(username="voter1")
        project = Project.create(name="Proyecto1", owner=owner)
        vote = Vote.create(
            project=project,
            pycampista=voter,
            interest=True,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )
        assert vote.interest is True
        assert vote.project.name == "Proyecto1"

    @use_test_database
    def test_create_vote_with_interest_false(self):
        owner = Pycampista.create(username="owner1")
        voter = Pycampista.create(username="voter1")
        project = Project.create(name="Proyecto1", owner=owner)
        vote = Vote.create(
            project=project,
            pycampista=voter,
            interest=False,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )
        assert vote.interest is False

    @use_test_database
    def test_duplicate_vote_raises_integrity_error(self):
        owner = Pycampista.create(username="owner1")
        voter = Pycampista.create(username="voter1")
        project = Project.create(name="Proyecto1", owner=owner)
        Vote.create(
            project=project,
            pycampista=voter,
            interest=True,
            _project_pycampista_id=f"{project.id}-{voter.id}",
        )
        with pytest.raises(peewee.IntegrityError):
            Vote.create(
                project=project,
                pycampista=voter,
                interest=False,
                _project_pycampista_id=f"{project.id}-{voter.id}",
            )

    @use_test_database
    def test_project_pycampista_id_format(self):
        owner = Pycampista.create(username="owner1")
        voter = Pycampista.create(username="voter1")
        project = Project.create(name="Proyecto1", owner=owner)
        expected_id = f"{project.id}-{voter.id}"
        vote = Vote.create(
            project=project,
            pycampista=voter,
            interest=True,
            _project_pycampista_id=expected_id,
        )
        assert vote._project_pycampista_id == expected_id


class TestVoteCount:

    @use_test_database
    def test_count_unique_voters(self):
        owner = Pycampista.create(username="owner1")
        voter1 = Pycampista.create(username="voter1")
        voter2 = Pycampista.create(username="voter2")
        project = Project.create(name="Proyecto1", owner=owner)

        Vote.create(project=project, pycampista=voter1, interest=True,
                     _project_pycampista_id=f"{project.id}-{voter1.id}")
        Vote.create(project=project, pycampista=voter2, interest=True,
                     _project_pycampista_id=f"{project.id}-{voter2.id}")

        votes = [vote.pycampista_id for vote in Vote.select()]
        assert len(set(votes)) == 2

    @use_test_database
    def test_count_zero_when_no_votes(self):
        votes = [vote.pycampista_id for vote in Vote.select()]
        assert len(set(votes)) == 0

    @use_test_database
    def test_count_deduplicates_same_user_multiple_projects(self):
        owner = Pycampista.create(username="owner1")
        voter = Pycampista.create(username="voter1")
        p1 = Project.create(name="Proyecto1", owner=owner)
        p2 = Project.create(name="Proyecto2", owner=owner)

        Vote.create(project=p1, pycampista=voter, interest=True,
                     _project_pycampista_id=f"{p1.id}-{voter.id}")
        Vote.create(project=p2, pycampista=voter, interest=True,
                     _project_pycampista_id=f"{p2.id}-{voter.id}")

        votes = [vote.pycampista_id for vote in Vote.select()]
        # Mismo usuario votó 2 veces, pero unique count es 1
        assert len(votes) == 2
        assert len(set(votes)) == 1
