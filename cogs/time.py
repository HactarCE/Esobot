import discord

from constants import colors
from utils import make_embed
from discord.ext import commands


class Time(object):
    """Commands related to time and delaying messages."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        aliases=["pw", "pwhen", "pingw"]
    )
    async def pingwhen(self, ctx):
        """Ping someone when a certain criterium is met.

        If the condition does not complete after 48 hours, then the command will terminate.
        """

    @pingwhen.command(
        aliases=["on"]
    )
    async def online(self, ctx, member: discord.Member, *, message=None):
        message = f"{member.mention}, {ctx.author.mention} has sent you a scheduled ping." + (f" A message was attached:\n\n```\n{message}\n```" if message else "")
        await ctx.send(
            embed=make_embed(
                title="Ping scheduled",
                description=f"{member.mention} will be pinged when they go online with the message:\n\n{message}",
                color=colors.EMBED_SUCCESS
            )
        )
        if member.status != discord.Status.online:
            await self.bot.wait_for(
                "member_update", 
                check=lambda before, after: after.id == member.id and after.status == discord.Status.online
            )
        await ctx.send(message)

    @pingwhen.command(
        aliases=["nogame"]
    )
    async def free(self, ctx, member: discord.Member, *, message=None):
        message = f"{member.mention}, {ctx.author.mention} has sent you a scheduled ping." + (f" A message was attached:\n\n```\n{message}\n```" if message else "")
        await ctx.send(
            embed=make_embed(
                title="Ping scheduled",
                description=f"{member.mention} will be pinged when they stop playing a game with the message:\n\n{message}",
                color=colors.EMBED_SUCCESS
            )
        )
        if member.activity:
            await self.bot.wait_for(
                "member_update", 
                check=lambda before, after: after.id == member.id and after.activity == None
            )
        await ctx.send(message)


def setup(bot):
    bot.add_cog(Time(bot))
