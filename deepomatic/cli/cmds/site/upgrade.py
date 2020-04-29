from .utils import _CurrentSiteCommand, SiteManager


class UpgradeCommand(_CurrentSiteCommand):
    """
        Upgrade a site
    """

    def run(self, **kwargs):
        manager = SiteManager()
        site_id = manager.current()
        app_id = manager.upgrade()
        if app_id is None:
            print('Site is up-to-date')
        else:
            print('Site', site_id, 'upgraded with app', app_id)
