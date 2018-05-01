from bot import bot, update

def projects(bot, update):
    """Prevent people for keep uploading projects"""
    projects = Project.select()
    text = []
    for project in projects:
        owners = map(lambda po: po.owner.username, project.projectowner_set.iterator())
        project_text = "{} \n owner: {} \n topic: {} \n level: {}".format(
            project.name,
            ', '.join(owners),
            project.topic,
            project.difficult_level
        )
        text.append(project_text)

    text = "\n\n".join(text)

    update.message.reply_text(text)