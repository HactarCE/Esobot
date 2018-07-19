from textwrap import dedent
import datetime
import re

import discord
from discord.ext import commands

from constants import colors, info
from utils import make_embed, react_yes_no


class Mod(object):
    """General-purpose moderation commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=['rem', 'rm']
    )
    @commands.check(commands.has_permissions(manage_messages=True))
    async def remove(self, ctx, limit: int=50, content: str=r'.', author: discord.User=None):
        """Delete messages in bulk.

        This command supports a number of filters:
        limit (Default: `50`) — Number of messages to search (not the number of messages to delete).
        content (Default `.*`) — Regular expression specifying content to search for in messages. If this regex matches any portion of the message, and it meets the other criteria, it will be deleted. Use `.*` to match all messages.
        author (Default: all) — Author of messages to remove. Unless specified, messages will not be filtered by author.

        This command will ask the user for confirmation first. To bypass this, use the `remove!` command.
        """
        # print(dict(zip(args[::2], args[1::2])))
        # await self.clean_(ctx, False, **dict(zip(args[::2], args[1::2])))
        await self.clean_(ctx, False, limit=limit, content=content, author=author)

    @commands.command(
        name='remove!',
        aliases=['rem!', 'rm!'],
        hidden=True
    )
    @commands.check(commands.has_permissions(manage_messages=True))
    async def clean_noconfirm(self, ctx, limit: int=50, content: str=r'.', author: discord.User=None):
        """Delete messages in bulk without asking for confirmation.

        See `remove` for more details.
        """
        # await self.clean_(ctx, True, **dict(zip(args[::2], args[1::2])))
        await self.clean_(ctx, False, limit=limit, content=content, author=author)

    async def clean_(self, ctx, noconfirm=False, *, limit: int=50, author: discord.User=None, content: str=None):
        if content == '.':
            content = '.*'
        if noconfirm:
            result = 'y'
        else:
            description = dedent(f"""\
            ```
            limit = {limit}
            author = {author.name + '#' + author.discriminator if author else '*'}
            content = {content or r'.*'}
            ```""")
            m = await ctx.send(embed=make_embed(
                color=colors.EMBED_ASK,
                title="Delete messages?",
                description=description
            ))
            result = await react_yes_no(ctx, m)
        await (ctx.send if noconfirm else m.edit)(embed=make_embed(
            color={
                'y': colors.EMBED_INFO if noconfirm else colors.EMBED_CONFIRM,
                'n': colors.EMBED_CANCEL,
                't': colors.EMBED_TIMEOUT
            }[result],
            title={
                'y': "Deleting messages...",
                'n': "Deletion cancelled.",
                't': "Deletion timed out."
            }[result],
            description=description
        ))
        if result == 'y':
            pattern = content and re.compile(content)
            def should_delete(msg):
                if author and msg.author != author:
                    return False
                return pattern and pattern.search(msg.content)
            channel_history = ctx.channel.history(limit=limit, before=datetime.datetime.now()).flatten()
            try:
                count = len(channel_history)
                await ctx.channel.delete_messages([msg for msg in reverse(await channel_history) if should_delete(msg)])
                await ctx.channel.send_message(embed=make_embed(
                    colors=colors.EMBED_SUCCESS,
                    title=f"{count} message{'' if count == 1 else 's'} deleted"
                ))
            except discord.errors.HTTPException:
                await ctx.channel.send_message(embed=make_embed(
                    color=colors.EMBED_ERROR,
                    title="Error",
                    description="Cannot delete messages older than 14 days"
                ))


def setup(bot):
    bot.add_cog(Mod(bot))
