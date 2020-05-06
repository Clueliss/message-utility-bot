#!/usr/bin/env python3

import argparse
import discord
import os
import sys

class SpacerBot(discord.Client):
    def __init__(self, config_filepath: str):
        super().__init__()
        self._config_filepath = config_filepath
        self._prefix = ">"
        self._settings = ["prefix"]

        try:
            self.load_prefix()
        except:
            pass

    def load_prefix(self):
        conffile = open(self._config_filepath, "r")
        self._prefix = conffile.readline().strip()
        conffile.close()

    def store_prefix(self):
        conffile = open(self._config_filepath, mode="w")
        conffile.write(self._prefix)
        conffile.close()

    async def on_ready(self):
        print("<6> now online")

    async def on_message(self, msg: discord.Message):
        if msg.author != self.user:
            if msg.content.startswith(self._prefix):
                cmd: [str] = msg.content[len(self._prefix):].split(" ")

                if len(cmd) == 0:
                    await msg.channel.send("Invalid command")
                else:
                    subroutine: str = cmd[0]
                    args: List[str] = cmd[1:]

                    if subroutine == "settings":
                        await self.subroutine_settings(msg, args)

                    elif subroutine == "insspace":
                        await self.subrouting_insspace(msg, args)
                        


    async def subrouting_insspace(self, msg: discord.Message, args):
        if len(args) == 0:
            await msg.channel.send("|" + ("▬"*15) + "|")
            await msg.delete()
        else:
            msg.channel.send("insspace: too many args")


    async def subroutine_settings(self, msg: discord.Message, args):
        if len(args) == 0:
            buf = ""
            for s in self._settings:
                buf += "{}settings {}".format(self._prefix, s)

            await msg.channel.send(buf)

        else:
            if args[0] == "prefix":
                if len(args)-1 == 0:
                    await msg.channel.send("{}settings prefix <Value>".format(self._prefix))
                else:
                    self._prefix = args[1]
                    self.store_prefix()

                    await msg.channel.send("settings prefix: success prefix is now '{}'".format(self._prefix))

            else:
                await msg.channel.send("settings: invalid setting")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--configpath", type=str, required=True)
    args = parser.parse_args()

    TOK = os.environ["SPACER_BOT_DISCORD_TOKEN"]

    client = SpacerBot(config_filepath=args.configpath)
    client.run(TOK)
