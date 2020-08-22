FROM docker.io/fedora

ENV MESSAGE_UTILITY_BOT_DISCORD_TOKEN=YOUR_BOT_TOKEN

RUN dnf install python3 python3-pip git -y
RUN python3 -m pip install discord requests

COPY ./message_utility_bot.py /init
RUN chmod +x /init

CMD ["/init", "--configpath", "/etc/message-utility-bot.conf"]
