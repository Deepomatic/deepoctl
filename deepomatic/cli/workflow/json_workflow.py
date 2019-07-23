import sys
import json
import logging
from .workflow_abstraction import AbstractWorkflow, InferenceError
from ..json_schema import is_valid_studio_json, is_valid_vulcan_json
from ..cmds.studio_helpers.vulcan2studio import transform_json_from_studio_to_vulcan
from ..exceptions import DeepoPredictionJsonError, DeepoOpenJsonError


LOGGER = logging.getLogger(__name__)


class JsonRecognition(AbstractWorkflow):

    class InferResult(AbstractWorkflow.AbstractInferResult):
        def __init__(self, frame_name, frame_pred):
            self.frame_name = frame_name
            self.frame_pred = frame_pred

        def get_predictions(self, timeout):
            return self.frame_pred

    def __init__(self, recognition_version_id, pred_file):
        super(JsonRecognition, self).__init__('r{}'.format(recognition_version_id))
        self._id = recognition_version_id
        self._pred_file = pred_file

        # Load the json
        try:
            with open(pred_file) as json_file:
                vulcan_json_with_pred = json.load(json_file)
        except Exception:
            raise DeepoOpenJsonError("Prediction JSON file {} is not a valid JSON file".format(pred_file))

        # Check json validity
        if is_valid_vulcan_json(vulcan_json_with_pred):
            LOGGER.debug("Vulcan prediction JSON {} validated".format(pred_file))
        elif is_valid_studio_json(vulcan_json_with_pred):
            vulcan_json_with_pred = transform_json_from_studio_to_vulcan(vulcan_json_with_pred)
            LOGGER.debug("Studio prediction JSON {} validated and transformed to Vulcan format".format(pred_file))
        else:
            raise DeepoPredictionJsonError("Prediction JSON file {} is neither a proper Studio or Vulcan JSON file".format(pred_file))

        # Store predictions for easy access
        self._all_predictions = {vulcan_pred['data']['framename']: vulcan_pred for vulcan_pred in vulcan_json_with_pred}

    def close(self):
        pass

    def infer(self, _useless_encoded_image_bytes, _useless_push_client, frame_name):
        # _useless_encoded_image_bytes and _useless_push_client are used only for rpc and cloud workflows
        try:
            frame_pred = self._all_predictions[frame_name]
        except Exception:
            raise InferenceError("Could not find predictions for frame {}".format(frame_name))

        return self.InferResult(frame_name, frame_pred)
