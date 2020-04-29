from ...utils import Command
from ..utils import PlatformManager


class ValidateCommand(Command):
    """
        Validate workflow
    """

    def run(self, path=".", **kwargs):
        # TODO: feedback
        if PlatformManager().validate(path):
            print('Your workflow is valid')
        else:
            print('Your workflow is invalid')
