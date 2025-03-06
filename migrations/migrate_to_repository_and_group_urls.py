# https://docs.peewee-orm.com/en/latest/peewee/playhouse.html#schema-migrations

import peewee
import playhouse.migrate

import pycamp_bot.models


my_db = peewee.SqliteDatabase('pycamp_projects.db')
migrator = playhouse.migrate.SqliteMigrator(my_db)


playhouse.migrate.migrate(
    migrator.add_column(
        pycamp_bot.models.Project._meta.table_name, 
        'repository_url', 
        pycamp_bot.models.Project.repository_url,
    ),
    migrator.add_column(
        pycamp_bot.models.Project._meta.table_name, 
        'group_url', 
        pycamp_bot.models.Project.group_url,
    ),
)
