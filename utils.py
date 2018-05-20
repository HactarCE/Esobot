import asyncio
import discord
import logging

from constants import emoji

l = logging.getLogger('bot')


def make_embed(*, fields=[], footer_text=None, **kwargs):
    # TODO Add docstring
    embed = discord.Embed(**kwargs)
    for field in fields:
        if len(field) > 2:
            embed.add_field(name=field[0], value=field[1], inline=field[2])
        else:
            embed.add_field(name=field[0], value=field[1], inline=False)
    if footer_text:
        embed.set_footer(text=footer_text)
    return embed


async def react_yes_no(ctx, m, timeout=30):
    # TODO Add docstring and possibly rename
    await m.add_reaction(emoji.CONFIRM)
    await m.add_reaction(emoji.CANCEL)
    try:
        reaction, _ = await ctx.bot.wait_for(
            'reaction_add',
            check=lambda reaction, user: (
                reaction.emoji in (emoji.CONFIRM, emoji.CANCEL)
                and reaction.message.id == m.id  # not sure why I need to compare the IDs
                and user == ctx.message.author
            ),
            timeout=timeout
        )
        result = 'ny'[reaction.emoji == emoji.CONFIRM]
    except asyncio.TimeoutError:
        result = 't'
    await m.remove_reaction(emoji.CONFIRM, ctx.me)
    await m.remove_reaction(emoji.CANCEL, ctx.me)
    return result
