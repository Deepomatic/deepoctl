from ..utils import _CurrentSiteCommand, SiteManager


class LogsCommand(_CurrentSiteCommand):
    """
        get the logs of the running site
    """

    def run(self, **kwargs):
        SiteManager().logs()
