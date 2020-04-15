from .utils import SiteManager, _SiteCommand


class UseCommand(_SiteCommand):
    """
        use a site
    """

    def run(self, site_id, **kwargs):
        SiteManager().use(site_id)

        # TODO: feedback
        # print('Now using', site_id)
        # print(site_id, 'does not exist')
