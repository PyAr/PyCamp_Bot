from datetime import datetime
from freezegun import freeze_time
from pycamp_bot.models import Pycamp, Pycampista, WizardAtPycamp
from pycamp_bot.commands import wizard
from test.conftest import use_test_database, test_db, MODELS


# ---------------------------
# Module Level Setup/TearDown
# ---------------------------
def setup_module(module):
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()

def teardown_module(module):
    # Not strictly necessary since SQLite in-memory databases only live
    # for the duration of the connection, and in the next step we close
    # the connection...but a good practice all the same.
    test_db.drop_tables(MODELS)

    # Close connection to db.
    test_db.close()
    # If we wanted, we could re-bind the models to their original
    # database here. But for tests this is probably not necessary.


class TestPycampGetCurrentWizard:

    def init_pycamp(self):
        self.pycamp = Pycamp.create(
            headquarters="Narnia",
            init=datetime(2024, 6, 20),
            end=datetime(2024, 6, 24),
        )

    @use_test_database
    @freeze_time("2024-06-21 15:30:00")
    def test_returns_correct_wizard_within_its_turno(self):
        """Integration test using persist_wizards_schedule_in_db."""
        p = Pycamp.create(
            headquarters="Narnia",
            init=datetime(2024,6,20),
            end=datetime(2024,6,23),
        )
        pycamper = p.add_wizard("pepe", 123)
        wizard.persist_wizards_schedule_in_db(p)

        assert p.get_current_wizard() == pycamper
            
    @use_test_database
    def test_no_scheduled_wizard_then_return_none(self):
        p = Pycamp.create(
            headquarters="Narnia"
        )
        # Wizard exists, but no time scheduled.
        pycamper = Pycampista.create(username="pepe", wizard=True)
        assert WizardAtPycamp.select().count() == 0

        assert p.get_current_wizard() is None

    @use_test_database
    @freeze_time("2024-06-21 15:30:00")
    def test_many_scheduled_wizard_then_return_one_of_them(self):
        p = Pycamp.create(
            headquarters="Narnia",
            init=datetime(2024,6,20),
            end=datetime(2024,6,23),
        )        
        w1 = p.add_wizard("gandalf", 123)
        w2 = p.add_wizard("merlin", 456 )
        wizard.persist_wizards_schedule_in_db(p)
        w = p.get_current_wizard()
        
        assert w == w1 or w == w2
