#!/usr/bin/env python3

import discord
import os

class SpacerBot(discord.Client):
    async def on_ready(self):
        print("<6> now online")

    async def on_message(self, msg: discord.Message):
        if msg.author != self.user:
            await msg.channel.send("|" + ("▬"*15) + "|")


TOK = os.environ["SPACER_BOT_DISCORD_TOKEN"]

client = SpacerBot()
client.run(TOK)
