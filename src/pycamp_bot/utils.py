from pycamp_bot.models import Pycamp
from pycamp_bot.logger import logger


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
def active_pycamp_needed(f):
    from pycamp_bot.commands.manage_pycamp import get_active_pycamp
    async def wrap(*args, **kargs):
        update, context = args

        _, pycamp = get_active_pycamp()
        if pycamp is None:
            msg = "🔥 %s: This operation (%s) needs an active PyCamp. Talk to an admin." % (
                update.message.from_user.username, str(f.__name__)
            )
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=msg)
            logger.warning(msg)
            return

        return await f(*args, pycamp=pycamp)
    return wrap
