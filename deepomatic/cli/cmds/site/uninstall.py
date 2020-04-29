from .utils import _SiteCommand, SiteManager


class UninstallCommand(_SiteCommand):
    """
        Uninstall a site
    """

    def run(self, site_id, **kwargs):
        SiteManager().uninstall(site_id)
        # TODO: feedback
