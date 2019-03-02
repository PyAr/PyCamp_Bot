from bot import bot, update

def define_slots(bot, update, args):
    if not is_auth(bot, update.message.from_user.username):
        return

    if not is_pycamp_started:
        return

    try:
        slot_code, slot_time = args
        letter = slot_code[0].lower()
        if letter not in ["a","b","c","d"]:
            raise
    except:
        bot.send_message(
        chat_id="me pasaste mal los argumentos, recatate",
        text=args
        )
    days_added = {"a": 0, "b": 1, "c": 2, "d": 3}
    days_to_add = timedelta(days=days_added[letter])

    slot_date = datetime(
        year=date_start_pycamp.year,
        month=date_start_pycamp.month,
        day=date_start_pycamp.day,
        hour=int(slot_time)
        ) + days_to_add

    slot = Slot(code=slot_code,start=slot_date)
    slot.save()
    
