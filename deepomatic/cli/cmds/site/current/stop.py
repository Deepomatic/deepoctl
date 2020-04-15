from ..utils import _CurrentSiteCommand, SiteManager


class StopCommand(_CurrentSiteCommand):
    """
        stop the site
    """

    def run(self, **kwargs):
        SiteManager().stop()
        # TODO: feedback
