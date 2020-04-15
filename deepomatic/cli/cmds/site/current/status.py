from ..utils import _CurrentSiteCommand, SiteManager


class StatusCommand(_CurrentSiteCommand):
    """
        get the site status
    """

    def run(self, **kwargs):
        SiteManager().status()
