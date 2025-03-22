from pycamp_bot.models import Pycamp

def escape_markdown(string):
    # See: https://core.telegram.org/bots/api#markdownv2-style

    new_string = string

    for char in "_*[]()~`>#+-=|{}.!":
        new_string = new_string.replace(char, f'\\{char}')

    return new_string


def get_slot_weekday_name(slot_day_code):
    ISO_WEEKDAY_NAMES = {
        0: 'Lunes',
        1: 'Martes',
        2: 'Miércoles',
        3: 'Jueves',
        4: 'Viernes',
        5: 'Sábado',
        6: 'Domingo',
    }

    pycamp_start_weekday = Pycamp.get(Pycamp.active == True).init.weekday()

    # Convert slot day code to a zero-based code, to use it as an
    # offset to get the weekday name of the slot
    offset = ord(slot_day_code) - ord('A')
    day_name = ISO_WEEKDAY_NAMES[pycamp_start_weekday + offset]

    return day_name
