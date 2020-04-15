from .site import SiteCommand
from .platform import PlatformCommand
from .system import SystemCommand

AVAILABLE_COMMANDS = [SiteCommand(), PlatformCommand(), SystemCommand()]
