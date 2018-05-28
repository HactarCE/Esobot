import discord
import asyncio

from discord.ext import commands
from collections import defaultdict
from utils import make_embed
from constants import colors

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
        """Ping someone when certain critera is met.
        `criteria` should be a comma-seperated list of `name=value`, where `name` is one of the following:
        
        `activity` - in which case `value` is the name of the activity and the criteria will be true once their activity is the same as the given value.
        `status` - in which case `value` is the name of the status and the criteria will be true once their status matches the given status.
        These values can be prepended with `not` to invert them, or you can put multiple criteria in the same place and seperate them with `or` to make the criteria count if any of the contained criteria are true.
        """
        possible_criteria = {
            "activity": self.activity,
            "status": self.status
        }
        criteria_list = criteria.split(",")
        criteria_list_ = []
        for criteria_ in criteria_list:
            criterias = criteria_.split(" or ")
            criteria_list__ = []
            for criteria__ in criterias:
                criteria___ = criteria__.split("=")
                try:
                    criteria_list__.append((possible_criteria[criteria___[0].strip()], 
                                           criteria___[1].strip()))
                except KeyError:
                    embed = make_embed(title="Error",
                                       description="Invalid criteria.",
                                       color=colors.EMBED_ERROR)
                    await ctx.send(embed=embed)
                    return
            criteria_list_.append(criteria_list__)
        self.events[member].append((criteria_list_, ctx.author, ctx.channel))
        criteria_message = "\n".join(["\N{BULLET} " + " or ".join([y[0].__name__ + " = " + y[1] for y in x]) for x in criteria_list_])
        embed = make_embed(title=f"Scheduled a ping for {member.name}",
                           description=criteria_message,
                           color=colors.EMBED_SUCCESS)
        await ctx.send(embed=embed)

    async def loop(self):
        self.bot.wait_until_ready()
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
