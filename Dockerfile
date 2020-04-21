FROM docker.io/fedora

ENV SPACER_BOT_DISCORD_TOKEN=YOUR_BOT_TOKEN

RUN dnf install python3 git
RUN python -m pip install discord

RUN curl -sSf https://raw.githubusercontent.com/Clueliss/spacer-bot/master/spacer-bot.py > /init
RUN chmod +x /init

CMD ["/init"]
