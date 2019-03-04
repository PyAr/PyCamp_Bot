import peewee as pw


db = pw.SqliteDatabase('pycamp_projects.db')


class BotStatus(pw.Model):
    '''
    Status of the pycamp bot
    vote_autorized: the votation is autorized
    '''
    vote_authorized = pw.BooleanField(null=True)
    proyect_load_authorized = pw.BooleanField(null=True)

    class Meta:
        database = db


class Pycampista(pw.Model):
    '''
    Representation of the pycamp user
    username: name on telegram (ex. roberto for @roberto)
    chat_id: number in string format
    arrive: time of arrival
    leave: time of departure
    wizard: True or False for is a wizard
    '''
    username = pw.CharField(unique=True)
    chat_id = pw.CharField(unique=True)
    arrive = pw.DateTimeField(null=True)
    leave = pw.DateTimeField(null=True)
    wizard = pw.BooleanField(null=True)

    class Meta:
        database = db


class Slot(pw.Model):
    '''
    Time slot representation
    code: String that represent the slot in the form A1, where the letter
    represents the day and the number the position of the slot that day.
    start: Time of start of the slot
    '''
    code = pw.CharField()  # For example A1 for first slot first day
    start = pw.DateTimeField()

    class Meta:
        database = db


class Project(pw.Model):
    '''
    Project representation
    name: name of the project
    difficult_level: difficult level between 1 and 3
    topic: string comma separated with the pertinences
    slot: ForeignKey with the slot asigned
    owner: ForeignKey with the pycamp user asigned
    '''
    name = pw.CharField()
    difficult_level = pw.IntegerField(default=1)
    topic = pw.CharField(null=True)
    slot = pw.ForeignKeyField(Slot, null=True)
    owner = pw.ForeignKeyField(Pycampista)

    class Meta:
        database = db


class Vote(pw.Model):
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
    #this field is to prevent saving multi votes from the same user in the
    # same project
    _project_pycampista_id = pw.CharField(unique=True)

    class Meta:
        database = db


def models_db_connection(initialize=False):
    db.connect()
    if initialize:
        db.create_tables([BotStatus, Pycampista, Project, Slot, Vote])
        base_status = BotStatus.create(
                            vote_authorized=False,
                            proyect_load_authorized=False
                            )
        base_status.save()
