import io
from PIL import Image
from ..common import Queue
from .workflow_abstraction import AbstractWorkflow
from .rpc_workflow import import_rpc_package, requires_deepomatic_rpc
from ..exceptions import ResultInferenceError, ResultInferenceTimeout
from ..exceptions import DeepoRPCRecognitionError, DeepoRPCUnavailableError
from ..exceptions import DeepoCLIException

rpc, protobuf = import_rpc_package()

@requires_deepomatic_rpc
class RpcWorkflow(AbstractWorkflow):

    @requires_deepomatic_rpc
    class WorfklowServiceStub(object):
        def __init__(self, channel):
            """Constructor.
            Args:
            channel: A grpc.Channel.
            """
            self.ExecuteWorkflow = channel.unary_unary(
                '/buffers.protobuf.workflows.WorkflowExecutor/ExecuteWorkflow',
                request_serializer=rpc.buffers.protobuf.workflows.WorkflowExecution_pb2.WorkflowRequest.SerializeToString,
                response_deserializer=rpc.buffers.protobuf.workflows.WorkflowExecution_pb2.WorkflowResponse.FromString,
            )
            self.ExecuteWorkflowStream = channel.stream_stream(
                '/buffers.protobuf.workflows.WorkflowExecutor/ExecuteWorkflowStream',
                request_serializer=rpc.buffers.protobuf.workflows.WorkflowExecution_pb2.WorkflowRequest.SerializeToString,
                response_deserializer=rpc.buffers.protobuf.workflows.WorkflowExecution_pb2.WorkflowResponse.FromString,
            )

    @requires_deepomatic_rpc
    class InferResult(AbstractWorkflow.AbstractInferResult):
        def get_response(self, timeout):
            raise NotImplementedError()

        def get_predictions(self, timeout):
            response = self.get_response(timeout)
            # regions = response.flow_container["TODO"].regions
            
            d = protobuf.json_format.MessageToDict(response,
                including_default_value_fields=True,
                preserving_proto_field_name=True)

            regions = d["flow_container"]["workflow_data"]["image_input"]["regions"]
            predicted = []
            for region in regions:
                roi = region["roi"]
                concepts = region["concepts"]
                for concept in concepts.values():
                    if "predictions" in concept:
                        predictions = concept["predictions"]["predictions"]
                        for prediction in predictions:
                            predicted.append({
                                "roi": roi,
                                "label_id": prediction['label_id'],
                                "label_name": prediction['label_name'],
                                "score": prediction['score']
                            })
                    else:
                        pass # TODO image, text, number

            predictions = {
                'outputs': [
                    {
                        'labels': {
                            'predicted': predicted
                        }
                    }
                ]
            }
            return predictions


    @requires_deepomatic_rpc
    class InferAMQPResult(InferResult):
        def __init__(self, consumer, correlation_id=None):
            self._correlation_id = correlation_id
            self._consumer = consumer

        def get_response(self, timeout):
            try:
                response = self._consumer.get(correlation_id=self._correlation_id, timeout=timeout)
                return rpc.buffers.protobuf.workflows.WorkflowExecution_pb2.WorkflowResponse.FromString(response.body)
            except rpc.amqp.exceptions.Timeout:
                raise ResultInferenceTimeout(timeout)

    @requires_deepomatic_rpc
    class InferGRPCResult(InferResult):
        def __init__(self, future):
            self._future = future

        def get_response(self, timeout):
            return self._future.result()

    def __init__(self, workflow_server, amqp_url, routing_key):
        super(RpcWorkflow, self).__init__('workflow')
        self.workflow_server = workflow_server
        self.amqp_url = amqp_url
        self.routing_key = routing_key

        self._durable = True # TODO

        try:
            import grpc
        except ImportError:
            raise DeepoCLIException("gRPC is not installed")

        self._input_queue = Queue()

        self._channel = grpc.insecure_channel('%s' % self.workflow_server)
        try:
            grpc.channel_ready_future(self._channel).result(timeout=5)
        except grpc.FutureTimeoutError:
            raise DeepoCLIException("Cannot connect to gRPC server at %s" % self.workflow_server)

        self._stub = RpcWorkflow.WorfklowServiceStub(self._channel)
        # self._stream = self._stub.ExecuteWorkflowStream.future(iter(self._input_queue.get, None))
        
        if amqp_url and routing_key:
            self.return_flow_container = False
            self._consume_client = rpc.client.Client(self.amqp_url)
            if self._durable:
                self._queue, self._consumer = self._consume_client.new_consuming_queue(queue_name=self.routing_key)
            else:
                self._queue = self._consume_client.amqp_client.force_declare_tmp_queue(routing_key=self.routing_key, exchange=self._consume_client.amqp_exchange)
                self._consumer =  self._consume_client.amqp_client.force_declare_lru_consumer([self._queue])
                self._consumer.consume()
        else:
            self.return_flow_container = True

    def close_client(self, client):
        if client is not None:
            client.amqp_client.ensured_connection.close()

    def new_client(self):
        return None

    def close(self):
        if self._channel is not None:
            self._channel.close()
            self._channel = None
            self._stub = None
            self._queue = None
        self.close_client(self._consume_client)

    def infer(self, encoded_image_bytes, _None, _useless_frame_name):
        request = rpc.buffers.protobuf.workflows.WorkflowExecution_pb2.WorkflowRequest()
        request.workflow_input['image_input'].image = encoded_image_bytes
        request.return_flow_container = self.return_flow_container
        if request.return_flow_container:
            return self.InferGRPCResult(self._stub.ExecuteWorkflow.future(request))
        else:
            request.output_queue_name = self.routing_key
            self._input_queue.put(request)
            return self.InferAMQPResult(self._consumer)
