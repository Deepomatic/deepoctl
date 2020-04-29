from ....utils import Command
from deepomatic.cli.lib.camera import get_camera_ctrl

manager = get_camera_ctrl()


class _CameraCommand(Command):
    """
        Base class for commands that requires the camera's name
    """

    def setup(self, subparsers):
        parser = super(_CameraCommand, self).setup(subparsers)
        parser.add_argument('name', type=str, help="camera name")
        return parser


class CameraCommand(Command):
    """
        Control the Camera server
    """

    class AddCommand(Command):
        """
            Add a camera
        """

        def setup(self, subparsers):
            parser = super(CameraCommand.AddCommand, self).setup(subparsers)
            parser.add_argument('name', type=str, help="camera name")
            parser.add_argument('address', type=str, help="camera address")
            parser.add_argument('--fps', type=float, help="camera fps", default=None)

            group = parser.add_mutually_exclusive_group()
            group.add_argument("--tcp", action="store_true")
            group.add_argument("--udp", action="store_true")

            return parser

        def run(self, name, address, fps, tcp, udp, **kwargs):
            print(manager.add(name, address))  # TODO: tcp/udp, fps

    class RemoveCommand(_CameraCommand):
        """
            Remove a camera
        """

        def run(self, name, **kwargs):
            print(manager.delete(name))

    class StartCommand(_CameraCommand):
        """
            Start a camera
        """

        def run(self, name, **kwargs):
            print(manager.start(name))

    class StopCommand(_CameraCommand):
        """
            Stop a camera
        """

        def run(self, name, **kwargs):
            print(manager.stop(name))

    class StatusCommand(_CameraCommand):
        """
            Get a camera's status
        """

        def run(self, name, **kwargs):
            print(manager.status(name))

    class ListCommand(Command):
        """
            List the cameras
        """

        def run(self, **kwargs):
            print(manager.list())
