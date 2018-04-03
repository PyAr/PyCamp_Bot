import json


DATA = json.load(open('data.json'))

user = input('Enter your name: ')

interested_projects = []


for project_name, project in DATA['projects'].items():
    vote = input('\nAre you interested in {}? y/n: '.format(project_name)).upper()

    while vote != 'Y' and vote != 'N':
        print('\nI will ask you again')
        print('Please insert "Y" if you are interested of "N" if you are not')
        vote = input('Are you interested in {}? y/n: '.format(project_name)).upper()

    if vote == 'Y':
        project['votes'].append(user)
        interested_projects.append(project_name)


print('Great! You have finished! These are the projects you are interested in:')

for project in interested_projects:
    print('-', project)

with open('data.json', 'w') as f:
    json.dump(DATA, f, indent=2)
