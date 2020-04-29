from deepomatic.cli.lib.site import SiteManager  # noqa: F401
from ..utils import Command


class _SiteCommand(Command):
    """
        Commands that expect a site_id
    """

    def setup(self, subparsers):
        parser = super(_SiteCommand, self).setup(subparsers)
        parser.add_argument('site_id', type=str, help="site id")
        return parser


class _CurrentSiteCommand(Command):
    """
        Commands that should work on the current site
    """
