import datetime as dt
from pycamp_bot.models import Pycamp
from pycamp_bot.commands.manage_pycamp import get_pycamp_by_name, get_active_pycamp
from test.conftest import use_test_database, test_db, MODELS


def setup_module(module):
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()


def teardown_module(module):
    test_db.drop_tables(MODELS)
    test_db.close()


class TestGetPycampByName:

    @use_test_database
    def test_returns_pycamp_when_exists(self):
        Pycamp.create(headquarters="Narnia")
        result = get_pycamp_by_name("Narnia")
        assert result is not None
        assert result.headquarters == "Narnia"

    @use_test_database
    def test_returns_none_when_not_exists(self):
        result = get_pycamp_by_name("Inexistente")
        assert result is None

    @use_test_database
    def test_finds_correct_pycamp_among_many(self):
        Pycamp.create(headquarters="Narnia")
        Pycamp.create(headquarters="Mordor")
        result = get_pycamp_by_name("Mordor")
        assert result.headquarters == "Mordor"


class TestGetActivePycamp:

    @use_test_database
    def test_returns_false_none_when_no_active(self):
        Pycamp.create(headquarters="Narnia", active=False)
        is_active, pycamp = get_active_pycamp()
        assert is_active is False
        assert pycamp is None

    @use_test_database
    def test_returns_true_pycamp_when_active(self):
        Pycamp.create(headquarters="Narnia", active=True)
        is_active, pycamp = get_active_pycamp()
        assert is_active is True
        assert pycamp.headquarters == "Narnia"

    @use_test_database
    def test_returns_false_none_when_no_pycamps(self):
        is_active, pycamp = get_active_pycamp()
        assert is_active is False
        assert pycamp is None

    @use_test_database
    def test_inactive_pycamp_not_returned(self):
        Pycamp.create(headquarters="Narnia", active=False)
        Pycamp.create(headquarters="Mordor", active=False)
        is_active, pycamp = get_active_pycamp()
        assert is_active is False


class TestPycampDurationCalculation:

    @use_test_database
    def test_duration_one_day(self):
        p = Pycamp.create(
            headquarters="Test",
            init=dt.datetime(2024, 6, 20),
            active=True,
        )
        duration = 1
        p.end = p.init + dt.timedelta(
            days=duration - 1,
            hours=23,
            minutes=59,
            seconds=59,
            milliseconds=99,
        )
        p.save()
        # Con duración 1 día, init y end deben ser el mismo día
        assert p.end.date() == p.init.date()

    @use_test_database
    def test_duration_four_days(self):
        p = Pycamp.create(
            headquarters="Test",
            init=dt.datetime(2024, 6, 20),
            active=True,
        )
        duration = 4
        p.end = p.init + dt.timedelta(
            days=duration - 1,
            hours=23,
            minutes=59,
            seconds=59,
            milliseconds=99,
        )
        p.save()
        # 4 días desde el 20: 20, 21, 22, 23 -> end el 23
        assert p.end.day == 23
        assert p.end.hour == 23
        assert p.end.minute == 59
