from .utils import SiteManager, _SiteCommand


class UseCommand(_SiteCommand):
    """
        Use a site
    """

    def run(self, site_id, **kwargs):
        if SiteManager().use(site_id):
            print('Now using', site_id)
        else:
            print(site_id, 'is not installed')
