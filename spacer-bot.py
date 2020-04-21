#!/usr/bin/env python

import discord
import os

TOK = os.environ["SPACER_BOT_DISCORD_TOKEN"]

class SpacerBot(discord.Client):
    async def on_ready(self):
        print("<6> now online")

    async def on_message(self, msg: discord.Message):
        if not msg.author == self.user:
            await msg.channel.send("|" + ("▬"*15) + "|")

client = SpacerBot()
client.run(TOK)
