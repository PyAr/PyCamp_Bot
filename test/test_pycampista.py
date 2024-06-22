from datetime import datetime, timedelta
from pycamp_bot.models import Pycampista, Slot
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


class TestPycampistaIsBusy:

    @use_test_database
    def test_return_true_if_assigned_in_slot_equal_to_target_period(self):
        pycamper = Pycampista.create(username="pepe")
        slot = Slot.create(code = "A1", start=datetime.now(), current_wizard=pycamper)
        period = (slot.start, slot.get_end_time())
        assert pycamper.is_busy(*period)

    @use_test_database
    def test_return_true_if_assigned_in_slot_starting_at_target_period(self):
        pycamper = Pycampista.create(username="pepe")
        slot_start = datetime.now()
        Slot.create(code = "A1", start=slot_start, current_wizard=pycamper)
        period = (slot_start, slot_start + timedelta(minutes=5))
        assert pycamper.is_busy(*period)

    @use_test_database
    def test_return_true_if_assigned_in_slot_around_target_period(self):
        pycamper = Pycampista.create(username="pepe")
        slot_start = datetime.now()
        Slot.create(code = "A1", start=slot_start, current_wizard=pycamper)
        period_start = slot_start + timedelta(minutes=5)
        period = (period_start, period_start + timedelta(minutes=10))
        assert pycamper.is_busy(*period)

    @use_test_database
    def test_return_true_if_assigned_in_slot_ending_after_target_period_starts(self):
        pycamper = Pycampista.create(username="pepe")
        slot = Slot.create(code = "A1", start=datetime.now(), current_wizard=pycamper)
        period = (
            slot.start + timedelta(minutes=5), 
            slot.get_end_time() + timedelta(minutes=5), 
        )
        assert pycamper.is_busy(*period)

    @use_test_database
    def test_return_true_if_assigned_in_slot_starting_before_target_period_ends(self):
        pycamper = Pycampista.create(username="pepe")
        slot = Slot.create(code = "A1", start=datetime.now(), current_wizard=pycamper)
        period = (
            slot.start - timedelta(minutes=5), 
            slot.start + timedelta(minutes=5), 
        )
        assert pycamper.is_busy(*period)

    @use_test_database
    def test_return_false_if_assigned_in_slot_ending_before_target_period_starts(self):
        pycamper = Pycampista.create(username="pepe")
        slot = Slot.create(code = "A1", start=datetime.now(), current_wizard=pycamper)
        period = (
            slot.get_end_time() + timedelta(seconds=1),
            slot.get_end_time() + timedelta(seconds=10),
        )
        assert not pycamper.is_busy(*period)

    @use_test_database
    def test_return_false_if_assigned_in_slot_start_after_target_period_ends(self):
        pycamper = Pycampista.create(username="pepe")
        slot = Slot.create(code = "A1", start=datetime.now(), current_wizard=pycamper)
        period = (
            slot.start - timedelta(seconds=10),
            slot.start - timedelta(seconds=1),
        )
        assert not pycamper.is_busy(*period)
