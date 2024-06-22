def escape_markdown(string):
    # See: https://core.telegram.org/bots/api#markdownv2-style

    new_string = string

    for char in "_*[]()~`>#+-=|{}.!":
        new_string = new_string.replace(char, f'\\{char}')

    return new_string
