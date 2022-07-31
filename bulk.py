from threading import Lock, Thread
from queue import Queue, Empty
from tqdm import tqdm
import pandas as pd
from flask import jsonify
import requests
from util import *

df = pd.read_csv("art.txt", sep="\n", engine="python", header=None, names=['url'])
print(df.head())

# Set up threading
pbar_success = tqdm(total=len(df), desc="Embedded")
pbar_failure = tqdm(total=len(df), desc="Failed")
q = Queue()
l = Lock()
num_workers = 16
features = {}

# Define and start queue
def _worker():
    while True:
        try:
            url = q.get()
        except Empty:
            q.task_done()
        try:
            r = requests.get("http://127.0.0.1:5000/api/query/", json={"url":url})
            if r.ok:          
                with l: pbar_success.update(1)
            else:
                img = img_from_url(url)
                with l: embedding = CLIP_img(img).tolist()
                r = requests.get("http://127.0.0.1:5000/api/get/", json={"url":url, "embedding":embedding})
                if r.ok:                
                    with l: pbar_success.update(1)
                else:
                    with l: pbar_failure.update(1)
        except:
            pbar_failure.update(1)
        q.task_done()

for i in range(num_workers):
    thread = Thread(target=_worker)
    thread.daemon = True
    thread.start()

for _, row in df.iterrows():
#for _, row in df.head(100).iterrows():
    q.put(row["url"])

# Cleanup
q.join()
pbar_success.close()
pbar_failure.close()