import os
import yaml
try:
    from builtins import FileExistsError
except ImportError:
    FileExistsError = OSError

from deepomatic.api.http_helper import HTTPHelper


class PlatformManager(object):
    def __init__(self, client_cls=HTTPHelper):
        self.client = client_cls()

    def create_app(self, app_name):
        # create directory
        try:
            os.makedirs(app_name)
        except FileExistsError:
            print(app_name, 'already exists')

        # add workflow.yaml template
        workflow_path = os.path.join(app_name, 'workflow.yaml')
        with open(workflow_path, 'w') as f:
            WORKFLOW_YAML_TEMPLATE['workflow']['name'] = app_name
            yaml.dump(WORKFLOW_YAML_TEMPLATE, f, allow_unicode=True)
        custom_node_path = os.path.join(app_name, 'custom_node.py')
        with open(custom_node_path, 'w') as f:
            f.write(CUSTOM_NODE_TEMPLATE)

    def infer(self, input):
        raise NotImplementedError()

    def inspect(self, workflow_path):
        raise NotImplementedError()

    def publish_workflow(self, workflow_path):
        with open(workflow_path, 'r') as f:
            workflow = yaml.load(f, Loader=yaml.FullLoader)

        # create using workflow server
        app_specs = [{
            "queue_name": "{}.forward".format(node['name']),
            "recognition_spec_id": node['args']['spec_id']
        } for node in workflow['workflow']['nodes'] if node["type"] == "Recognition"]

        data_app = {"name": workflow['workflow']['name'], "app_specs": app_specs}
        files = {'workflow_yaml': open(workflow_path, 'r')}

        # TODO: upload custom_nodes

        ret = self._client.post('/apps-workflow/', data=data_app, files=files, content_type='multipart/mixed')
        if 'app_id' not in ret:
            print("Failed to create app: {}".format(ret))
        else:
            app_id = ret['app_id']
            print("New app created with id: {}".format(app_id))
            ret = self._client.get('/accounts/me/')
            email = ret['account']['email']
            organization = email.split('@')[0].split('-')[0]
            host = self._client.host
            print("Go to {}/{}/deployments to choose your recognition versions!".format(host, organization))

        # TODO: remove prints

    def train(self):
        raise NotImplementedError()

    def upload(self):
        raise NotImplementedError()

    def validate(self):
        # TODO: implement
        return True


# TODO: clone repo ?
CUSTOM_NODE_TEMPLATE = """
from deepomatic.workflows.nodes import CustomNode


class MyNode(CustomNode):
    def __init__(self, config, node_name, input_nodes, concepts):
        super(MyNode, self).__init__(config, node_name, input_nodes)

    def process(self, context, regions):
        return regions

"""
WORKFLOW_YAML_TEMPLATE = {
    "version": 1,
    "workflow": {
        "name": "workflow",
        "nodes": [
            {
                "name": "input",
                "type": "Input",
                "args": {
                    "type": "Image"
                }
            },
            {
                "name": "detector",
                "type": "Recognition",
                "input_nodes": [
                    "input"
                ],
                "args": {
                    "spec_id": 0,
                    "concepts": [
                        "item"
                    ]
                }
            }
        ]
    }
}
