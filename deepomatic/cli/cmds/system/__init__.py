from ..utils import Command
from deepomatic.cli.lib.system import SystemManager


class SystemCommand(Command):
    """
        System command
    """

    class SetupCommand(Command):
        """
            Setup the system
        """

        def run(self, **kwargs):
            SystemManager().setup()

    class CheckCommand(Command):
        """
            Check the system
        """

        def run(self, **kwargs):
            SystemManager().check()
