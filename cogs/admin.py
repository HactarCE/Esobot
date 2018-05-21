from discord.ext import commands
import asyncio
import os
from subprocess import PIPE
import sys

from . import ALL_EXTENSIONS
from constants import colors, emoji, info
from utils import l, make_embed, react_yes_no, report_error


class Admin(object):
    """Admin-only commands."""

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(
        aliases=['quit']
    )
    async def shutdown(self, ctx):
        """Shuts down the bot.

        This command will ask the user for confirmation first. To bypass this, use the `shutdown!` command.
        """
        await self.shutdown_(ctx)

    @commands.command(
        name='shutdown!',
        aliases=['quit!'],
        hidden=True
    )
    async def shutdown_noconfirm(self, ctx):
        """Shuts down the bot without asking for confirmation.

        See `shutdown` for more details.
        """
        await self.shutdown_(ctx, True)

    async def shutdown_(self, ctx, noconfirm=False):
        if noconfirm:
            result = 'y'
        else:
            m = await ctx.send(embed=make_embed(
                color=colors.EMBED_ASK,
                title="Shutdown?",
                description="This action may be difficult to undo without phsyical or remote access to the host machine. Are you sure?"
            ))
            result = await react_yes_no(ctx, m)
        await (ctx.send if noconfirm else m.edit)(embed=make_embed(
            color={
                'y': colors.EMBED_INFO if noconfirm else colors.EMBED_CONFIRM,
                'n': colors.EMBED_CANCEL,
                't': colors.EMBED_TIMEOUT
            }[result],
            title={
                'y': "Shutting down...",
                'n': "Shutdown cancelled.",
                't': "Shutdown timed out."
            }[result]
        ))
        if result is 'y':
            l.info(f"Shutting down at the command of {ctx.message.author.display_name}...")
            await self.bot.logout()

    @commands.command()
    async def update(self, ctx):
        """Runs `git pull` to update the bot."""
        subproc = await asyncio.create_subprocess_exec('git', 'pull', stdout=PIPE)
        embed = make_embed(
            color=colors.EMBED_INFO,
            title="Running `git pull`"
        )
        m = await ctx.send(embed=embed)
        returncode = await subproc.wait()
        embed.color = colors.EMBED_ERROR if returncode else colors.EMBED_SUCCESS
        stdout, stderr = await subproc.communicate()
        fields = []
        if stdout:
            embed.add_field(
                name="Stdout",
                value=f"```\n{stdout.decode('utf-8')}\n```",
                inline=False
            )
        if stderr:
            embed.add_field(
                name="Stderr",
                value=f"```\n{stderr.decode('utf-8')}\n```",
                inline=False
            )
        if not (stdout or stderr):
            embed.description = "`git pull` completed."
        await m.edit(embed=embed)
        await self.reload_(ctx, '*')

    @commands.command()
    async def reload(self, ctx, *extensions):
        """Reload an extension.

        Use `reload *` to reload all extensions.

        This command is automatically run by `update`.
        """
        if not extensions:
            ctx.send(embed=make_embed(
                color=colors.EMBED_ERROR,
                title="Error",
                description="No modules supplied."
            ))
        await self.reload_(ctx, *extensions)

    async def reload_(self, ctx, *extensions):
        if '*' in extensions:
            title = "Reloading all extensions"
        elif len(extensions) > 1:
            title = "Reloading extensions"
        else:
            title = f"Reloading `{extensions[0]}`"
        embed = make_embed(
            color=colors.EMBED_INFO,
            title=title
        )
        m = await ctx.send(embed=embed)
        color = colors.EMBED_SUCCESS
        description = ''
        if '*' in extensions:
            extensions = ALL_EXTENSIONS
        for extension in extensions:
            self.bot.unload_extension('cogs.' + extension)
            try:
                self.bot.load_extension('cogs.' + extension)
            except:
                color = colors.EMBED_ERROR
                description += f"Failed to load `{extension}`.\n"
                _, exc, _ = sys.exc_info()
                if not isinstance(exc, ImportError):
                    await report_error(ctx, exc)
        if not description:
            description = "Done."
        await m.edit(embed=make_embed(
            color=color,
            title=title.replace("ing", "ed"),
            description=description
        ))


def setup(bot):
    bot.add_cog(Admin(bot))
