import discord


VERSION = '0.2.0'


async def send_embed(client, channel, fields=[], show_footer=False, **kwargs):
    # TODO add docstring
    embed = discord.Embed(**kwargs)
    for field in fields:
        if len(field) > 2:
            embed.add_field(name=field[0], value=field[1], inline=field[2])
        else:
            embed.add_field(name=field[0], value=field[1], inline=False)
    if show_footer:
        embed.set_footer(text=f"Esobot v{VERSION}")
    await client.send_message(channel, embed=embed)
