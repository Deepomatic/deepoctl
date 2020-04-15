from ..utils import Command


class SiteCommand(Command):
    """
        Operations on your site (local or cloud)
        You can choose from the following commands to manage your local sites
    """

    from .use import UseCommand
    from .create import CreateCommand
    from .list import ListCommand
    from .load import LoadCommand
    from .save import SaveCommand
    from .upgrade import UpgradeCommand
    from .install import InstallCommand
    from .uninstall import UninstallCommand

    from .rollback import RollbackCommand
    from .show import ShowCommand

    from .current import CurrentCommand
