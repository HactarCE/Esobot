from utils import send_embed, VERSION

from . import command, commands, get_matching_command, get_matching_implicit_command, PRETTY_COMMAND_PREFIX

ABOUT_TEXT = f'''\
Esobot is an open source Discord bot created using \
[discord.py](https://github.com/Rapptz/discord.py) for the \
[Esolang Discord Server](https://discord.gg/vwsaeee).
'''


@command(
    regex=r'about',
    help_syntax='about',
    help_summary="Display information about Esobot."
)
async def about(client, args, message):
    await send_embed(
        client, message.channel,
        title="About Esobot",
        description=ABOUT_TEXT,
        # TODO add color
        fields=[
            ("Version", VERSION),
            ("Author", "[HactarCE](https://github.com/HactarCE)"),
            ("GitHub Repository", "https://github.com/HactarCE/Esobot")
        ]
    )


@command(
    regex=r'h|help|man',
    help_syntax='help [command]',
    help_summary="Display this command list or get help on a specific command.",
    # help_full="Yes, you're very creative. Well done running the help command on itself.",
    aliases=['man']
)
async def help(client, args, message):
    if args:
        cmd = get_matching_implicit_command(args[0])
        if cmd:
            fields = []
            if cmd.aliases:
                fields.append(("Aliases", ', '.join(cmd.aliases)))
            fields.append(("Summary", cmd.help_summary))
            if cmd.help_full:
                fields.append(("Description", cmd.help_full))
            await send_embed(
                client, message.channel,
                title="Command Reference",
                description=cmd.help_syntax,  # TODO merge with duplicated code below
                fields=fields,
                show_footer=True
            )
        else:
            await send_embed(
                client, message.channel,
                title="Command Reference",
                description=f"Could not find a command matching `{args[0]}`.",
                show_footer=True
            )
    else:
        command_summaries = '\n'.join(f'**{PRETTY_COMMAND_PREFIX}{c.help_syntax}** - {c.help_summary}' for c in commands)
        await send_embed(
            client, message.channel,
            title="Command List",
            description=command_summaries,
            show_footer=True
        )
