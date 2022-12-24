import requests
import os
import json

assets_index = requests.get("https://piston-meta.mojang.com/v1/packages/c492375ded5da34b646b8c5c0842a0028bc69cec/2.json").json()

cid_db = {}
if os.path.exists("cid_db.json"):
  print("Loading cid_db.json...")
  with open("cid_db.json", "r") as f:
    cid_db = json.loads(f.read())
else:
  print("cid_db.json not found, exiting...")
  exit(1)

out = {
  "objects": {}
}

for asset in assets_index["objects"]:
  asset_val = assets_index["objects"][asset]
  hash_ = asset_val["hash"]
  out["objects"][asset] = {
    "hash": hash_,
    "size": asset_val["size"],
    "path": cid_db[hash_]
  }


with open("assets.json", "w") as f:
  json.dump(out, f, indent=2)
