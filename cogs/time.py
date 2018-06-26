import asyncio
import discord
import json
import pytz

from constants import colors, channels, paths
from utils import make_embed
from discord.ext import commands
from datetime import datetime


class Time(object):
    """Commands related to time and delaying messages."""

    def __init__(self, bot):
        self.bot = bot
        with open(paths.TIME_SAVES) as f:
            self.time_config = json.load(f)

    def get_time(self, id):
        if str(id) not in self.time_config:
            return None

        now = datetime.now(pytz.timezone(self.time_config[str(id)]))
        return now.strftime("%H:%M on %A, timezone %Z%z")

    @commands.group(
        aliases=["tz", "when", "t"],
        invoke_without_command=True
    )
    async def time(self, ctx, *, user: discord.Member = None):
        user = ctx.author if not user else user
        time = self.get_time(user.id)

        if not time:
            message = ("You don't have a timezone set. You can set one with `time set`." if user == ctx.author
                  else "That user doesn't have a timezone set.")
            await ctx.send(
                embed=make_embed(
                    title="Timezone not set",
                    description=message,
                    color=colors.EMBED_ERROR
                )
            )
            return

        await ctx.send(
            embed=make_embed(
                title=f"{user.name}'s time",
                description=time,
                color=colors.EMBED_SUCCESS
            )
        )

    @time.command()
    async def set(self, ctx, timezone="invalid"):
        try:
            pytz.timezone(timezone)
            self.time_config[str(ctx.author.id)] = timezone
            with open(paths.TIME_SAVES, "w") as f:
                json.dump(self.time_config, f)
            await ctx.send(
                embed=make_embed(
                    title="Set timezone",
                    description=f"Your timezone is now {timezone}.",
                    color=colors.EMBED_SUCCESS
                )
            )
        except pytz.exceptions.UnknownTimeZoneError:
            url = "https://github.com/sdispater/pytzdata/blob/master/pytzdata/_timezones.py"
            await ctx.send(
                embed=make_embed(
                    title="Invalid timezone",
                    description=f"You either set an invalid timezone or didn't specify one at all. "
                                 "Read a list of valid timezone names [here]({url}).",
                    color=colors.EMBED_ERROR
                )
            )

    async def time_loop(self, channel_id):
        await self.bot.wait_until_ready()

        channel = self.bot.get_channel(channel_id)
        await channel.purge()
        info_msg = await channel.send("Processing times...")

        while True:
            next_msg = []
            for id in self.time_config:
               next_msg.append(f"<@{id}>'s time is {self.get_time(id)}")
            if next_msg:
                await info_msg.edit(content="\n".join(next_msg))
            else:
                await info_msg.edit(content="Nobody has added a timezone to the bot yet.")
            await asyncio.sleep(30)


def setup(bot):
    time = Time(bot)
    bot.loop.create_task(time.time_loop(channels.TIME_CHANNEL))
    bot.add_cog(Time(bot))
