import json
from tqdm import tqdm
import requests

with open("cid_db.json", "r") as f:
  cid_db = json.load(f)

for hash_ in tqdm(cid_db):
  cid = cid_db[hash_]
  url = f"https://ipfs.frsqr.xyz/ipfs/{cid}"
  r = requests.get(url)
  if r.status_code != 200:
    print(f"Error: {cid} ({hash})")
    print(r.text)
