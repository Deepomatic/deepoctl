import sys
import argparse
from deepocli.cmds.infer import main as infer
from deepocli.cmds.draw import main as draw
from deepocli.cmds.feedback import main as feedback
from deepocli.cmds.blur import main as blur
from deepocli.io_data import ImageInputData, VideoInputData, StreamInputData


def argparser_init():
    argparser = argparse.ArgumentParser(prog='deepo')
    subparsers = argparser.add_subparsers(dest='command', help='')
    subparsers.required = True

    infer_parser = subparsers.add_parser('infer', help="Computes prediction on a file or directory and outputs results as a JSON file.")
    infer_parser.set_defaults(func=infer)

    draw_parser = subparsers.add_parser('draw', help="Generates new images and videos with predictions results drawn on them. Computes prediction if JSON has not yet been generated.")
    draw_parser.set_defaults(func=draw)

    blur_parser = subparsers.add_parser('blur', help="Generates new images and videos with predictions results blurred on them. Computes prediction if JSON has not yet been generated.")
    blur_parser.set_defaults(func=blur)

    feedback_parser = subparsers.add_parser('feedback', help='Uploads images from the local machine to Deepomatic Studio.')
    feedback_parser.set_defaults(func=feedback, recursive=False)

    parsers = [infer_parser, draw_parser, blur_parser]
    for parser in parsers:
        parser.add_argument('-i', '--input', help="Path on which inference should be run. It can be an image (supported formats: *{}), a video (supported formats: *{}) or a directory. If the given path is a directory, it will recursively run inference on all the supported files in this directory.".format(', *'.join(ImageInputData.supported_formats), ', *'.join(VideoInputData.supported_formats)))
        parser.add_argument('-o', '--output', help="Path in which output should be written. It can be an image (supported formats: *{}), a video (supported formats: *{}) or a directory.".format(', *'.join(ImageInputData.supported_formats), ', *'.join(VideoInputData.supported_formats)))
        parser.add_argument('-r', '--recognition_id', help="Neural network recognition version ID.")
        parser.add_argument('-u', '--amqp_url', help="AMQP url for on-premises deployments.")
        parser.add_argument('-k', '--routing_key', help="Recognition routing key for on-premises deployments.")
        parser.add_argument('-t', '--threshold', help="Threshold above which a prediction is considered valid.", default=0.7)
        parser.add_argument('--output_fps', help="In case of video output, video frame rate.", default=25)
        parser.add_argument('--fullscreen', help="Fullscreen if window output.", action="store_true")

    draw_parser.add_argument('--draw_scores', help="Overlays the prediction scores.", action="store_true")
    draw_parser.add_argument('--draw_labels', help="Overlays the prediction labels.", action="store_true")

    blur_parser.add_argument('--blur_method', help="Blur method to apply, either 'pixel', 'gaussian' or 'black'. Defaults to 'pixel'.", default="pixel")
    blur_parser.add_argument('--blur_strength', help="Blur strength, defaults to 10.", default=10)

    feedback_parser.add_argument('-d', '--dataset', help="Deepomatic Studio dataset name.", type=str)
    feedback_parser.add_argument('-o', '--organization', help="Deepomatic Studio organization slug.", type=str)
    feedback_parser.add_argument('path', type=str, nargs='+', help='Path to an image file, images directory or json file or directory.')
    feedback_parser.add_argument('--recursive', dest='recursive', action='store_true', help='Goes through all files in subdirectories.')
    feedback_parser.add_argument('--json', dest='json_file', action='store_true', help='Look for JSON files instead of images.')

    return argparser

def run(args):
    # Initialize the argparser
    argparser = argparser_init()

    # Display the help section if no arguments are supplied
    if len(sys.argv)==1:
        argparser.print_help(sys.stderr)
        sys.exit(1)
    # Otherwise parse the arguments and run the command
    else:
        args = argparser.parse_args(args)
        args.func(vars(args))
