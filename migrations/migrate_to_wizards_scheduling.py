# https://docs.peewee-orm.com/en/latest/peewee/playhouse.html#schema-migrations

from datetime import datetime, timedelta
from playhouse.migrate import *
import peewee as pw

from pycamp_bot.models import Pycampista, Slot, Pycamp


my_db = pw.SqliteDatabase('pycamp_projects.db')
migrator = SqliteMigrator(my_db)

from pycamp_bot.models import Pycamp


migrate(
    migrator.add_column(  # wizard_slot_duration = pw.IntegerField(default=60, null=False)
        Pycamp._meta.table_name, 
        'wizard_slot_duration', 
        Pycamp.wizard_slot_duration
    ),
    migrator.add_column(  # current_wizard = pw.ForeignKeyField(Pycampista)
        Slot._meta.table_name, 
        'current_wizard_id', 
        Slot.current_wizard
    ),
)

p = Pycamp.get()
p.end = datetime(2024,6,23,23,59,59,99)
p.end = datetime(2024,6,23,23,59,59,999999)
p.save()

