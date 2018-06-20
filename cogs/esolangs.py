import aiohttp
import importlib
import os
import io

from discord.ext import commands
from urllib import parse
from constants import colors, info
from utils import make_embed

def clean(text):
    return text.replace("*", r"\*"
              ).replace("~", r"\~"
              ).replace("_", r"\_"
              ).replace("`", r"\`"
              ).replace("\\", "\\\\")

class DiscordInput:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        self.buffer = ""

    async def read(self, amount):
        response = []
        for _ in range(amount):
            if not self.buffer:
                async def check(message):
                    return (message.channel == self.channel and 
                            message.author != self.bot.user)

                message = await self.bot.wait_for("message", check=check)
                self.buffer = message.content + "\n"

            response.append(self.buffer[0])
            self.buffer = self.buffer[1:]
        return "".join(response)

    async def readline(self):
        result = ""
        while result[-1] != "\n":
            result.append(self.read(1))
        return result


class DiscordOutput:
    def __init__(self, message):
        self.message = message
        self.output = ""

    async def write(self, text):
        self.output += text
        if text.endswith("\n"):
            await self.flush()

    async def flush(self):
        await self.message.edit(content="```\n" + clean(self.output) + "\n```")


class Esolangs(object):
    """Commands related to esoteric programming languages."""

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'session'):
            bot.session = aiohttp.ClientSession(loop=bot.loop, headers={"User-Agent": info.NAME})

    @commands.command(
        aliases=["ew", "w", "wiki"]
    )
    async def esowiki(self, ctx, *, esolang_name):
        """Link to the Esolang Wiki page for an esoteric programming language."""
        url = f"https://esolangs.org/wiki/{parse.quote(esolang_name)}"
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
                        description=f"**{esolang_name.capitalize()}** is not on the Esolangs wiki. Make sure the capitalization is correct."
                    ))

    @commands.group(
        aliases=["run", "exe", "execute"],
        invoke_without_command=True
    )
    async def interpret(self, ctx, language, *, flags=""):
        """Interpret a program in an esoteric programming language."""
        program = None

        if language in os.listdir("programs"):
            with open(f"programs/{language}") as f:
                language = f.readline().strip()
                program = f.read()

        try:
            interpreter = importlib.import_module(f"languages.{language.lower()}")
        except ImportError:
            await ctx.send(embed=make_embed(
                color=colors.EMBED_ERROR,
                title="Error",
                description=f"**{esolang_name.capitalize()}** has no interpreter at this point in time. Consider sending a pull request to add an interpreter."
            ))

        if not program:
            await ctx.send("Enter a program as a message or an attachment.")
            async def check(message):
                return (message.channel == ctx.channel and
                       (message.content or message.attachments) and 
                        message.author != self.bot.user)
            program_msg = await self.bot.wait_for("message", check=check)
            if program_msg.attachments:
                string = io.StringIO()
                program_msg.save(string)
                program = string.read()
            else:
                program = program_msg.content

        console = await ctx.send("```\n```")
        await interpreter.interpret(program, flags, DiscordInput(self.bot, ctx.channel), DiscordOutput(console))

    @interpret.command(
        aliases=["saves", "uploaded"]
    )
    async def saved(self, ctx):
        """Get a list of saved programs."""
        await ctx.send("\n".join(os.listdir("programs")))

    @interpret.command(
        aliases=["save", "sv", "upl"]
    )
    async def upload(self, ctx, language):
        """Upload a program to save."""
        if not ctx.message.attachments:
            await ctx.send("Please attach a file to upload as a program.")
            return
        if os.path.exists(f"programs/{attach.filename}"):
            await ctx.send("A program with this name has already been uploaded.")
            return

        attach = ctx.message.attachments[0]
        with open(f"programs/{attach.filename}", "wb") as f:
            f.write((language + "\n").encode())
            await attach.save(f)
        
        await ctx.send(f"Successfully saved `{attach.filename}`.")

def setup(bot):
    bot.add_cog(Esolangs(bot))
