import asyncio
import discord
import logging
import traceback

from constants import colors, emoji

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


async def report_error(ctx, exc, *args, **kwargs):
    if ctx:
        if isinstance(ctx.channel, discord.DMChannel):
            guild_name = "N/A"
            channel_name = f"DM"
        elif isinstance(ctx.channel, discord.GroupChannel):
            guild_name = "N/A"
            channel_name = f"Group with {len(ctx.channel.recipients)} members (id={ctx.channel.id})"
        else:
            guild_name = ctx.guild.name
            channel_name = f"#{ctx.channel.name}"
        user = ctx.author
        tb = ''.join(traceback.format_tb(exc.original.__traceback__))
        fields = [
            ("Guild", guild_name, True),
            ("Channel", channel_name, True),
            ("User", f"{user.name}#{user.discriminator} (A.K.A. {user.display_name})"),
            ("Message Content", f"{ctx.message.content}"),
        ]
    else:
        fields = []
    fields += [
        ("Args", f"```\n{repr(args)}\n```" if args else "None", True),
        ("Keyword Args", f"```\n{repr(kwargs)}\n```" if kwargs else "None", True),
        ("Traceback", f"```\n{tb}\n```")
    ]
    await ctx.bot.get_user(ctx.bot.owner_id).send(embed=make_embed(
        color=colors.EMBED_ERROR,
        title="Error",
        description=f'`{str(exc)}`',
        fields=fields
    ))
