from ..utils import _CurrentSiteCommand, SiteManager


class LogsCommand(_CurrentSiteCommand):
    """
        Get the logs of the running site
    """

    def run(self, **kwargs):
        SiteManager().logs()
