import requests
from pathlib import Path
from tqdm import tqdm
from threading import Thread
from shutil import rmtree
import os
import json

threads = 0
MAX_THREADS = 24


def download(url: str, path: Path):
  global threads
  threads += 1
  response = requests.get(url, stream=True)
  # Create the directory if it doesn't exist
  path.parent.mkdir(parents=True, exist_ok=True)
  with open(str(path), "wb") as f:
    for chunk in response.iter_content(chunk_size=1024):
      if chunk:
        f.write(chunk)
  threads -= 1


# VERSION_META = "https://piston-meta.mojang.com/v1/packages/6607feafdb2f96baad9314f207277730421a8e76/1.19.3.json"

cid_db = {}
if os.path.exists("cid_db.json"):
  print("Loading cid_db.json...")
  with open("cid_db.json", "r") as f:
    cid_db = json.loads(f.read())
else:
  print("cid_db.json not found, creating new one...")

# index = requests.get(VERSION_META).json()
assets_index = requests.get("https://piston-meta.mojang.com/v1/packages/28680197f74e5e1d55054f6a63509c8298d428f9/1.16.json").json()
rmtree("assets", ignore_errors=True)

print("Downloading assets...")
for asset in tqdm(assets_index["objects"]):
  asset_val = assets_index["objects"][asset]
  hash_ = asset_val["hash"]
  if hash_ in cid_db:
    continue
  url = f"https://resources.download.minecraft.net/{hash_[0:2]}/{hash_}"
  while threads >= MAX_THREADS:
    pass
  Thread(target=download, args=(url, Path("assets") / hash_)).start()

while threads > 0:
  pass

# launch "w3 put --no-wrap assets/"
os.system("w3 put --no-wrap assets/")

cid = input("CID: ").strip()

print("Updating cid_db.json...")
for asset in assets_index["objects"]:
  asset_val = assets_index["objects"][asset]
  hash_ = asset_val["hash"]
  if hash_ not in cid_db:
    cid_db[hash_] = cid + "/" + hash_

with open("cid_db.json", "w") as f:
  f.write(json.dumps(cid_db, indent=2))
