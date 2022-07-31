from flask import Flask, make_response, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from util import *

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:////Users/fabian/Desktop/clip_server/db.db'
db = SQLAlchemy(app)

class Embeddings(db.Model): 
    url = db.Column(db.String, primary_key=True)
    embedding = db.Column(db.PickleType)

@app.route('/api/get/', methods=['GET', 'POST'])
def get():
    url = request.json["url"]
    q = Embeddings.query.filter_by(url=url).first()
    if q is None: # If URL not in database
        if "embedding" in request.json: # If embedding provided
            embedding = request.json["embedding"]
            db.session.add(Embeddings(url=url, embedding=embedding))
            db.session.commit() 
        else:
            try: # Try to extract embedding
                img = img_from_url(url)
                embedding=CLIP_img(img).tolist()
                db.session.add(Embeddings(url=url, embedding=embedding))
                db.session.commit() 
            except:
                return make_response("Embedding not found and not created", 404)
    else:
        embedding = q.embedding
    print(url)
    return jsonify({"url": url, "embedding": embedding})

@app.route('/api/query/', methods=['GET', 'POST'])
def query():
    url = request.json["url"]
    q = Embeddings.query.filter_by(url=url).first()
    if q is None: # If URL not in database
        return make_response("Embedding not found and not created", 404)
    else:
        return jsonify({"url": url, "embedding": q.embedding})