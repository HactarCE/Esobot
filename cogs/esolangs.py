from discord.ext import commands
from urllib import parse
import aiohttp

from constants import colors, info
from utils import make_embed


class Esolangs(object):
    """Commands related to esoteric programming languages."""

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'session'):
            bot.session = aiohttp.ClientSession(loop=bot.loop, headers={"User-Agent": info.NAME})

    @commands.command(
        aliases=['ew', 'w', 'wiki']
    )
    async def esowiki(self, ctx, esolang_name):
        """Link to the Esolang Wiki page for an esoteric programming langauge."""
        url = f"https://esolangs.org/wiki/{parse.quote(esolang_name)}"
        async with ctx.typing():
            async with ctx.bot.session.get(url) as response:
                if response.status == 200:
                    await ctx.send(url)
                else:
                    await ctx.send(f"{esolang_name} is not on the Esolangs wiki. Make sure you've got the capitalization correct.")


def setup(bot):
    bot.add_cog(Esolangs(bot))
