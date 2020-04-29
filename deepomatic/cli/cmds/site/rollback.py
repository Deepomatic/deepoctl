from .utils import _CurrentSiteCommand, SiteManager


class RollbackCommand(_CurrentSiteCommand):
    """
        Rollback a site
    """

    def setup(self, subparsers):
        parser = super(RollbackCommand, self).setup(subparsers)
        parser.add_argument('n', nargs='?', type=int, help="how far back to rollback", default=1)
        return parser

    def run(self, n, **kwargs):
        print(SiteManager().rollback(n))
