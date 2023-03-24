import peewee as pw


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


class Pycamp(BaseModel):
    '''
    Representation of the pycamp
    headquartes: headquarters name
    init: time of init
    end: time of end
    vote_authorized: the vote is auth in this pycamp
    project_load_authorized: the project load is auth in this pycamp
    '''
    headquarters = pw.CharField(unique=True)
    init = pw.DateTimeField(null=True)
    end = pw.DateTimeField(null=True)
    vote_authorized = pw.BooleanField(default=False, null=True)
    project_load_authorized = pw.BooleanField(default=False, null=True)
    active = pw.BooleanField(default=False, null=True)

    def __str__(self):
        rv_str = 'Pycamp:\n'
        for attr in ['headquarters', 'init', 'end', 'active',
                     'vote_authorized', 'project_load_authorized']:
            rv_str += f'{attr}: {getattr(self, attr)}\n'
        return rv_str


class PycampistaAtPycamp(BaseModel):
    '''
    Many to many relationship. Ona pycampista will attend many pycamps. A
    pycamps will have many pycampistas
    '''
    pycamp = pw.ForeignKeyField(Pycamp)
    pycampista = pw.ForeignKeyField(Pycampista)


class Slot(BaseModel):
    '''
    Time slot representation
    code: String that represent the slot in the form A1, where the letter
    represents the day and the number the position of the slot that day.
    start: Time of start of the slot
    '''
    code = pw.CharField()  # For example A1 for first slot first day
    start = pw.DateTimeField()
    current_wizzard = pw.ForeignKeyField(Pycampista)


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
        Project,
        Slot,
        Vote])
