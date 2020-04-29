from .utils import _SiteCommand, SiteManager


class InstallCommand(_SiteCommand):
    """
        Install a site
    """

    def run(self, site_id, **kwargs):
        app_id = SiteManager().install(site_id)
        if app_id is None:
            print('Site', site_id, 'already installed')
        else:
            print('Site', site_id, 'installed with app', app_id)
