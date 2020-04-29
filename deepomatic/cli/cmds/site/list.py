from ..utils import Command
from .utils import SiteManager


class ListCommand(Command):
    """
        Get the list of installed sites
    """

    def run(self, **kwargs):
        print('\n'.join(SiteManager().list()))
