from models import *
import json


projects = Project.select()

result = {"projects": {}, "responsable_available_slots":{}}

result["available_slots"] = [
    "A1",
    "A2",
    "B1",
    "B2",
    "B3",
    "B4",
    "B5",
    "C1",
    "C2",
    "C3",
    "C4",
    "C5",
    "D1",
    "D2"
]


for n, p in enumerate(projects):
    votes = list(Vote.select().where(Vote.project_id == p.id & Vote.interest))
    votes_users = set([v.pycampista.username for v in votes])
    result["projects"][p.name] = {
        "priority_slots": [],
        "difficult_level": p.difficult_level,
        "responsable": [n],
        "votes": list(votes_users),
    }
    result["responsable_available_slots"][n] = result["available_slots"]

with open('cualquiera.json', 'w') as fjson:
    json.dump(result, fjson, indent=2)
