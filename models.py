import peewee as pw


db = pw.SqliteDatabase('pycamp_projects.db')


class Pycampista(pw.Model):
    username = pw.CharField(unique=True)
    chat_id = pw.CharField(unique=True)
    arrive = pw.DateTimeField(null=True)
    leave = pw.DateTimeField(null=True)

    class Meta:
        database = db


class Slot(pw.Model):
    code = pw.CharField()  # For example A1 for first slot first day
    start = pw.DateTimeField()

    class Meta:
        database = db


class Project(pw.Model):
    name = pw.CharField()
    difficult_level = pw.IntegerField(default=1)  # From 1 to 3
    theme = pw.CharField(null=True)
    slot = pw.ForeignKeyField(Slot, null=True)

    class Meta:
        database = db


class ProjectOwner(pw.Model):
    project = pw.ForeignKeyField(Project)
    owner = pw.ForeignKeyField(Pycampista)

    class Meta:
        database = db
        primary_key = pw.CompositeKey('project', 'owner')


class Vote(pw.Model):
    project = pw.ForeignKeyField(Project)
    pycampista = pw.ForeignKeyField(Pycampista)
    interest = pw.BooleanField()

    class Meta:
        database = db


db.connect()
db.create_tables([Pycampista, Project, Slot, ProjectOwner, Vote])
