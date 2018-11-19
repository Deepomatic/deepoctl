import os
import sys
import io
import json
import cv2
import logging
import progressbar
import numpy as np

import deepoctl.cmds.infer as infer
import deepoctl.io_data as io_data
import deepoctl.workflow_abstraction as wa


class BlurThread(infer.InferenceThread):
    def __init__(self, input_queue, output_queue, **kwargs):
        super(BlurThread, self).__init__(input_queue, output_queue, **kwargs)
        self.process = io_data.BlurOutputData(**kwargs)

    def processing(self, frame, prediction):
        return self.process(frame, prediction)

def main(args, force=False):
    try:
        io_data.input_loop(args, BlurThread)
    except KeyboardInterrupt:
        pass
    except:
        logging.error("Unexpected error: %s" % sys.exc_info()[0])