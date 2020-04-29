from ...utils import Command


class CurrentCommand(Command):
    """
        Control the current site
    """

    from .start import StartCommand
    from .stop import StopCommand
    from .logs import LogsCommand
    from .status import StatusCommand

    from .camera import CameraCommand
