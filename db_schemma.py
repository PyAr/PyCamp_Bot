import sqlite3


def tables_maker(cursor):
    '''creates all tables schema if they don't exist'''
    c = cursor

    # projects table
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        difficult_level INTEGER,
        theme TEXT
    );''')

    # pycampistas table
    c.execute('''CREATE TABLE IF NOT EXISTS pycampistas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    );''')

    # slots table
    c.execute('''CREATE TABLE IF NOT EXISTS slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        when DATETIME
    );''')

    # available_slots table
    c.execute('''CREATE TABLE IF NOT EXISTS available_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pycampista_id INTEGER REFERENCES pycampistas(id) ON UPDATE CASCADE,
        slot_id INTEGER REFERENCES slots(id) ON UPDATE CASCADE
    );''')

    # project_owner table
    c.execute('''CREATE TABLE IF NOT EXISTS project_owner (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER REFERENCES projects(id) ON UPDATE CASCADE,
        pycampista_id INTEGER REFERENCES pycampistas(id) ON UPDATE CASCADE
    );''')

    # votes table
    c.execute('''CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER REFERENCES projects(id) ON UPDATE CASCADE,
        pycampista_id INTEGER REFERENCES pycampistas(id) ON UPDATE CASCADE,
        interest INTEGER
    );''')

    # schedule_slots table
    c.execute('''CREATE TABLE IF NOT EXISTS schedule_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot_id INTEGER REFERENCES slots(id) ON UPDATE CASCADE,
        project_id INTEGER REFERENCES projects(id) ON UPDATE CASCADE
    );''')


def database():
    conn = sqlite3.connect('pycamp_projects.db')
    c = conn.cursor()

    tables_maker(c)

    return conn, c
