from .utils import _SiteCommand, SiteManager


class InstallCommand(_SiteCommand):
    """
        install a site
    """

    def run(self, site_id, **kwargs):
        SiteManager().install(site_id)
