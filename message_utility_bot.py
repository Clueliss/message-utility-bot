#!/usr/bin/env python3

import argparse
import discord
import os
import sys
import requests
import tempfile
import imgkit
import subprocess
from typing import *


DISCORD_CODE_MARKER = chr(96) * 3 # is backtick
DISCORD_MAX_MSG_LEN = 2000


def max_code_len(code_type: str) -> int:
    return DISCORD_MAX_MSG_LEN - (2 * len(DISCORD_CODE_MARKER)) - len(code_type) - 2


def rfind_space(s: str) -> int:
    for i, ch in enumerate(reversed(s)):
        if ch.isspace():
            return i

    return -1


def find_word_cut_index(s: str, max_len: int) -> int:
    if len(s) >= max_len:
        last_space = s.rfind(" ")
        if last_space > 0:
            return last_space

    return len(s)


def find_code_cut_index(s: str, max_len: int) -> int:
    front = s[:max_len]
    last_line = front.rfind("\n")

    if last_line > 0:
        return last_line
    else:
        return len(s)
        

def extract_file_extension(s: str) -> str:
    last_point = s.rfind(".")

    if last_point != -1:
        return s[last_point+1:]
    else:
        return ""


def split_message(content: str, code_type: str) -> List[str]:
    ret = []
    
    while len(content.strip()) > 0:
        if code_type != "_":
            MAX_CODE_LEN = max_code_len(code_type)

            front = content[:MAX_CODE_LEN]
            cut_idx = find_code_cut_index(content, MAX_CODE_LEN)
            
            ret.append("{marker}{code_type}\n{code}\n{marker}".format(
                marker=DISCORD_CODE_MARKER,
                code_type=code_type, 
                code=front[:cut_idx]))

            content = content[cut_idx:]
        else:
            front = content[:DISCORD_MAX_MSG_LEN]
            cut_idx = find_word_cut_index(front, DISCORD_MAX_MSG_LEN)

            ret.append(front[:cut_idx])
            content = content[cut_idx:]

    return ret


class MessageUtilityBot(discord.Client):
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

                elif subroutine == "expand":
                    await self.subroutine_expand(msg, args)

                elif subroutine == "embedmarkdown":
                    await self.subroutine_markdown_to_image(msg, args)
                      

    async def subroutine_markdown_to_image(self, msg: discord.Message, args):
        if len(msg.attachments) == 0:
            msg.channel.send(":error: Nothing to expand")
        else:
            GRIP_TOK = os.environ.get("MESSAGE_UTILITY_BOT_GRIP_TOKEN", "")

            attach = msg.attachments[0]
            content = requests.get(attach.url).text
            title = attach.filename if len(args) == 0 else " ".join(args)

            tmpfilepath = tempfile.mktemp() 
            with open(tmpfilepath, "w") as tmpfile:
                tmpfile.write(content)

            html_tmp_filepath = tempfile.mktemp(suffix=".html")
            subprocess.call(["grip", "--title", title, "--pass", GRIP_TOK, "--export", tmpfilepath, html_tmp_filepath])

            img_tmp_filepath = tempfile.mktemp(suffix=".jpg")
            imgkit.from_file(html_tmp_filepath, img_tmp_filepath)

            file = discord.File(img_tmp_filepath)
            await msg.channel.send(title, file=file)
            await msg.delete()

            os.remove(tmpfilepath)
            os.remove(html_tmp_filepath)
            os.remove(img_tmp_filepath)


    async def subroutine_expand(self, msg: discord.Message, args):
        if len(msg.attachments) == 0:
            msg.channel.send(":error: Nothing to expand")
        else:
            
            for idx, attach in enumerate(msg.attachments):
                specified_code_type = "_" if idx >= len(args) else args[idx]

                content = requests.get(attach.url).text.replace(DISCORD_CODE_MARKER, "\\" + DISCORD_CODE_MARKER)

                if specified_code_type == "_":
                    ext = extract_file_extension(attach.filename)

                    detected_code_type = "_"

                    if ext == "txt":
                        if content.startswith(DISCORD_CODE_MARKER) and content.endswith(DISCORD_CODE_MARKER):
                            first_line_end = content.find("\n")
                            if first_line_end != -1:
                                detected_code_type = content[3:first_line_end]

                            content = content.splitlines()[1:-1].join("\n")
                    else:
                        detected_code_type = ext

                    msgs = split_message(content, detected_code_type)
                else:
                    msgs = split_message(content, specified_code_type)
            

                tmpfilepath = tempfile.mktemp() 
                tmpfile = open(tmpfilepath, "w")
                tmpfile.write(content)
                tmpfile.close()

                file = discord.File(tmpfilepath, filename=attach.filename)
                await msg.channel.send("**Author**: {}".format(msg.author.name), file=file)

                os.remove(tmpfilepath)

                for submsg in msgs:
                    await msg.channel.send(submsg)


                await msg.delete()


    async def subrouting_insspace(self, msg: discord.Message, args):
        if len(args) == 0:
            await msg.channel.send("|" + ("▬"*15) + "|")
            await msg.delete()
        else:
            msg.channel.send(":x: Error: too many args")


    async def subroutine_settings(self, msg: discord.Message, args):
        if len(args) == 0:
            embed = discord.Embed()

            embed.title = "MessageUtilityBot Settings"
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

    TOK = os.environ["MESSAGE_UTILITY_BOT_DISCORD_TOKEN"]

    client = MessageUtilityBot(config_filepath=args.configpath)
    client.run(TOK)
