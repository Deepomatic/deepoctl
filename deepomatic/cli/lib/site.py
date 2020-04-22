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
        raise NotImplementedError('Please use the web interface')

    def current(self):
        return str(self._repo.head.reference)

    def current_app(self):
        return self._repo.head.commit.message

    def delete(self, site_id):
        raise NotImplementedError('Please use the web interface')

    def install(self, site_id):
        site = self.get(site_id)
        headers = self._client.setup_headers(content_type='application/yaml')
        response = self._client.send_request(self._client.session.get, '{}/sites/{}/docker-compose'.format(self._client.resource_prefix, site_id), headers=headers)
        docker_compose = yaml.load(response.content.decode(), Loader=yaml.FullLoader)
        try:
            # create branch
            self._repo.git.checkout(site_id, orphan=True)
        except Exception:
            return None

        docker_compose_path = os.path.join(self._repo.working_tree_dir, 'docker-compose.yml')
        with open(docker_compose_path, 'w') as f:
            f.write(docker_compose)

        # add to index
        self._repo.index.add([docker_compose_path])

        # commit
        self._repo.index.commit(site['app']['id'])

        return site['app']['id']

    def list(self):
        return [head.name for head in self._repo.heads]

    def load(self, archive_path):
        self._repo.git.bundle('verify', archive_path)
        site_id = self._repo.git.bundle('list-heads', archive_path).split('/')[-1]
        return self._repo.git.fetch(archive_path, '{}:{}'.format(site_id, site_id))

    def logs(self):
        return self._run_docker_compose("logs", "-f", "-t")

    def rollback(self, n=1):
        self._repo.git.reset("HEAD~{}".format(n), hard=True)
        return self._repo.head.commit.committed_datetime

    def save(self, site_id, archive_path):
        return self._repo.git.bundle('create', archive_path, site_id)

    def start(self):
        return self._run_docker_compose("up", "-d")

    def status(self):
        return self._run_docker_compose("ps")

    def stop(self):
        return self._run_docker_compose("down", "-v")

    def uninstall(self, site_id):
        try:
            self._repo.git.branch(site_id, D=True)
        except Exception:
            # last site, we can delete the repo
            shutil.rmtree(self._repo.working_tree_dir)

    def upgrade(self):
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

        return site['app']['id']

    def use(self, site_id):
        if hasattr(self._repo.heads, site_id):
            # TODO: stop current site
            getattr(self._repo.heads, site_id).checkout()
            return True
        else:
            # site does not exist
            return False

    def _run_docker_compose(self, *args):
        site_id = self.current()
        return subprocess.call(' '.join(["docker-compose", "-f", os.path.join(DEEPOMATIC_SITE_PATH, "docker-compose.yml")] + list(args)),
            env={
                "DEEPOMATIC_SITE_ID": site_id
            },
            shell=True
        )