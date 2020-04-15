from ..utils import _CurrentSiteCommand, SiteManager


class StartCommand(_CurrentSiteCommand):
    """
        start the site
    """

    def run(self, **kwargs):
        SiteManager().start()
