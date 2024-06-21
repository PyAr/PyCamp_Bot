import os

from datetime import datetime
from functools import wraps
from peewee import SqliteDatabase
import pytest
from telegram import Bot

from pycamp_bot.models import Pycampista, Slot, Pycamp, WizardAtPycamp



bot = Bot(token=os.environ['TOKEN'])


# use an in-memory SQLite for tests.
test_db = SqliteDatabase(':memory:')

MODELS = [Pycampista, Slot, Pycamp, WizardAtPycamp]


# Bind the given models to the db for the duration of wrapped block.
def use_test_database(fn):
    @wraps(fn)
    def inner(self):
        with test_db.bind_ctx(MODELS):
            test_db.create_tables(MODELS)
            try:
                fn(self)
            finally:
                test_db.drop_tables(MODELS)
    return inner


TEST_INIT_DATE = datetime(2024, 6, 20, 0, 0, 0)
TEST_END_DATE = datetime(2024, 6, 24, 23, 59, 59, 99999)
