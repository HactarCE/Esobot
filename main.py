#!/usr/bin/env python3

DEV = True

from discord.ext import commands
import logging
import os
import sys
import traceback

from utils import l, make_embed
import cogs

LOG_LEVEL_API = logging.WARNING
LOG_LEVEL_BOT = logging.INFO
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


if DEV:
    logging.basicConfig(format=LOG_FMT)
else:
    logging.basicConfig(format=LOG_FMT, filename='bot.log')
logging.getLogger('discord').setLevel(LOG_LEVEL_API)
l.setLevel(LOG_LEVEL_BOT)


try:
    with open('admin.txt') as f:
        owner_id = int(f.read())
except IOError:
    owner_id = None

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('!'),
    case_insensitive=True,
    owner_id=owner_id
)


@bot.listen()
async def on_ready():
    l.info(f"Logged in as {bot.user.name}#{bot.user.discriminator}")


@bot.listen()
async def on_resume():
    l.info("Resumed session")


@bot.listen()
async def on_error(event, ctx, *args, **kwargs):
    print(event, ctx, args, kwargs)
    _, exc, tb = sys.exc_info()
    l.error(f'"{str(exc)}" while executing {event} (args: {args}; kwargs: {kwargs})')
    if isinstance(exc, commands.MissingRequiredArgument):
        # await
        pass
    else:
        await bot.send_message(await bot.get_user_info(bot.owner_id), embed=make_embed(
            title="Error",
            description=str(exc),
            fields=[
                ("Event", f'```\n{event}\n```', True),
                ("Args", f'```\n{repr(args)}\n```', True),
                ("Keyword Args", f'```\n{repr(kwargs)}\n```', True),
                ("Traceback", f'```\n{"".join(traceback.format_tb(tb))}\n```')
            ]
        ))


@bot.listen()
async def on_message(message):
    is_private = message.type in (discord.ChannelType.private, discord.ChannelType.group)
    l.info(f"[#{message.channel.id if is_private else message.channel.name}] {message.author.display_name}: {message.content}")


if __name__ == '__main__':
    # EXTENSIONS = ['admin', 'general']
    EXTENSIONS = ['admin', 'general']
    for extension in EXTENSIONS:
        bot.load_extension('cogs.' + extension)
    bot.run(TOKEN)
