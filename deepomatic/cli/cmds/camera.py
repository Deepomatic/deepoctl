# -*- coding: utf-8 -*-

import os
import logging
from contextlib import contextmanager
from deepomatic.api.http_helper import HTTPHelper
from . import parser_helpers
from ..version import __title__, __version__
from ..common import (SUPPORTED_IMAGE_OUTPUT_FORMAT,
                      SUPPORTED_VIDEO_OUTPUT_FORMAT)

###############################################################################


LOGGER = logging.getLogger(__name__)

DEFAULT_USER_AGENT_PREFIX = user_agent_prefix = '{}/{}'.format(
    __title__, __version__)

CLIENT = None

###############################################################################


class CameraCtrl(object):
    def __init__(self, client):
        self.client = client

    def add(self, name, address):
        return self.client.post('/cameras', json={
            "name": name,
            "address": address,
        })

    def delete(self, name):
        return self.client.delete('/cameras/{}'.format(name))

    def start(self, name):
        return self.client.post('/cameras/{}/start'.format(name))

    def stop(self, name):
        return self.client.post('/cameras/{}/stop'.format(name))

    def list(self):
        return self.client.get('/cameras')


def get_client():
    global CLIENT
    if CLIENT is None:
        camera_server_url = os.environ['CAMERA_SERVER_URL']
        CLIENT = HTTPHelper(host=camera_server_url,
                            user_agent_prefix=DEFAULT_USER_AGENT_PREFIX,
                            version=None)
    return CLIENT


def get_camera_ctrl():
    return CameraCtrl(get_client())


@contextmanager
def start_stop_camera(name):
    LOGGER.info("Starting camera")
    get_camera_ctrl().start(name)
    try:
        yield
    except Exception:
        LOGGER.info("Stopping camera")
        get_camera_ctrl().stop(name)
        raise


@contextmanager
def temp_camera(name, address):
    LOGGER.info("Adding camera")
    camera = get_camera_ctrl().add(name, address)
    name = camera['name']

    try:
        with start_stop_camera(name):
            yield camera
    except Exception:
        LOGGER.info("Deleting camera")
        get_camera_ctrl().delete(name)
        raise


def add_start_camera(name, address):
    LOGGER.info("Adding camera")
    get_camera_ctrl().add(name, address)
    LOGGER.info("Starting camera")
    get_camera_ctrl().start(name)


def add(args):
    camera = get_camera_ctrl().add(args.camera_name, args.camera_address)
    LOGGER.info("Camera added: ".format(camera))


def start(args):
    get_camera_ctrl().start(args.camera_name)
    LOGGER.info("Camera '{}' started".format(args.camera_name))


def stop(args):
    get_camera_ctrl().stop(args.camera_name)
    LOGGER.info("Camera '{}' stopped".format(args.camera_name))


def delete(args):
    get_camera_ctrl().delete(args.camera_name)
    LOGGER.info("Camera '{}' delete".format(args.camera_name))


def list(args):
    cameras = get_camera_ctrl().list(args.camera_name)
    LOGGER.info("Cameras: \n{}".format(cameras))


def stream(args):
    add_start_camera(args.camera_name, args.camera_address)


def infer(args):
    with temp_camera(args.camera_name, args.camera_address):
        # get_camera_results()
        pass


def draw(args):
    with temp_camera(args.camera_name, args.camera_address):
        # draw_camera_results()
        pass

    # - draw results
    # - Disable gevent ?

    # deepo camera add name -a rtsp://
    # deepo camera start name
    # deepo camera stop  name
    # deepo camera delete name
    # deepo camera list

    # deepo camera infer -a rtsp:// -n name
    # deepo camera draw -a rtsp:// -n name


def add_parser(camera_subparser, parsers, subcmd, help_msg, add_name=True):
    parser = camera_subparser.add_parser(subcmd, help=help_msg, description=help_msg)
    func = globals()[subcmd]  # Functions must be called like subcmd
    parser.set_defaults(func=func, recursive=False)

    if add_name:
        parser.add_argument('-n', '--name', dest='camera_name', type=str,
                            required=True, help='Name of the camera.')

    parsers.append(parser)
    return parser


def setup_cmd_line_subparser(camera_subparser):

    parsers = []

    # Add camera
    parser = add_parser(camera_subparser, parsers, 'add', 'Add a camera.')
    parser.add_argument('-a', '--address', dest='camera_address', type=str,
                        required=True, help='Address of the camera (must be a URL).')

    # start, stop, delete camera
    for subcmd in ['start', 'stop', 'delete']:
        help_msg = '{} a camera.'.format(subcmd.capitalize())
        add_parser(camera_subparser, parsers, subcmd, help_msg)

    # Stream
    add_parser(camera_subparser, parsers, 'list', 'List cameras.', add_name=False)
    help_msg = ('Add and start a camera then exit.'
                'The camera will continue to transmit frames until stopped by user (for production).')
    add_parser(camera_subparser, parsers, 'stream', help_msg)

    # Infer
    help_msg = ('Add and start a temporary camera then prints aggregated inference results. '
                'When the user asks to the process (KeyboardInterrupt), '
                'the camera is stopped and deleted before exiting.')
    add_parser(camera_subparser, parsers, 'infer', help_msg, add_name=False)

    # Draw
    help_msg = ('Add and start a temporary camera then draws aggregated inference results. '
                'When the user asks to the process (KeyboardInterrupt), '
                'the camera is stopped and deleted before exiting.')
    parser = add_parser(camera_subparser, parsers, 'draw', help_msg, add_name=False)
    output_group = parser_helpers.add_common_cmd_group(parser, 'output')
    output_group.add_argument('-o', '--outputs', required=True, nargs='+', help="Output path, either an image (*{}),"
                              " a video (*{}), a json (*.json) or a directory.".format(', *'.join(SUPPORTED_IMAGE_OUTPUT_FORMAT),
                                                                                       ', *'.join(SUPPORTED_VIDEO_OUTPUT_FORMAT)))

    for parser in parsers:
        # TODO: put this in parent parser when infer commands are not in the root parser
        # And remove all calls to add_verbose_argument
        # https://stackoverflow.com/questions/7498595/python-argparse-add-argument-to-multiple-subparsers
        parser_helpers.add_verbose_argument(parser)
