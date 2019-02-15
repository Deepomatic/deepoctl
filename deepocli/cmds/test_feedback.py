import os
import tempfile
import requests

from deepocli.cli_parser import run

def download(url, filepath):
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, filepath)
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    r = requests.get(url)
    with open(path, 'wb') as f:
        f.write(r.content)
    return path


# Download all files for the test
#     .
#     ├── img_dir
#     │   ├── img1.jpg
#     │   ├── img2.jpg
#     │   └── subdir
#     │       └── img3.jpg
#     └── studio.json
single_img_pth = download('https://s3-eu-west-1.amazonaws.com/deepo-tests/vulcain/images/test.jpg', 'single_img.jpg')
img1_pth = download('https://s3-eu-west-1.amazonaws.com/deepo-tests/vulcain/images/test.jpg', 'img_dir/img1.jpg')
img2_pth = download('https://s3-eu-west-1.amazonaws.com/deepo-tests/vulcain/images/test.jpg', 'img_dir/img2.jpg')
img3_pth = download('https://s3-eu-west-1.amazonaws.com/deepo-tests/vulcain/images/test.jpg', 'img_dir/subdir/img3.jpg')
img_dir_pth = os.path.dirname(img1_pth)

def test_2e2_upload_single_image():
    run(['feedback', '-d', 'deepocli-feedback-test', '-o', 'travis-deepocli', single_img_pth])

def test_2e2_upload_image_dir():
    run(['feedback', '-d', 'deepocli-feedback-test', '-o', 'travis-deepocli', img_dir_pth])

def test_2e2_upload_image_dir_recursive():
    run(['feedback', '-d', 'deepocli-feedback-test', '-o', 'travis-deepocli', img_dir_pth, '--recursive'])

def test_2e2_upload_studio_json():
    return
    run()
