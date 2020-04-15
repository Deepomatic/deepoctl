from .utils import _CurrentSiteCommand, SiteManager


class UpgradeCommand(_CurrentSiteCommand):
    """
        upgrade a site
    """

    def run(self, **kwargs):
        SiteManager().upgrade()
        # TODO: feedback
        # print('Site is up-to-date')
        # print('Site', site_id, 'upgraded')
