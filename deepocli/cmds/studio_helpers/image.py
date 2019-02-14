# -*- coding: utf-8 -*-
import os
import sys
import json
import uuid
import time
import signal
import threading
from tqdm import tqdm
from .task import Task
if sys.version_info >= (3,0):
    import queue as Queue
else:
    import Queue

# Define thread parameters
THREAD_NUMBER = 5
q = Queue.Queue()
count = 0
run = True
lock = threading.Lock()

def handler(signum, frame):
    global run, q, pbar
    run = False
    pbar.close()
    print("Stopping upload...")
    while not q.empty():
        q.get()
        q.task_done()

def worker(self):
    global count, run, q, pbar
    while run:
        try:
            url, data, file = q.get(timeout=2)
            try:
                with open(file, 'rb') as fd:
                    rq = self._helper.post(url, data={"meta": data}, content_type='multipart/form', files={"file": fd})
                self._task.retrieve(rq['task_id'])
            except RuntimeError as e:
                tqdm.write('Annotation format for image named {} is incorrect'.format(file))
            pbar.update(1)
            q.task_done()
            lock.acquire()
            count += 1
            lock.release()
        except Queue.Empty:
            pass

class Image(object):
    def __init__(self, helper, task=None):
        self._helper = helper
        if not task:
            task = Task(helper)
        self._task = task


    def post_images(self, dataset_name, files, org_slug, is_json=False):
        global run, pbar
        try:
            ret = self._helper.get('datasets/' + dataset_name + '/')
        except RuntimeError as err:
            raise RuntimeError("Can't find the dataset {}".format(dataset_name))
        commit_pk = ret['commits'][0]['uuid']

        # Initialize threads
        threads = []
        for i in range(THREAD_NUMBER):
            t = threading.Thread(target=worker, args=(self, ))
            t.daemon = True
            t.start()
            threads.append(t)
        signal.signal(signal.SIGINT, handler)

        # Build the queue
        total_images = 0
        for file in files:
            # If it's an image, add it to the queue
            if file.split('.')[-1].lower() != 'json':
                tmp_name = uuid.uuid4().hex
                q.put(('v1-beta/datasets/{}/commits/{}/images/'.format(dataset_name, commit_pk), json.dumps({'location': tmp_name}), file))
                total_images += 1
            # If it's a json, deal with it accordingly
            else:
                # Verify json validity
                try:
                    with open(file, 'rb') as fd:
                        json_objects = json.load(fd)
                except ValueError as err:
                    tqdm.write(err)
                    tqdm.write("Can't read file {}, skipping...".format(file))
                    continue

                if isinstance(json_objects, dict):
                    if 'location' not in json_objects:
                        for ext in ('bmp', 'jpeg', 'jpg', 'jpe', 'png'):
                            tmp_path = os.path.join(os.path.dirname(file), os.path.basename(file).replace('json', ext))
                            if os.path.isfile(tmp_path):
                                json_objects['location'] = tmp_path
                                json_objects = [json_objects]
                                break
                        else:
                            tqdm.write("Can't find an image for json {}".format(os.path.basename(file)))
                            continue

                for i, json_object in enumerate(json_objects):
                    image_path = os.path.join(os.path.dirname(file), json_object['location'])
                    if not os.path.isfile(image_path):
                        tqdm.write("Can't find an image named {}".format(json_object['location']))
                        continue
                    image_key = uuid.uuid4().hex
                    json_object['location'] = image_key
                    q.put(('v1-beta/datasets/{}/commits/{}/images/'.format(dataset_name, commit_pk), json.dumps(json_object), image_path))
                    total_images += 1

        # Initialize progressbar
        print("Uploading images...")
        pbar = tqdm(total=total_images)

        # Process all files
        while not q.empty() and run:
            time.sleep(2)
        run = False

        # Close properly
        q.join()
        for t in threads:
            t.join()
        pbar.close()
        if count == total_images:
            print("All {} images have been uploaded.".format(count))
        else:
            print("{} images out of {} have been uploaded.".format(count, total_images))

        return True
