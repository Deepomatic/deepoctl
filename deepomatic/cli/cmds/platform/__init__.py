from ..utils import Command


class PlatformCommand(Command):
    """
        Operations on the Deepomatic Platform (studio)
    """

    from .upload import UploadCommand
    from .train import TrainCommand
    from .app import AppCommand
