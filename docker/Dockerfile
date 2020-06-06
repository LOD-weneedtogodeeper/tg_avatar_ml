FROM python:3.7-slim

MAINTAINER Alex Karavaev


RUN pip3 install \
      python-telegram-bot \
      requests 

COPY src /var/local/bot
WORKDIR  /var/local/bot

CMD [ "python3", "/var/local/bot/bot.py" ]
