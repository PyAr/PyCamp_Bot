from datetime import datetime
from pycamp_bot.utils import escape_markdown, get_slot_weekday_name
from pycamp_bot.models import Pycamp
from test.conftest import use_test_database, test_db, MODELS


def setup_module(module):
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()


def teardown_module(module):
    test_db.drop_tables(MODELS)
    test_db.close()


class TestEscapeMarkdown:

    def test_escapes_asterisks(self):
        assert escape_markdown("*bold*") == "\\*bold\\*"

    def test_escapes_underscores(self):
        assert escape_markdown("_italic_") == "\\_italic\\_"

    def test_escapes_all_special_chars(self):
        for char in "_*[]()~`>#+-=|{}.!":
            result = escape_markdown(char)
            assert result == f"\\{char}", f"Failed for char: {char}"

    def test_no_change_on_plain_text(self):
        assert escape_markdown("hello world") == "hello world"

    def test_empty_string(self):
        assert escape_markdown("") == ""

    def test_mixed_text_and_special_chars(self):
        result = escape_markdown("hello *world* (test)")
        assert result == "hello \\*world\\* \\(test\\)"


class TestGetSlotWeekdayName:

    @use_test_database
    def test_first_day_returns_correct_weekday(self):
        # 2024-06-20 es jueves (weekday=3)
        Pycamp.create(
            headquarters="Test",
            init=datetime(2024, 6, 20),
            end=datetime(2024, 6, 23),
            active=True,
        )
        assert get_slot_weekday_name("A") == "Jueves"

    @use_test_database
    def test_second_day_returns_next_weekday(self):
        # 2024-06-20 es jueves, B = viernes
        Pycamp.create(
            headquarters="Test",
            init=datetime(2024, 6, 20),
            end=datetime(2024, 6, 23),
            active=True,
        )
        assert get_slot_weekday_name("B") == "Viernes"

    @use_test_database
    def test_monday_start_offset(self):
        # 2024-06-17 es lunes (weekday=0)
        Pycamp.create(
            headquarters="Test",
            init=datetime(2024, 6, 17),
            end=datetime(2024, 6, 21),
            active=True,
        )
        assert get_slot_weekday_name("A") == "Lunes"
        assert get_slot_weekday_name("B") == "Martes"
        assert get_slot_weekday_name("C") == "Miércoles"
