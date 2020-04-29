from ..utils import Command
from .utils import SiteManager


class LoadCommand(Command):
    """
        Load a site from an archive
    """

    def setup(self, subparsers):
        parser = super(LoadCommand, self).setup(subparsers)
        parser.add_argument('archive', type=str, help="path to archive")
        return parser

    def run(self, archive, **kwargs):
        SiteManager().load(archive)
