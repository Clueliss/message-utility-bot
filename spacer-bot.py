#!/usr/bin/env python3

import argparse
import discord
import os
import sys

class SpacerBot(discord.Client):
    def __init__(self, config_filepath: str):
        super().__init__()
        self._config_filepath = config_filepath
        self._prefix = "-"
        self._settings = ["prefix"]
        self._settings_descr = [":exclamation: prefix"]

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
        if not msg.author.bot and msg.content.startswith(self._prefix):
            cmd = msg.content[len(self._prefix):].split(" ")

            if len(cmd) == 0:
                await msg.channel.send("Invalid command")
            else:
                subroutine: str = cmd[0]
                args = cmd[1:]

                if subroutine == "settings":
                    await self.subroutine_settings(msg, args)

                elif subroutine == "insspace":
                    await self.subrouting_insspace(msg, args)
                        


    async def subrouting_insspace(self, msg: discord.Message, args):
        if len(args) == 0:
            await msg.channel.send("|" + ("▬"*15) + "|")
            await msg.delete()
        else:
            msg.channel.send(":x: Error: too many args")


    async def subroutine_settings(self, msg: discord.Message, args):
        if len(args) == 0:
            embed = discord.Embed()

            embed.title = "SpacerBot Settings"
            embed.description = "Use the command format `{}settings <option>`".format(self._prefix)
        
            for s,d in zip(self._settings, self._settings_descr):
                embed.add_field(name=d, value="`{}settings {}`".format(self._prefix, s), inline=True)

            await msg.channel.send(embed=embed)

        else:
            if args[0] == "prefix":
                if len(args) != 2:
                    await msg.channel.send("Success :x: expected exactly 1 arg")
                else:
                    self._prefix = args[1]
                    self.store_prefix()

                    await msg.channel.send(":white_check_mark: Success: prefix is now '{}'".format(self._prefix))

            else:
                await msg.channel.send(":x: Error: invalid setting")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--configpath", type=str, required=True)
    args = parser.parse_args()

    TOK = os.environ["SPACER_BOT_DISCORD_TOKEN"]

    client = SpacerBot(config_filepath=args.configpath)
    client.run(TOK)
