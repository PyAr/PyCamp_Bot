import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

DATA = json.load(open('data.json'))



interested_projects = []
def vote(bot, update):
    for project_name, project in DATA['projects'].items():
    
        keyboard = [[InlineKeyboardButton("Si!", callback_data="si"),
                     InlineKeyboardButton("Nop", callback_data="no")]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
        'Te interesa el proyecto: {}?'.format(project_name),
         reply_markup=reply_markup
                                )

        # query = update.callback_query
        # if query.data == "si":
        #     result = 'Te interesa el proyecto'
        # else:
        #     result = 'No te interesa el proyecto'

    # while vote != 'Y' and vote != 'N':
    #     print('\nI will ask you again')
    #     print('Please insert "Y" if you are interested of "N" if you are not')
    #     vote = input('Are you interested in {}? y/n: '.format(project_name)).upper()

    # if vote == 'Y':
    #     project['votes'].append(user)
    #     interested_projects.append(project_name)


#print('Great! You have finished! These are the projects you are interested in:')

for project in interested_projects:
    print('-', project)

with open('data.json', 'w') as f:
    json.dump(DATA, f, indent=2)
