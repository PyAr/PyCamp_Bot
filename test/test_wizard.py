from datetime import datetime
from pycamp_bot.models import Pycamp, Pycampista, Slot
from pycamp_bot.commands import wizard
from test.conftest import use_test_database, test_db, MODELS


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


class BaseForOtherWizardsTests:

    def init_pycamp(self):
        self.pycamp = Pycamp.create(
            headquarters="Narnia",
            init=datetime(2024,6,20),
            end=datetime(2024,6,24),
        )


class TestWizardScheduleSlots(BaseForOtherWizardsTests):
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


class TestDefineWizardsSchedule(BaseForOtherWizardsTests):

    # If no wizards, returns {}
    @use_test_database
    def test_no_wizards_then_return_empty_dict(self):
        self.init_pycamp()
        sched = wizard.define_wizards_schedule(self.pycamp)
        assert sched == {}
    
    # all slots are asigned a wizard
    @use_test_database
    def test_all_slots_are_signed_a_wizard(self):
        self.init_pycamp()
        gandalf = Pycampista.create(username="gandalf", wizard=True)
        sched = wizard.define_wizards_schedule(self.pycamp)
        assert all(
            (isinstance(s, Pycampista) and s.wizard) for s in sched.values()
        )

    # Wizards are not asigned to slots when they are busy
    @use_test_database
    def test_all_slots_are_signed_a_wizard(self):
        self.init_pycamp()
        gandalf = Pycampista.create(username="gandalf", wizard=True)
        merlin = Pycampista.create(username="merlin", wizard=True)
        for h in [9, 10, 11, 12]:
            # Create 3 slots where Gandalf is busy
            Slot.create(
                code = "A1", 
                start=datetime(2024, 6, 21, h, 30, 0),
                current_wizard=gandalf
            )
        sched = wizard.define_wizards_schedule(self.pycamp)
        # Verify Gandalf is not assigned to slots where he is busy
        for (ini, end), w in sched.items():
            if gandalf.is_busy(ini, end):
                print(ini, end, w.username)
                assert w != gandalf

    # If all wizards are busy in a slot, then one is asigned all the same
    @use_test_database
    def test_all_slots_are_signed_a_wizard(self):
        self.init_pycamp()
        gandalf = Pycampista.create(username="gandalf", wizard=True)
        merlin = Pycampista.create(username="merlin", wizard=True)
        for h in [9, 10, 11, 12]:
            # Create 3 slots where Gandalf AND Merlin are busy
            Slot.create(
                code = "A1", 
                start=datetime(2024, 6, 21, h, 30, 0),
                current_wizard=gandalf
            )
            Slot.create(
                code = "A1", 
                start=datetime(2024, 6, 21, h, 30, 0),
                current_wizard=merlin
            )
        sched = wizard.define_wizards_schedule(self.pycamp)

        assert all(
            (isinstance(s, Pycampista) and s.wizard) for s in sched.values()
        )

class TestListWizards(BaseForOtherWizardsTests):

    @use_test_database
    def test_wizard_registration(self):
        self.init_pycamp()
        w = self.pycamp.add_wizard("Gandalf", 123)
        wizards = self.pycamp.get_wizards()
        assert len(wizards) == 1
        assert w.username == wizards[0].username


    @use_test_database
    def test_wizard_registration_works_in_one_pycamp_only(self):
        self.init_pycamp()
        self.pycamp.add_wizard("Gandalf", 123)
        
        other_pycamp = Pycamp.create(
            headquarters="Mordor",
            init=datetime(2025,3,22),
            end=datetime(2025,3,24),
        )
        w = other_pycamp.add_wizard("Merlin", 456)
        #import ipdb; ipdb.set_trace()
        results = other_pycamp.get_wizards()
        assert len(results) == 1
        assert w.username == results[0].username


    # @use_test_database
    # def test_no_active_pycamp_then_fail(self):
    #     self.init_pycamp()
    #     agregarle un mago
        
    #     creo OTRO Pycamp
    #     agregarle otro mago

    #     pedir listado: check está el OTRO mago solamente