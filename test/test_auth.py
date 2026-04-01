from pycamp_bot.models import Pycampista
from pycamp_bot.commands.auth import get_admins_username
from test.conftest import use_test_database, test_db, MODELS


def setup_module(module):
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()


def teardown_module(module):
    test_db.drop_tables(MODELS)
    test_db.close()


class TestGetAdminsUsername:

    @use_test_database
    def test_returns_empty_when_no_admins(self):
        Pycampista.create(username="pepe", admin=False)
        assert get_admins_username() == []

    @use_test_database
    def test_returns_admin_usernames(self):
        Pycampista.create(username="admin1", admin=True)
        result = get_admins_username()
        assert result == ["admin1"]

    @use_test_database
    def test_excludes_non_admin_users(self):
        Pycampista.create(username="admin1", admin=True)
        Pycampista.create(username="user1", admin=False)
        result = get_admins_username()
        assert "admin1" in result
        assert "user1" not in result

    @use_test_database
    def test_multiple_admins(self):
        Pycampista.create(username="admin1", admin=True)
        Pycampista.create(username="admin2", admin=True)
        Pycampista.create(username="user1", admin=False)
        result = get_admins_username()
        assert len(result) == 2
        assert "admin1" in result
        assert "admin2" in result

    @use_test_database
    def test_admin_with_null_flag(self):
        Pycampista.create(username="pepe", admin=None)
        result = get_admins_username()
        assert result == []

    @use_test_database
    def test_no_users_returns_empty(self):
        result = get_admins_username()
        assert result == []
