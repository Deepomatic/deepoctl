import os
import yaml
import shutil
import subprocess

from git import Repo
from deepomatic.api.http_helper import HTTPHelper

DEEPOMATIC_SITE_PATH = os.path.join(os.environ['HOME'], '.deepomatic', 'sites')


class SiteManager(object):
    def __init__(self, path=DEEPOMATIC_SITE_PATH, client_cls=HTTPHelper):
        os.makedirs(path, exist_ok=True)
        self._repo = Repo.init(path)
        self._client = client_cls()

    def get(self, site_id):
        return self._client.get('/sites/{}'.format(site_id))

    def create(self, name, app_version_id, description=''):
        data = {
            'name': name,
            'desc': description,
            'app_version_id': app_version_id,
        }

        site = self._client.post('/sites', data=data)
        return site

    def current(self):
        return str(self._repo.head.reference)

    def current_app(self):
        return self._repo.head.commit.message

    def delete(self, site_id):
        print('DELETE /sites/{}'.format(site_id))
        # site = self._client.delete(f'/sites/{site_id}')

    def install(self, site_id):
        # TODO: stop current site
        # TODO: download docker-compose
        site = self.get(site_id)
        docker_compose = convert_to_docker_compose(site)

        try:
            # create branch
            self._repo.git.checkout(site_id, orphan=True)
        except Exception:
            # TODO: raise deepo exception
            print('Site', site_id, 'already installed')
            return

        docker_compose_path = os.path.join(self._repo.working_tree_dir, 'docker-compose.yml')
        with open(docker_compose_path, 'w') as f:
            f.write(yaml.dump(docker_compose))

        # add to index
        self._repo.index.add([docker_compose_path])

        # commit
        self._repo.index.commit(site['app']['id'])

    def list(self):
        return [head.name for head in self._repo.heads]

    def load(self, archive_path):
        self._repo.git.bundle('verify', archive_path)
        site_id = self._repo.git.bundle('list-heads', archive_path).split('/')[-1]
        self._repo.git.fetch(archive_path, '{}:{}'.format(site_id, site_id))

    def logs(self):
        raise NotImplementedError()

    def rollback(self, n=1):
        self._repo.git.reset("HEAD~{}".format(n), hard=True)
        return self._repo.head.commit.committed_datetime

    def save(self, site_id, archive_path):
        self._repo.git.bundle('create', archive_path, site_id)

    def start(self):
        site_id = self.current()
        with open("/dev/null", "w") as null:
            subprocess.call(["docker-compose", "-f", os.path.join(DEEPOMATIC_SITE_PATH, "docker-compose.yml"), "up", "-d"],
                            env={
                "DEEPOMATIC_SITE_ID": site_id
            },
                stdout=null,
                stderr=null
            )
            print('Site started')

    def status(self):
        raise NotImplementedError()

    def stop(self):
        with open("/dev/null", "w") as null:
            subprocess.call(["docker-compose", "-f", os.path.join(DEEPOMATIC_SITE_PATH,
                                                                  "docker-compose.yml"), "down", "-v"], stdout=null, stderr=null)

    def uninstall(self, site_id):
        try:
            self._repo.git.branch(site_id, D=True)
        except Exception:
            # last site, we can delete the repo
            shutil.rmtree(self._repo.working_tree_dir)

    def upgrade(self):
        # TODO: stop current site
        site_id = self.current()
        site = self.get(site_id)

        if (self._repo.head.commit.message == site['app']['id']):
            return

        docker_compose = convert_to_docker_compose(site)

        docker_compose_path = os.path.join(self._repo.working_tree_dir, 'docker-compose.yml')
        with open(docker_compose_path, 'w') as f:
            f.write(yaml.dump(docker_compose))

        # add to index
        self._repo.index.add([docker_compose_path])

        # commit
        self._repo.index.commit(site['app']['id'])

    def use(self, site_id):
        if hasattr(self._repo.heads, site_id):
            # TODO: stop current site
            getattr(self._repo.heads, site_id).checkout()
        else:
            # site does not exist
            pass


# Following won't be use when docker-compose api is done

def camera_server(id, app_id, name, docker_image, resources, circus_watchers, configuration, site_configuration):
    AMQP_USER = site_configuration.get('AMQP_USER')
    AMQP_PASSWORD = site_configuration.get('AMQP_PASSWORD')
    AMQP_VHOST = site_configuration.get('AMQP_VHOST')
    AMQP_URL = 'amqp://{AMQP_USER}:{AMQP_PASSWORD}@rabbitmq:5672/{AMQP_VHOST}'.format(
        AMQP_USER=AMQP_USER, AMQP_PASSWORD=AMQP_PASSWORD, AMQP_VHOST=AMQP_VHOST)

    return {
        "restart": "always",
        "image": "deepomatic/camera-server:master-34" if docker_image is None else docker_image,
        "environment": [
            "INIT_SYSTEM=circus",
            "AUTOSTART_SERVER=false",
            "AMQP_URL={}".format(AMQP_URL),
            "DEEPOMATIC_STORAGE_DIR=/var/lib/deepomatic/services/camera-server",
            "CAMERAS_CONFIG_DIR=/tmp/cameras",
            "WORKFLOW_SERVER_GRPC_ADDRESS=workflow-server:8080"
        ],
        "volumes": [
            "deepomatic-resources:/var/lib/deepomatic"
        ],
        "ports": [
            "80:80"
        ]
    }


