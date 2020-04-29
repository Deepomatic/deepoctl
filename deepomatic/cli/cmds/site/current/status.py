from ..utils import _CurrentSiteCommand, SiteManager


class StatusCommand(_CurrentSiteCommand):
    """
        Get the site status
    """

    def run(self, **kwargs):
        SiteManager().status()
