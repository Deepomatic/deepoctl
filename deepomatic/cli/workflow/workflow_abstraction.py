import os


class InferenceError(Exception):
    def __init__(self, error):
        super(InferenceError, self).__init__(str(error))
        self.error = error


class InferenceTimeout(Exception):
    def __init__(self, timeout=None):
        self.timeout = timeout
        error = 'timeout reached'
        if timeout is not None:
            error += ' after {}'.format(timeout)
        super(InferenceTimeout, self).__init__(error)


class AbstractWorkflow(object):
    class AbstractInferResult(object):
        def __init__(self, threshold):
            self.threshold = threshold

        def filter_by_threshold(self, predictions):
            if self.threshold is not None:
                # Keep only predictions higher than threshold
                for output in predictions['outputs']:
                    labels = output['labels']
                    labels['predicted'] = [prediction 
                        for prediction in labels['predicted']+labels['discarded']
                            if prediction['score'] >= self.threshold]
                    labels['discarded'] = [prediction 
                            for prediction in labels['predicted']+labels['discarded']
                                if prediction['score'] < self.threshold]
            return predictions

        def get_predictions(self):
            raise NotImplementedError()

    def new_client(self):
        return None

    def close_client(self, client):
        pass

    def close(self):
        raise NotImplementedError()

    def infer(self, encoded_image_bytes, push_client):
        """Should return a subclass of AbstractInferResult"""
        raise NotImplementedError()