def workflow_server(id, app_id, name, docker_image, resources, circus_watchers, configuration, site_configuration):
    AMQP_USER = site_configuration.get('AMQP_USER')
    AMQP_PASSWORD = site_configuration.get('AMQP_PASSWORD')
    AMQP_VHOST = site_configuration.get('AMQP_VHOST')
    AMQP_URL = 'amqp://{AMQP_USER}:{AMQP_PASSWORD}@rabbitmq:5672/{AMQP_VHOST}'.format(
        AMQP_USER=AMQP_USER, AMQP_PASSWORD=AMQP_PASSWORD, AMQP_VHOST=AMQP_VHOST)

    return {
        "restart": "always",
        "image": "deepomatic/workflow-server:master-55" if docker_image is None else docker_image,
        "environment": [
            "LOGLEVEL=DEBUG",
            "INIT_SYSTEM=circus",
            "AUTOSTART_SERVER=false",
            "AMQP_URL={}".format(AMQP_URL),
            "DEEPOMATIC_STORAGE_DIR=/var/lib/deepomatic/services/workflow-server"
        ],
        "volumes": [
            "deepomatic-resources:/var/lib/deepomatic"
        ]
    }


def neural_worker(id, app_id, name, docker_image, resources, circus_watchers, configuration, site_configuration):
    AMQP_USER = site_configuration.get('AMQP_USER')
    AMQP_PASSWORD = site_configuration.get('AMQP_PASSWORD')
    AMQP_VHOST = site_configuration.get('AMQP_VHOST')
    AMQP_URL = 'amqp://{AMQP_USER}:{AMQP_PASSWORD}@rabbitmq:5672/{AMQP_VHOST}'.format(
        AMQP_USER=AMQP_USER, AMQP_PASSWORD=AMQP_PASSWORD, AMQP_VHOST=AMQP_VHOST)

    return {
        "restart": "always",
        "image": "deepomatic/run-neural-worker:0.5.0-native",
        "runtime": "nvidia",
        "environment": [
            "GPU_IDS=0",
            "AUTOSTART_WORKER=false",
            "AMQP_URL={}".format(AMQP_URL),
            "DEEPOMATIC_STORAGE_DIR=/var/lib/deepomatic/services/worker-nn",
            "WORKFLOWS_PATH=/var/lib/deepomatic/services/worker-nn/resources/workflows.json"
        ],
        "volumes": [
            "deepomatic-resources:/var/lib/deepomatic"
        ]
    }


def get_service(name):
    if name == "worker-nn":
        return neural_worker
    elif name == "workflow-server":
        return workflow_server
    elif name == "camera-server":
        return camera_server
    else:
        raise ValueError('Unknown service {}'.format(name))


def convert_to_docker_compose(site):
    app = site["app"]
    # app_version = site["app_version"]
    site_configuration = site["site_configuration"]

    docker_compose = {
        "version": "2.4",
        "volumes": {
            "deepomatic-resources": None
        },
        "services": {
            "resource-server": {
                "restart": "always",
                "image": "deepomatic/run-resource-server:0.5.0",
                "environment": [
                    "DEEPOMATIC_API_URL={}".format(site_configuration.get('DEEPOMATIC_API_URL')),
                    "DEEPOMATIC_APP_ID={}".format(site_configuration.get('DEEPOMATIC_APP_ID')),
                    "DEEPOMATIC_API_KEY={}".format(site_configuration.get('DEEPOMATIC_API_KEY')),
                    "DEEPOMATIC_SITE_ID={}".format(site_configuration.get('DEEPOMATIC_SITE_ID')),
                    "DOWNLOAD_ON_STARTUP=1",
                    "INIT_SYSTEM=circus"
                ],
                "volumes": [
                    "deepomatic-resources:/var/lib/deepomatic"
                ]
            },
            "rabbitmq": {
                "restart": "always",
                "image": "rabbitmq:3.7",
                "expose": [
                    5672
                ],
                "ports": [
                    "5672:5672"
                ],
                "environment": [
                    "RABBITMQ_DEFAULT_USER={}".format(site_configuration.get('AMQP_USER')),
                    "RABBITMQ_DEFAULT_PASS={}".format(site_configuration.get('AMQP_PASSWORD')),
                    "RABBITMQ_DEFAULT_VHOST={}".format(site_configuration.get('AMQP_VHOST'))
                ]
            }
        }
    }

    for service in app["services"]:
        name = service["name"]
        docker_compose["services"][name] = get_service(name)(site_configuration=site_configuration, **service)

    return docker_compose
