import io
import os
import math
import numpy as np
import cv2
import logging
try:
    import Queue as queue
except ImportError:
    import queue as queue

Full = queue.Full
Queue = queue.Queue
Empty = queue.Empty

LOGGER = logging.getLogger(__name__)
SUPPORTED_IMAGE_INPUT_FORMAT = ['.bmp', '.jpeg', '.jpg', '.jpe', '.png', '.tif', '.tiff']
SUPPORTED_VIDEO_INPUT_FORMAT = ['.avi', '.mp4', '.webm', '.mjpg']
SUPPORTED_FILE_INPUT_FORMAT = SUPPORTED_IMAGE_INPUT_FORMAT + SUPPORTED_VIDEO_INPUT_FORMAT
SUPPORTED_PROTOCOLS_INPUT = ['rtsp', 'http', 'https']
SUPPORTED_IMAGE_OUTPUT_FORMAT = SUPPORTED_IMAGE_INPUT_FORMAT
SUPPORTED_VIDEO_OUTPUT_FORMAT = ['.avi', '.mp4']


class TqdmToLogger(io.StringIO):
    """Tqdm output stream to play nice with logger."""
    logger = None
    level = None
    buf = ''

    def __init__(self, logger, level=None):
        super(TqdmToLogger, self).__init__()
        self.logger = logger
        self.level = level or logging.INFO

    def write(self, buf):
        self.buf = buf.strip('\r\n\t ')

    def flush(self):
        self.logger.log(self.level, self.buf)


def clear_queue(queue):
    with queue.mutex:
        queue.queue.clear()


def write_frame_to_disk(frame, path):
    if frame.output_image is not None:
        if os.path.isfile(path):
            LOGGER.warning('File {} already exists. Skipping it.'.format(path))
        else:
            LOGGER.debug('Writing file {} to disk'.format(path))
            cv2.imwrite(path, frame.output_image)
    else:
        LOGGER.warning('No frame to output.')
    return


def packing(images):
    area = sum([image.shape[0] * image.shape[1] for image in images])
    maxWidth = max([image.shape[1] for image in images])
    maxHeight = max([image.shape[0] for image in images])

    # sort the boxes for insertion by height, descending
    boxes = [
        {'x': 0, 'y': 0, 'image': image } for image in sorted(images, key=lambda i: -i.shape[0])
    ]
    # aim for a squarish resulting container,
    # slightly adjusted for sub-100% space utilization
    startWidth = math.ceil(math.sqrt(len(images))) * maxWidth
    width = 0
    height = 0
    # start with a single empty space, unbounded at the bottom
    spaces = [{'x': 0, 'y': 0, 'w': startWidth, 'h': np.inf}]
    for box in boxes:
        image = box['image']
        # look through spaces backwards so that we check smaller spaces first
        for i in range(len(spaces) - 1, -1, -1):
            space = spaces[i]

            # look for empty spaces that can accommodate the current box
            if (image.shape[1] > space['w'] or image.shape[0] > space['h']):
                continue

            # found the space; add the box to its top-left corner
            # |-------|-------|
            # |  box  |       |
            # |_______|       |
            # |         space |
            # |_______________|
            box['x'] = space['x']
            box['y'] = space['y']

            height = max(height, box['y'] + image.shape[0])
            width = max(width, box['x'] + image.shape[1])


            if (image.shape[1] == space['w'] and image.shape[0] == space['h']):
                # space matches the box exactly; remove it
                last = spaces.pop()
                if (i < len(spaces)):
                    spaces[i] = last

            elif (image.shape[0] == space['h']):
                # space matches the box height; update it accordingly
                # |-------|---------------|
                # |  box  | updated space |
                # |_______|_______________|
                space['x'] += image.shape[1]
                space['w'] -= image.shape[1]

            elif (image.shape[1] == space['w']):
                # space matches the box width; update it accordingly
                # |---------------|
                # |      box      |
                # |_______________|
                # | updated space |
                # |_______________|
                space['y'] += image.shape[0]
                space['h'] -= image.shape[0]

            else:
                # otherwise the box splits the space into two spaces
                # |-------|-----------|
                # |  box  | new space |
                # |_______|___________|
                # | updated space     |
                # |___________________|
                spaces.append({
                    'x': space['x'] + image.shape[1],
                    'y': space['y'],
                    'w': space['w'] - image.shape[1],
                    'h': image.shape[0]
                })
                space['y'] += image.shape[0]
                space['h'] -= image.shape[0]
            break
    bg = np.zeros((height, width, 3), dtype=np.uint8)
    for box in boxes:
        y = box['y']
        x = box['x']
        image = box['image']
        h, w, c = image.shape
        bg[y:y+h,x:x+w, :] = image
    return bg