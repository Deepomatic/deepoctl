from .utils import _CurrentSiteCommand, SiteManager


class ShowCommand(_CurrentSiteCommand):
    """
        Show the site
    """

    def run(self, **kwargs):
        print('site:', SiteManager().current())
        print('app', SiteManager().current_app())
