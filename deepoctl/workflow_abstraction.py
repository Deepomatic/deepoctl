import os
import logging
import datetime
import deepomatic
from deepomatic.exceptions import TaskTimeout, TaskError

import deepoctl.common as common
import deepoctl.input_data as input_data

class AbstractWorkflow(object):
    class AbstractInferResult(object):
        def get(self):
            raise NotImplemented

    def __init__(self, display_id):
        self._display_id = display_id

    @property
    def display_id(self):
        return self._display_id

    def infer(self, frame):
        """Should return a subclass of AbstractInferResult"""
        raise NotImplemented

    def get_json_output_filename(self, file):
        dirname = os.path.dirname(file)
        filename, ext = input_data.splitext(file)
        return os.path.join(dirname, filename + '.{}.json'.format(self.display_id))


class CloudRecognition(AbstractWorkflow):
    class InferResult(AbstractWorkflow.AbstractInferResult):
        def __init__(self, task):
            self._task = task

        def get(self):
            try:
                return self._task.wait().data()['data']
            except (TaskTimeout, TaskError) as e:
                return None

    def __init__(self, recognition_version_id):
        super(CloudRecognition, self).__init__('r{}'.format(recognition_version_id))
        self._id = recognition_version_id

        app_id = os.getenv('DEEPOMATIC_APP_ID', None)
        api_key = os.getenv('DEEPOMATIC_API_KEY', None)
        if app_id is None or api_key is None:
            raise common.DeepoCTLException('Please define the environment variables DEEPOMATIC_APP_ID and DEEPOMATIC_API_KEY to use cloud-based recognition models.')
        self._client = deepomatic.Client(app_id, api_key)
        self._model = None
        try:
            recognition_version_id = int(recognition_version_id)
        except ValueError:
            logging.warning("Cannot cast recognition ID into a number, trying with a public recognition model")
            self._model = self._client.RecognitionSpec.retrieve(recognition_version_id)
        if self._model is None:
            self._model = self._client.RecognitionVersion.retrieve(recognition_version_id)

    def infer(self, frame):
        return self.InferResult(self._model.inference(inputs=[deepomatic.ImageInput(frame, encoding="binary")], return_task=True, wait_task=False))

# ---------------------------------------------------------------------------- #

def get_workflow(args):
    mutually_exclusive_options = ['recognition_id']
    check_mutually_exclusive = sum([int(getattr(args, option) is not None) for option in mutually_exclusive_options])
    if check_mutually_exclusive != 1:
        raise common.DeepoCTLException('Exactly one of those options must be specified: {}'.format(', '.join(mutually_exclusive_options)))

    if args.recognition_id is not None:
        workflow = CloudRecognition(args.recognition_id)
    else:
        raise Exception('This should not happen: hint for deepomatic developers: ')
    return workflow
