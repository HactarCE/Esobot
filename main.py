#!/usr/bin/env python3

import logging

import commands

LOG_LEVEL_API = logging.WARNING
LOG_LEVEL_BOT = logging.INFO
# LOG_FMT = '[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s'
LOG_FMT = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'

try:
    import discord
    import asyncio
except ImportError:
    print("discord.py is required. Run `python3 -m pip install -U discord.py`.")
    exit(1)

try:
    with open('token.txt') as f:
        TOKEN = f.read().strip()
except IOError:
    print("Create a file token.txt and place the bot token in it.")
    exit(1)

logging.basicConfig(format=LOG_FMT)
logging.getLogger('discord').setLevel(LOG_LEVEL_API)
l = logging.getLogger('bot')
l.setLevel(LOG_LEVEL_BOT)

client = discord.Client()


@client.event
async def on_ready():
    l.debug('on_ready')
    l.info(f"Logged in as {client.user.name}#{client.user.discriminator}")


@client.event
async def on_message(message):
    l.debug(f"on_message{str(message)}")
    l.info(f"[#{message.channel.id if message.channel.is_private else message.channel.name}] {message.author.display_name}: {message.content}")
    cmd = commands.get_matching_command(message)
    print(cmd)
    if cmd:
        await cmd.run_if_matches(client, message)


async def on_command(command, message):
    l.debug('on_command' + command)
    args = command.split()

client.run(TOKEN)
