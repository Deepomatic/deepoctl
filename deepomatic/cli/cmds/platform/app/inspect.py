from ...utils import Command
from ..utils import PlatformManager


class InspectCommand(Command):
    """
        Inspect a workflow
    """

    def setup(self, subparsers):
        parser = super(InspectCommand, self).setup(subparsers)
        parser.add_argument('workflow_path', type=str, help="")
        parser.add_argument('-f', '--file', type=str, help="workflow file name", default="workflow.yaml")
        return parser

    def run(self, workflow_path, **kwargs):
        PlatformManager.inspect(workflow_path)
