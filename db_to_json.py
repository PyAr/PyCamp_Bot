from models import *
import json


projects = Project.select()
project_owners = ProjectOwner.select()

result = {"projects": {}, "responsable_available_slots":{}}

available_slots = [slot.code for slot in Slot.select()]

result["available_slots"] = available_slots

for project in projects:
    votes = list(Vote.select().where(Vote.project == project, Vote.interest))
    responsables = list(ProjectOwner.select().where(ProjectOwner.project == project))
    responsables = [responsable.username for responsable in responsables]
    votes_users = set([v.pycampista.username for v in votes])
    result["projects"][project.name] = {
        "priority_slots": [],
        "difficult_level": project.difficult_level,
        "responsables": responsables,
        "votes": list(votes_users),
    }

all_responsables = set([owner.username for owner in project_owners])
for responsable in all_responsables:
    result["responsable_available_slots"][responsable] = available_slots

with open('cualquiera.json', 'w') as fjson:
    json.dump(result, fjson, indent=2)
