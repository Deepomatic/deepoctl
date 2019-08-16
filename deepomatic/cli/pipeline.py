import os
import sys
import logging
import threading
from .thread_base import Pool, Thread, MainLoop, CurrentMessages, blocking_lock, QUEUE_MAX_SIZE
from .cmds.infer import SendInferenceGreenlet, ResultInferenceGreenlet, PrepareInferenceThread
from tqdm import tqdm
from .common import TqdmToLogger, Queue
from .frame import CurrentFrames
from .input_data import InputThread, get_input, VideoInputData
from .output_data import OutputThread, get_outputs
from .workflow import get_workflows
from .cmds.infer import BlurImagePostprocessing, DrawImagePostprocessing

LOGGER = logging.getLogger(__name__)


class Pipeline(object):
    @classmethod
    def from_kwargs(cls, kwargs):
         # build pipeline
        input = get_input(kwargs)
        stages = get_workflows(kwargs)
        outputs = get_outputs(kwargs)

        postprocessing = (DrawImagePostprocessing(**kwargs) if kwargs['command'] == 'draw'
                            else BlurImagePostprocessing(**kwargs) if kwargs['command'] == 'blur'
                            else None)
        return cls(input, stages, outputs, postprocessing)

    def __init__(self, input, stages, outputs, postprocessing, queue_max_size=QUEUE_MAX_SIZE):
        # TODO: might need to rethink the whole pipeling for infinite streams
        # IMPORTANT: maxsize is important, it allows to regulate the pipeline and avoid to pushes too many requests to rabbitmq when we are already waiting for many results
        queues = [Queue(maxsize=queue_max_size) for _ in range(
            len(stages) * 2 + 2
        )]

        self.exit_event = threading.Event()
        self.stages = stages
        current_frames = CurrentFrames()

        # Initialize progress bar
        frame_count = input.get_frame_count()
        max_value = int(frame_count) if frame_count >= 0 else None
        tqdmout = TqdmToLogger(LOGGER, level=LOGGER.getEffectiveLevel())
        pbar = tqdm(total=max_value, file=tqdmout, desc='Input processing', smoothing=0)


        pools = []

        # Input frames
        pools.append(Pool(1, InputThread, thread_args=(self.exit_event, None, queues[0], iter(input))))

        # Encode image into jpeg
        pools.append(Pool(1, PrepareInferenceThread, thread_args=(self.exit_event, queues[0], queues[1], current_frames)))

        for i, stage in enumerate(self.stages):
            # Send inference
            skip = queues[2*i+3] if input.is_infinite() else None
            send_inference = Pool(1, SendInferenceGreenlet, thread_args=(self.exit_event, queues[2*i+1], queues[2*i+2], current_frames, stage, skip))
            # Gather inference predictions from the worker(s)
            result_inference =  Pool(1, ResultInferenceGreenlet, thread_args=(self.exit_event, queues[2*i+2], queues[2*i+3], current_frames, stage))
            pools.extend([
                send_inference,
                result_inference
            ])

        # Output frames/predictions
        pools.append(Pool(1, OutputThread, thread_args=(self.exit_event, queues[-1], None, current_frames, pbar.update, outputs, postprocessing)))

        self.loop = MainLoop(pools, queues, pbar, self.exit_event, self.close)


    def run(self):
        try:
            stop_asked = self.loop.run_forever()
        except Exception:
            self.cleanup()
            raise
    
        # If the process encountered an error, the exit code is 1.
        # If the process is interrupted using SIGINT (ctrl + C) or SIGTERM, the queues are emptied and processed by the
        # threads, and the exit code is 0.
        # If SIGINT or SIGTERM is sent again during this shutdown phase, the threads are killed, and the exit code is 2.
        if self.exit_event.is_set():
            sys.exit(1)
        elif stop_asked >= 2:
            sys.exit(2)

    def cleanup(self):
        self.loop.cleanup()

    def stop(self):
        self.loop.stop()

    def close(self):
        for stage in self.stages:
            stage.close()