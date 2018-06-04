from collections import defaultdict
from discord.ext import commands
import asyncio
import discord
import re

from constants import colors
from utils import make_embed


class Time(object):
    """Commands related to time and delaying messages."""

    def __init__(self, bot):
        self.bot = bot
        self.events = defaultdict(list)

    def activity(self, member, value):
        notted = value.startswith("not ")
        val = value if not notted else value[4:]
        result = member.activity.name == val if member.activity else False
        return result if not notted else not result

    def status(self, member, value):
        notted = value.startswith("not ")
        val = value if not notted else value[4:]
        result = str(member.status) == value
        return result if not notted else not result

    @commands.command(
        aliases=["pw", "pwhen", "pingw"]
    )
    async def pingwhen(self, ctx, member: discord.Member, *, criteria):
        """Ping someone when certain critera are met.
        `criteria` should be a list of criteria, each separated either by `or` or `and`. (`and` takes precedence over `or`; thus `A or B and C` would be parsed as `A or (B and C)`.) Each criterium is of the form `name = value` or `name != value`. (Using `!=` inverts the condition.) The following `name`s are supported:

        `activity` \N{EM_DASH} `value` is the name of an activity (e.g. a game)
        `status` \N{EM_DASH} `value` is one of `online`, `offline`, `idle`/`away`, `dnd`.

        If the condition does not complete after 48 hours, then the command will terminate.
        """  # TODO add examples and add support for 'away'
        possible_criteria = {
            'activity': lambda m: m.activity,
            'status': lambda m: m.status
        }
        or_checks = []
        summary = "Will ping {} on any of the following conditions:"
        for or_criterium in re.split(r"\s+or\s+", criteria):
            and_checks = []
            summary += "\N{BULLET}"
            for and_criterium in re.split(r"\s+and\s+", or_criterium):
                summary += "\n    All of the following are true:"
                try:
                    name, value = re.split("\s*!?=\s*", and_criterium)
                    check = lambda m: possible_criteria[name] == value
                    if '!=' in and_criterium:
                        def check(m): return not check(m)
                    and_checks.append(check)
                except KeyError:
                    await ctx.send(embed=make_embed(
                        color=colors.EMBED_ERROR,
                        title="Error",
                        description=f"Invalid criterium: {and_criterium}"
                    ))
                    return
            or_checks.append(lambda m: any(f(m) for f in and_checks))
        unified_check = all(lambda m: )
        await ctx.send(embed=make_embed(
            color=colors.EMBED_SUCCESS,
            title=f"Scheduled a ping for {member.name}",
            description=summary
        ))
        await ctx.wait_for(
            'member_update',
            timeout=60 * 60 * 48
        )

    async def loop(self):
        await self.bot.wait_until_ready()
        while True:
            events_copy = self.events.copy()
            for member in self.events:
                for event in self.events[member]:
                    if all([any([y[0](member, y[1]) for y in x]) for x in event[0]]):
                        await event[2].send(f"{member.mention} You have received a scheduled ping from {event[1].mention}.")
                        events_copy[member].remove(event)
            self.events = events_copy
            await asyncio.sleep(1)


def setup(bot):
    time = Time(bot)
    bot.loop.create_task(time.loop())
    bot.add_cog(time)
