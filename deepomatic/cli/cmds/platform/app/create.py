from ...utils import Command
from ..utils import PlatformManager


class CreateCommand(Command):
    """
        Create a new app
    """

    def setup(self, subparsers):
        parser = super(CreateCommand, self).setup(subparsers)
        parser.add_argument('app_name', type=str, help="")
        return parser

    def run(self, app_name, **kwargs):
        PlatformManager().create_app(app_name)
