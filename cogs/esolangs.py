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
    async def esowiki(self, ctx, *, esolang_name):
        """Link to the Esolang Wiki page for an esoteric programming langauge."""
        # npr = network path reference (https://stackoverflow.com/a/4978266/4958484)
        npr = f"//esolangs.org/wiki/{parse.quote(esolang_name.replace(' ', '_'))}"
        async with ctx.typing():
            async with ctx.bot.session.get('http:' + npr) as response:
                if response.status == 200:
                    await ctx.send('https:' + npr)
                else:
                    await ctx.send(embed=make_embed(
                        color=colors.EMBED_ERROR,
                        title="Error",
                        description=f"**{esolang_name}** is not on the Esolangs wiki. Make sure the capitalization is correct."
                    ))


def setup(bot):
    bot.add_cog(Esolangs(bot))
