import requests

# Tries to get the embedding for an URL, if not available asks the server to make one
r = requests.get("http://127.0.0.1:5000/api/get/", json={"url": "https://cdn.britannica.com/51/194651-050-747F0C18/Interior-National-Gallery-of-Art-Washington-DC.jpg"})
if r.ok:
    print(r.json())
print(r.status_code)

# Checks if an embedding for an URL exists, returns 404 if not
r = requests.get("http://127.0.0.1:5000/api/query/", json={"url": "http://images.metmuseum.org/iisstart.png"})
if r.ok:
    print(r.json())
print(r.status_code)