FROM python:3.8

USER root

COPY . /pycamp/telegram_bot
WORKDIR /pycamp/telegram_bot
RUN pip3 install -U .

CMD [ "python", "bin/run_bot.py" ]
