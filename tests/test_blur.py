import os
import tempfile
import requests

from deepomatic.cli.cli_parser import run

def download(url):
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, os.path.basename(url))
    r = requests.get(url)
    with open(path, 'wb') as f:
        f.write(r.content)
    return path

image_url = 'https://s3-eu-west-1.amazonaws.com/deepo-tests/vulcain/images/test.jpg'
image_path = download(image_url)

video_url = 'https://s3-eu-west-1.amazonaws.com/deepo-tests/vulcain/videos/test.mp4'
video_path = download(video_url)


def test_e2e_image_blur_image():
    run(['blur', '-i', image_path, '--recognition_id', 'fashion-v4', '-o', '/tmp/test.jpeg'])

def test_e2e_image_blur_image_pixel():
    run(['blur', '-i', image_path, '--recognition_id', 'fashion-v4', '-o', '/tmp/test_blur_pixel.jpeg', '--blur_method', 'pixel'])

def test_e2e_image_blur_image_strength():
    run(['blur', '-i', image_path, '--recognition_id', 'fashion-v4', '-o', '/tmp/test_blur_strength.jpeg', '--blur_strength', '4'])

def test_e2e_video_blur_video():
    run(['blur', '-i', video_path, '--recognition_id', 'fashion-v4', '-o', '/tmp/test.mp4'])

def test_e2e_image_blur_json_flag():
    run(['blur', '-i', image_path, '--recognition_id', 'fashion-v4', '-o', '/tmp/test_json_flag.jpeg', '--json'])

def test_e2e_video_blur_json_flag():
    run(['blur', '-i', video_path, '--recognition_id', 'fashion-v4', '-o', '/tmp/test_json_flag.mp4', '--json'])