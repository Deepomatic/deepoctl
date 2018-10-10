import os
import tempfile
import requests

from deepoctl.cli_parser import run

def make_args(url):
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, os.path.basename(url))
    r = requests.get(url)
    with open(path, 'wb') as f:
        f.write(r.content)
    return ['draw', path, '--recognition_id', 'fashion-v4']

def test_e2e_draw_image():
    run(make_args('https://storage.googleapis.com/dp-vulcan/tests/deepoctl/test.jpg'))

def test_e2e_draw_video():
    run(make_args('https://storage.googleapis.com/dp-vulcan/tests/deepoctl/test.mp4'))
