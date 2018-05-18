import re
import logging

l = logging.getLogger('bot')

commands = []

PRETTY_COMMAND_PREFIX = r'!'
COMMAND_PREFIX = r'^!\s*'  # TODO also support @mentions
COMMAND_SUFFIX = r'([\s\S]*)$'


class Command(object):
    def __init__(self, handler, regex, help_syntax, help_summary, help_full=None, aliases=[], hidden=False):
        """Decorator handler for bot commands

        Parameters:
        handler -- a handler taking a discord.Client, a list of strings (arguments to the command) and a message object
        regex -- a regex string to be matched after COMMAND_PREFIX
        help_syntax -- a short description of the command syntax (should not include prefix)
        help_summary -- a short description of the command's purpose
        help_full -- a longer (possibly multiline) documentation of the command (default None)
        aliases -- a list of command aliases to be shown to the user (default [])
        hidden -- if True, then this command will not appear in the main command list (default False)
        """
        self.handler = handler
        self.regex = regex
        self.explicit_matcher = re.compile(rf'{COMMAND_PREFIX}({regex})(\s+{COMMAND_SUFFIX})?')
        self.implicit_matcher = re.compile(rf'({regex})(\s+{COMMAND_SUFFIX})?')
        self.help_syntax = help_syntax
        self.help_summary = help_summary
        self.help_full = help_full
        self.aliases = aliases
        self.hidden = hidden

    def matches(self, message):
        """Returns Truthy if the message matches; otherwise returns Falsey."""
        match = self.explicit_matcher.fullmatch(message.content)
        if not match and message.channel.is_private and len(message.channel.recipients) == 2:
            match = self.implicit_matcher.fullmatch(message.content)
        # if match:
        #     l.debug(f"Matched command '{self.help_syntax}'")
        # else:
        #     l.debug(f"Did not match command '{self.help_syntax}'")
        return match

    def implicitly_matches(self, string):
        # TODO Add docstring
        return self.implicit_matcher.fullmatch(string)

    async def run_if_matches(self, client, message):
        """Runs command handler and returns Truthy if the message matches; otherwise returns Falsey."""
        # l.debug(f"run_if_matches '{self.help_syntax}'")
        match = self.matches(message)
        if match:
            l.debug(f"Running command '{self.help_syntax}'")
            await self.handler(client, (match.groups()[-1] or '').split(), message)
        return match


def command(*args, **kwargs):
    """Returns a decorator that register a function as a command.
    All arguments are passed to Command().
    """
    def decorate(f):
        commands.append(Command(f, *args, **kwargs))
        return f
    return decorate


def get_matching_command(message):
    """Returns the first matching command or None."""
    return next((c for c in commands if c.matches(message)), None)

def get_matching_implicit_command(string):
    return next((c for c in commands if c.implicitly_matches(string)), None)
