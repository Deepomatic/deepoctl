from ..utils import _CurrentSiteCommand, SiteManager


class StartCommand(_CurrentSiteCommand):
    """
        start the site
    """

    def run(self, **kwargs):
        manager = SiteManager()
        print('Starting site', manager.current())
        manager.start()
        print('Site started')
