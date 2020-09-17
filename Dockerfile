FROM docker.io/fedora

ENV MESSAGE_UTILITY_BOT_DISCORD_TOKEN=YOUR_BOT_TOKEN
ENV MESSAGE_UTILITY_BOT_GRIP_TOKEN=YOUR_GITHUB_AUTH_KEY
ENV QT_QPA_PLATFORM=offscreen

RUN dnf install python3 python3-pip git wkhtmltopdf which -y
RUN python3 -m pip install discord requests imgkit grip

COPY ./message_utility_bot.py /init
RUN chmod +x /init

CMD ["/init", "--configpath", "/etc/message-utility-bot.conf"]
