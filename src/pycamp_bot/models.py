import peewee as pw

from datetime import datetime, timedelta
from random import choice


DEFAULT_SLOT_PERIOD = 60  # Minutos

db = pw.SqliteDatabase('pycamp_projects.db')


class BaseModel(pw.Model):
    class Meta:
        database = db


class Pycampista(BaseModel):
    '''
    Representation of the pycamp user
    username: name on telegram (ex. roberto for @roberto)
    chat_id: number in string format
    arrive: time of arrival
    leave: time of departure
    wizard: True or False for is a wizard
    admin: True or False for admin privileges
    '''
    username = pw.CharField(unique=True)
    chat_id = pw.CharField(unique=True, null=True)
    arrive = pw.DateTimeField(null=True)
    leave = pw.DateTimeField(null=True)
    wizard = pw.BooleanField(null=True)
    admin = pw.BooleanField(null=True)

    def __str__(self):
        rv_str = 'Pycampista:\n'
        for attr in ['username', 'arrive', 'leave']:
            rv_str += f'{attr}: {getattr(self, attr)}\n'
        rv_str += 'Wizard on!' if self.wizard else 'Muggle'
        rv_str += '\n'
        rv_str += 'Admin' if self.admin else 'Commoner'
        return rv_str

    def is_busy(self, from_time, to_time):
        """`from_time, to_time` are two datetime objects."""
        project_presentation_slots = Slot.select().where(Slot.current_wizard == self)
        for slot in project_presentation_slots:
            # https://stackoverflow.com/a/13403827/1161156
            latest_start = max(from_time, slot.start)
            earliest_end = min(to_time, slot.get_end_time())
            if latest_start <= earliest_end:  # Overlap
                return True
        return False


class Pycamp(BaseModel):
    '''
    Representation of the pycamp
    headquartes: headquarters name
    init: time of init
    end: time of end
    vote_authorized: the vote is auth in this pycamp
    project_load_authorized: the project load is auth in this pycamp
    active: boolean telling wheter this PyCamp instance is active (or an old one)
    wizard_slot_duration: config to compute the schedule of mages
    '''
    headquarters = pw.CharField(unique=True)
    init = pw.DateTimeField(null=True)
    end = pw.DateTimeField(null=True)
    vote_authorized = pw.BooleanField(default=False, null=True)
    project_load_authorized = pw.BooleanField(default=False, null=True)
    active = pw.BooleanField(default=False, null=True)
    wizard_slot_duration = pw.IntegerField(default=60, null=False)  # In minutes

    def __str__(self):
        rv_str = 'Pycamp:\n'
        for attr in ['headquarters', 'init', 'end', 'active',
                     'vote_authorized', 'project_load_authorized']:
            rv_str += f'{attr}: {getattr(self, attr)}\n'
        return rv_str

    def set_as_only_active(self):
        active = Pycamp.select().where(Pycamp.active)
        for p in active:
            p.active = False
        Pycamp.bulk_update(active, fields=[Pycamp.active])
        self.active = True
        self.save()

    def get_wizards(self):
        return Pycampista.select().where(Pycampista.wizard == 1)

    def get_current_wizard(self):
        """Return the Pycampista instance that's the currently scheduled wizard."""
        now = datetime.now()
        current_wizards = WizardAtPycamp.select().where(  
            (WizardAtPycamp.pycamp == self) & 
            (WizardAtPycamp.init <= now) &
            (WizardAtPycamp.end > now) 
        )

        wizard = None  # Default if n_wiz == 0
        if current_wizards.count() >= 1:
            # Ready for an improbable future where we'll have many concurrent wizards ;-)
            wizard = choice(current_wizards).wizard
        
        return wizard


    def clear_wizards_schedule(self):
        return WizardAtPycamp.delete().where(WizardAtPycamp.pycamp == self).execute()

class PycampistaAtPycamp(BaseModel):
    '''
    Many to many relationship. Ona pycampista will attend many pycamps. A
    pycamps will have many pycampistas
    '''
    pycamp = pw.ForeignKeyField(Pycamp)
    pycampista = pw.ForeignKeyField(Pycampista)


class WizardAtPycamp(BaseModel):
    '''
    Many to many relationship. Ona pycampista will attend many pycamps. A
    pycamps will have many pycampistas
    '''
    pycamp = pw.ForeignKeyField(Pycamp)
    wizard = pw.ForeignKeyField(Pycampista)
    init = pw.DateTimeField()
    end = pw.DateTimeField()


class Slot(BaseModel):
    '''
    Time slot representation
    code: String that represent the slot in the form A1, where the letter
    represents the day and the number the position of the slot that day.
    start: Time of start of the slot
    '''
    code = pw.CharField()  # For example A1 for first slot first day
    start = pw.DateTimeField()
    current_wizard = pw.ForeignKeyField(Pycampista, null=True)

    def get_end_time(self):
        return self.start + timedelta(minutes=DEFAULT_SLOT_PERIOD)


class Project(BaseModel):
    '''
    Project representation
    name: name of the project
    difficult_level: difficult level between 1 and 3
    topic: string comma separated with the pertinences
    slot: ForeignKey with the slot asigned
    owner: ForeignKey with the pycamp user asigned
    '''
    name = pw.CharField(unique=True)
    difficult_level = pw.IntegerField(default=1)
    topic = pw.CharField(null=True)
    slot = pw.ForeignKeyField(Slot, null=True)
    owner = pw.ForeignKeyField(Pycampista)
    repository_url = pw.CharField(null=True)


class Vote(BaseModel):
    '''
    Vote representation. Relation many to many
    project: ForeignKey project
    pycampista: ForeignKey pycampista
    interest: True or False for interest in the project. None repesents no
    vote.
    '''
    project = pw.ForeignKeyField(Project)
    pycampista = pw.ForeignKeyField(Pycampista)
    interest = pw.BooleanField(null=True)
    # this field is to prevent saving multi votes from the same user in the
    # same project
    _project_pycampista_id = pw.CharField(unique=True)


def models_db_connection():
    db.connect()
    db.create_tables([
        Pycamp,
        Pycampista,
        PycampistaAtPycamp,
        WizardAtPycamp,
        Project,
        Slot,
        Vote], safe=True)
    db.close()
