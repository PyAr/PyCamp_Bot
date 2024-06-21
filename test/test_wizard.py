from datetime import datetime, timedelta
from pycamp_bot.models import Pycamp
from pycamp_bot.commands import wizard
from test.conftest import use_test_database, test_db, MODELS


# ---------------------------
# Module Level Setup/TearDown
# ---------------------------
def setup_module(module):
    """setup any state specific to the execution of the given module."""
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()

def teardown_module(module):
    """teardown any state that was previously setup with a setup_module method."""
    # Not strictly necessary since SQLite in-memory databases only live
    # for the duration of the connection, and in the next step we close
    # the connection...but a good practice all the same.
    test_db.drop_tables(MODELS)

    # Close connection to db.
    test_db.close()
    # If we wanted, we could re-bind the models to their original
    # database here. But for tests this is probably not necessary.


class TestWizardScheduleSlots:

    def init_pycamp(self):
        self.pycamp = Pycamp.create(
            headquarters="Narnia",
            init=datetime(2024,6,20),
            end=datetime(2024,6,24),
        )

    @use_test_database
    def test_correct_number_of_slots_in_one_day(self):
        p = Pycamp.create(
            headquarters="Narnia",
            init=datetime(2024,6,20),
            end=datetime(2024,6,20),
        )
        slots = wizard.compute_wizards_slots(p)
        assert len(slots) == 0
            
    @use_test_database
    def test_correct_number_of_slots_in_three_day(self):
        p = Pycamp.create(
            headquarters="Narnia",
            init=datetime(2024,6,20),
            end=datetime(2024,6,22,23,59,59,99),
        )
        slots = wizard.compute_wizards_slots(p)
        for i in slots:
            print(i)
        assert len(slots) == 20


    @use_test_database
    def test_no_slot_before_first_day_lunch(self):
        self.init_pycamp()
        lunch_time_end = datetime(
            self.pycamp.init.year,
            self.pycamp.init.month,
            self.pycamp.init.day,
            wizard.LUNCH_TIME_END_HOUR
        )
        for (start, end) in wizard.compute_wizards_slots(self.pycamp):
            assert lunch_time_end <= start

    @use_test_database
    def test_no_slot_after_coding_time(self):
        self.init_pycamp()
        for (start, _) in wizard.compute_wizards_slots(self.pycamp):
            assert start.hour < wizard.WIZARD_TIME_END_HOUR

    @use_test_database
    def test_no_slot_before_breakfast(self):
        self.init_pycamp()
        for (start, _) in wizard.compute_wizards_slots(self.pycamp):
            assert start.hour >= wizard.WIZARD_TIME_START_HOUR



    @use_test_database
    def test_no_slot_after_last_day_lunch(self):
        self.init_pycamp()
        lunch_time_end = datetime(
            self.pycamp.end.year,
            self.pycamp.end.month,
            self.pycamp.end.day,
            wizard.LUNCH_TIME_END_HOUR
        )
        for (start, _) in wizard.compute_wizards_slots(self.pycamp):
            print(start)
            if start.day == self.pycamp.end.day:
                assert start >= lunch_time_end


class TestDefineWizardsSchedule:
    pass
