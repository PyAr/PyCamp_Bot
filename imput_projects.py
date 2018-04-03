# -*- coding: utf-8 -*-
import json
from pprint import pprint

# loads the data from an existing .json into a dictiorary
data = json.load(open('data.json'))
   
    #given a certain boolean question loops you in until your answer is valid

def insert_proyect(update):

    def checkYesNo(question):
        update.message.reply_text(question + "  ".lower())
        resp = str(update.message.text).lower
        while resp != "si" and resp != "no":
            update.message.reply_text("Por favor responde con 'Si' o 'No'  ")
            update.message.reply_text(question)
            resp = str(update.message.text).lower
        return resp
    
    update.message.reply_text("¿Cuál es tu nombre?")
    user_name = str(update.message.text).lower
     
    update.message.reply_text("Ingresá el Nombre del Proyecto a proponer")
    project_name = str(update.message.text).lower

    # data['projects'][project_name] = {}
    # resp_check = 0
    # while resp_check not in range(1, 11):
    #     resp_check = input("Ingresá el grado de dificultad del proyecto (1-10  ")
    #     if resp_check.isnumeric():
    #         resp_check = int(resp_check)

    #data['projects'][project_name]['difficult_level'] = resp_check

    resp_check = checkYesNo("Sos el responsable de este proyecto? Si/No  ")
    print (resp_check)

    if resp_check == "si":
        
        data['projects'][project_name]['responsables'] = [user_name, ]

    elif resp_check == "no":

        update.message.reply_text("Por favor ingresa el nombre del responsable")
        project_resp = str(update.message.text).lower
        data['projects'][project_name]['responsables'] = project_resp

    resp_check = checkYesNo("¿Hay otrx responsable del proyecto? Si/No")

    while resp_check == "si":

        update.message.reply_text("Ingresá el nombre de la persona responsable")
        resp_check = str(update.message.text).lower
        data['projects'][project_name]['responsables'].append(resp_check)
        
    resp_check = checkYesNo("¿Hay otrx responsable del proyecto? Si/No")
    
    print ("La información fue cargada correctamente")
    print ("Gracias!")

with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)