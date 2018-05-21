#!/usr/bin/env python3

DEV = True

from discord.ext import commands
import logging
import traceback

from cogs import ALL_EXTENSIONS
from constants import colors
from utils import l, make_embed, report_error

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

COMMAND_PREFIX = '!'

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(COMMAND_PREFIX),
    case_insensitive=True,
    owner_id=owner_id
)


@bot.listen()
async def on_ready():
    l.info(f"Logged in as {bot.user.name}#{bot.user.discriminator}")


@bot.listen()
async def on_resume():
    l.info("Resumed session")


error_descriptions = {
    commands.MissingRequiredArgument: lambda exc: f"Missing required argument: {exc.param.name}.",
}


@bot.listen()
async def on_command_error(ctx, exc, *args, **kwargs):
    command_name = ctx.command.name if ctx.command else 'unknown command'
    l.error(f"'{str(exc)}' encountered while executing {command_name} (args: {args}; kwargs: {kwargs})")
    if isinstance(exc, commands.UserInputError):
        if isinstance(exc, commands.MissingRequiredArgument):
            description = f"Missing required argument `{exc.param.name}`."
        elif isinstance(exc, commands.TooManyArguments):
            description = f"Too many arguments."
        elif isinstance(exc, commands.BadArgument):
            description = f"Bad argument:\n```\n{str(exc)}\n```"
        else:
            description = f"Bad user input."
        description += "\n\nRun `{COMMAND_PREFIX}help {command_name}` to view the required arguments."
    elif isinstance(exc, commands.CommandNotFound):
        description = f"Could not find command `{ctx.invoked_with.split()[0]}`."
    elif isinstance(exc, commands.CheckFailure):
        if isinstance(exc, commands.NoPrivateMessage):
            description = f"Cannot be run in a private message channel."
        elif isinstance(exc, commands.MissingPermissions) or isinstance(exc, commands.BotMissingPermissions):
            if isinstance(exc, commands.MissingPermissions):
                description = f"You don't have permission to do that."
            elif isinstance(exc, commands.BotMissingPermissions):
                description = f"I don't have permission to do that."
            missing_perms = '\n'.join(exc.missing_perms)
            description += f" Missing:\n```\n{missing_perms}\n```"
        else:
            description = f"Command check failed."
    elif isinstance(exc, commands.DisabledCommand):
        description = f"That command is disabled."
    elif isinstance(exc, commands.CommandOnCooldown):
        description = f"That command is on cooldown."
    else:
        description = f"Sorry, something went wrong.\n\nA team of highly trained monkeys has been dispatched to deal with the situation."
        await report_error(ctx, exc)
    await ctx.send(embed=make_embed(
        color=colors.EMBED_ERROR,
        title="Error",
        description=description
    ))


@bot.listen()
async def on_message(message):
    ch = message.channel
    is_private = isinstance(ch, discord.DMChannel) or isinstance(ch, discord.GroupChannel)
    l.info(f"[#{ch.id if is_private else ch.name}] {message.author.display_name}: {message.content}")


if __name__ == '__main__':
    for extension in ALL_EXTENSIONS:
        bot.load_extension('cogs.' + extension)
    bot.run(TOKEN)
