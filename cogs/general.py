from discord.ext import commands

from utils import l, make_embed
from constants import colors, info, symbols


def get_command_signature(command):
    # almost entirely copied from within discord.ext.commands, but ignores aliases
    result = command.qualified_name
    if command.usage:
        result += ' ' + command.usage
    elif command.clean_params:
        # l.warning(f"Command {command.name} has parameters but no 'usage'.")
        result = command.qualified_name
        params = command.clean_params
        if params:
            for name, param in command.clean_params.items():
                if param.default is not param.empty:
                    if param.default not in (None, ''):
                        result += f' [{name}={param.default}]'
                    else:
                        result += f' [{name}]'
                elif param.kind == param.VAR_POSITIONAL:
                    result += f' [{name}{symbols.ELLIPSIS}]'
                else:
                    result += f' <{name}>'
    return result


class General(object):
    """General-purpose commands."""

    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')

    @commands.command(
        aliases=['h', 'man'],
    )
    async def help(self, ctx, *, command_name: str=None):
        """Display a list of all commands or display information about a specific command."""
        prefix = await self.bot.get_prefix(ctx.message)
        if isinstance(prefix, list):
            prefix = prefix[0]
        if command_name:
            command = self.bot.get_command(command_name)
            if command is None:
                await ctx.send(embed=make_embed(
                    color=colors.EMBED_ERROR,
                    title="Command help",
                    description=f"Could not find command `{command_name}`."
                ))
            elif await command.can_run(ctx):
                fields = []
                if command.usage or command.clean_params:
                    fields.append(("Synopsis", f'`{get_command_signature(command)}`', True))
                if command.aliases:
                    aliases = ', '.join(f'`{alias}`' for alias in command.aliases)
                    fields.append(("Aliases", aliases, True))
                if command.help:
                    fields.append(("Description", command.help))
                misc = ''
                if not command.enabled:
                    misc += "This command is currently disabled.\n"
                if command.hidden:
                    misc += "This command is usually hidden.\n"
                if misc:
                    fields.append(("Miscallenous", misc))
                await ctx.send(embed=make_embed(
                    color=colors.EMBED_HELP,
                    title="Command help",
                    description=f'`{command.name}`',
                    fields=fields
                ))
            else:
                await ctx.send(embed=make_embed(
                    color=colors.EMBED_ERROR,
                    title="Command help",
                    description=f"You have insufficient permission to access `{command_name}`."
                ))
        else:
            cog_names = []
            ungrouped_commands = []
            for command in self.bot.commands:
                if (command.cog_name and command.cog_name not in cog_names):
                    cog_names.append(command.cog_name)
            fields = []
            for cog_name in sorted(cog_names):
                lines = []
                for command in sorted(self.bot.get_cog_commands(cog_name), key=lambda cmd: cmd.name):
                    if not command.hidden and (await command.can_run(ctx)):
                        line = f'{symbols.BULLET} **`{get_command_signature(command)}`**'
                        if command.short_doc:
                            line += f' {symbols.EM_DASH} {command.short_doc}'
                        lines.append(line)
                if lines:
                    fields.append((cog_name, '\n'.join(lines)))
            mention = ctx.me.mention
            await ctx.send(embed=make_embed(
                color=colors.EMBED_HELP,
                title="Command list",
                description=f"Invoke a command by prefixing it with `{prefix}` or {mention}. Use `{prefix}{ctx.command.name} [command]` to get help on a specific command.",
                fields=fields
            ))

    @commands.command(
        aliases=['i', 'info']
    )
    async def about(self, ctx):
        await ctx.send(embed=make_embed(
            title=f"About {info.NAME}",
            description=info.ABOUT_TEXT,
            fields=[
                ("Author", f"[{info.AUTHOR}]({info.AUTHOR_LINK})", True),
                ("GitHub Repository", info.GITHUB_LINK, True)
            ],
            footer_text=f"{info.NAME} v{info.VERSION}"
        ))


def setup(bot):
    bot.add_cog(General(bot))
