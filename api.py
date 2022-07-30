from flask import Flask, make_response, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import clip
import torch as t
import numpy as np
import pandas as pd
import requests
from io import BytesIO
import PIL

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/fabian/clip_server/db.db'
db = SQLAlchemy(app)

class Embeddings(db.Model): 
    url = db.Column(db.String, primary_key=True)
    embedding = db.Column(db.PickleType)

def img_from_url(url, max_tries=10):
    tries = 0
    while tries < max_tries:
        try:
            response = requests.get(url, timeout=30)
            img_bytes = BytesIO(response.content)
            img = PIL.Image.open(img_bytes).convert("RGB")
            return img
        except:
            tries += 1

def set_cuda():
    device = "cuda" if t.cuda.is_available() else "cpu"
    return device

def from_device(tensor):
    return tensor.detach().cpu().numpy()

device = set_cuda()
model, transforms = clip.load("ViT-B/32", device=device)

def CLIP_img(img):
    with t.no_grad():
        input_ = transforms(img).unsqueeze(0).to(device)
        output = model.encode_image(input_)
        output /= output.norm(dim=-1, keepdim=True)
        return from_device(output).astype(np.float32).flatten()

@app.route('/api/', methods=['GET', 'POST'])
def api():
    url = request.json["url"]
    q = Embeddings.query.filter_by(url=url).first()
    if q is None:
        try:
            img = img_from_url(url)
            embedding=CLIP_img(img)
            db.session.add(Embeddings(url=url, embedding=embedding))
            db.session.commit() 
            return jsonify({"url":embedding.tolist()})
        except:
            return make_response("Embedding not found and not created", 404)
    else:
        return jsonify({"url":q.embedding.tolist()})