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
        `criteria` should be a list of criteria, each separated either by `or` or `and`. (`or` takes precedence over `and`; thus `A and B or C` would be parsed as `A and (B or C)`.) Each criterium is of the form `name=value`, and can be preceded by `not` to invert it. The following `name`s are supported:

        `activity` \N{EM_DASH} `value` is the name of an activity (e.g. a game)
        `status` \N{EM_DASH} `value` is one of `online`, `offline`, `idle`/`away`, `dnd`.
        """ # TODO add examples and add support for 'away'
        possible_criteria = {
            'activity': self.activity,
            'status': self.status
        }
        and_criteria = []
        for and_criterium in re.split(r"\s+and\s+", criteria):
            or_criteria = []
            for or_criterium in re.split(r"\s+or\s+", and_criterium):
                try:
                    name, value = re.split("\s*=\s*", or_criterium)
                    and_criteria.append((possible_criteria[name], value))
                except KeyError:
                    await ctx.send(embed=make_embed(
                        color=colors.EMBED_ERROR,
                        title="Error",
                        description=f"Invalid criterium: {or_criterium}"
                    ))
                    return
            and_criteria.append()
        self.events[member].append((criteria_list_, ctx.author, ctx.channel))
        criteria_message = "\n".join(["\N{BULLET} " + " or ".join([y[0].__name__ + " = " + y[1] for y in x]) for x in criteria_list_])
        await ctx.send(embed=make_embed(
            color=colors.EMBED_SUCCESS,
            title=f"Scheduled a ping for {member.name}",
            description=criteria_message
        ))

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
