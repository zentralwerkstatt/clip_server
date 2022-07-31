import clip
import torch as t
from io import BytesIO
import PIL
import requests
import numpy as np

def set_cuda():
    device = "cuda" if t.cuda.is_available() else "cpu"
    return device

device = set_cuda()
model, transforms = clip.load("ViT-B/32", device=device)

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

def from_device(tensor):
    return tensor.detach().cpu().numpy()

def CLIP_img(img):
    with t.no_grad():
        input_ = transforms(img).unsqueeze(0).to(device)
        output = model.encode_image(input_)
        output /= output.norm(dim=-1, keepdim=True)
        return from_device(output).astype(np.float32).flatten()