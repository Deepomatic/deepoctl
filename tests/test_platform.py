import os.path
from deepomatic.cli.cli_parser import run
from contextlib import contextmanager
from utils import modified_environ


ROOT = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_PATH = ROOT + '/workflow.yaml'
CUSTOM_NODES_PATH = ROOT + '/custom_nodes.py'


def call_deepo(args, api_key=None):
    args = args.split()
    if api_key:
        with modified_environ(DEEPOMATIC_API_KEY=api_key):
            res = run(args)
    else:
        res = run(args)
    try:
        return res.strip()
    except Exception:
        return res


@contextmanager
def app():
    args = "platform app create -n test -d abc -w {} -c {}".format(WORKFLOW_PATH, CUSTOM_NODES_PATH)
    result = call_deepo(args)
    msg, app_id = result.split(':')
    assert msg == "New app created with id"

    yield app_id

    args = "platform app delete --id {}".format(app_id)
    result = call_deepo(args)


@contextmanager
def app_version():
    with app() as app_id:
        args = "platform app-version create -n test_av -d abc -a {} -r 44363 44364".format(app_id)
        result = call_deepo(args)
        _, app_version_id = result.split(':')

        yield app_version_id.strip(), app_id
        args = "platform app-version delete --id {}".format(app_version_id)
        result = call_deepo(args)


class TestPlatform(object):
    def test_app(self):
        args = "platform app create -n test -d abc -w {} -c {}".format(WORKFLOW_PATH, CUSTOM_NODES_PATH)
        result = call_deepo(args)
        message, app_id = result.split(':')
        assert message == 'New app created with id'

        args = "platform app update --id {} -d ciao".format(app_id)
        message = call_deepo(args)
        assert message == 'App{} updated'.format(app_id)

        args = "platform app delete --id {}".format(app_id)
        message = call_deepo(args)
        assert message == 'App{} deleted'.format(app_id)

    def test_appversion(self):
        with app() as app_id:
            args = "platform app-version create -n test_av -d abc -a {} -r 44363 44364".format(app_id)
            result = call_deepo(args)
            message, app_version_id = result.split(':')
            assert message == 'New app version created with id'

            args = "platform app-version update --id {} -d ciao".format(app_version_id)
            message = call_deepo(args)
            assert message == 'App version{} updated'.format(app_version_id)

            args = "platform app-version delete --id {}".format(app_version_id)
            message = call_deepo(args)
            assert message == 'App version{} deleted'.format(app_version_id)

    def test_service(self):
        for service in ['customer-api', 'camera-server']:
            with app() as app_id:
                args = "platform service create -a {} -n {}".format(app_id, service)
                result = call_deepo(args)
                message, service_id = result.split(':')
                assert message == 'New service created with id'

                args = "platform service delete --id {}".format(service_id)
                message = call_deepo(args)
                assert message == 'Service{} deleted'.format(service_id)
