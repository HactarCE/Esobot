from .command import *
from . import management

commands.sort(key=lambda c: c.help_syntax)
