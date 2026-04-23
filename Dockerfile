FROM python:3.10-slim

USER root

# Install git for de /mostrar_version command.
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY . /pycamp/telegram_bot
WORKDIR /pycamp/telegram_bot
RUN pip3 install -U -e '.[dev]'

CMD [ "python", "bin/run_bot.py" ]
