import json
from pycamp_bot.models import Project, Slot, Vote


def export_db_2_json():
    projects = Project.select()

    result = {"projects": {}, "responsable_available_slots": {}}

    # Slots de comida no participan del optimizador de proyectos
    available_slots = [
        s.code for s in Slot.select().where(Slot.meal_type.is_null(True))
    ]

    result["available_slots"] = available_slots
    all_responsables = []

    for project in projects:
        votes = list(Vote.select().where(Vote.project == project, Vote.interest))
        # responsables = list(ProjectOwner.select().where(ProjectOwner.project == project))
        # responsables = [responsable.username for responsable in responsables]
        responsables = [project.owner.username]
        if project.owner.username not in all_responsables:
            all_responsables.append(project.owner.username)
        votes_users = set([v.pycampista.username for v in votes])
        result["projects"][project.name] = {
            "priority_slots": [],
            "difficult_level": project.difficult_level,
            "responsables": responsables,
            "votes": list(votes_users),
            "theme": project.topic,
        }

    for responsable in all_responsables:
        result["responsable_available_slots"][responsable] = available_slots

    return result
