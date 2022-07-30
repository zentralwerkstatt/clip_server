import json
import requests

r = requests.get('http://127.0.0.1:5001/api/', json={"url": "https://iip-thumb.smk.dk/iiif/jp2/kks15987.tif.jp2/full/!1024,/0/default.jpg"})
if r.ok:
    print(r.json())
print(r.status_code)