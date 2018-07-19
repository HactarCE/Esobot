from discord.ext import commands
import discord

from constants import colors, info
from utils import make_embed


class Utility(object):
    """General-purpose utility commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=['p', 'ping', 'pl']
    )
    async def pinglater(self, ctx, user: discord.User, message: str=None):
        """Ping a user when they come online, with an optional message.

        If the user does come online after 48 hours, the command will timeout.
        """
        # TODO subcommands!
        user_text = f'**{user.name}#{user.discriminator}**'
        if user.display_name != user.name:
            user_text += f' (**{user.display_name}**)'
        m = ctx.send_message(embed=make_embed(
            colors=colors.EMBED_INFO,
            description=f"Waiting to ping {user_text}\N{HORIZONTAL ELLIPSIS}"
        ))
        # while user.status is not discord.Status.online:
            # ctx.bot.wait_for('memeber_update', check=lambda)

def setup(bot):
    bot.add_cog(Utility(bot))
