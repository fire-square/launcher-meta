import json
from tqdm import tqdm
import requests
import threading

with open("cid_db.json", "r") as f:
  cid_db = json.load(f)

MAX_TASKS = 100
tasks = 0

def download(cid):
  global tasks
  tasks += 1
  try:
    url = f"https://ipfs.frsqr.xyz/ipfs/{cid}"
    r = requests.get(url)
    if r.status_code != 200:
      print(f"Error: {cid} ({hash})")
      print(r.text)
  except Exception as e:
    print(f"Error: {cid} ({hash})")
    print(e)
  tasks -= 1

for hash_ in tqdm(cid_db):
  cid = cid_db[hash_]
  if tasks < MAX_TASKS:
    threading.Thread(target=download, args=(cid,)).start()
  else:
    while tasks >= MAX_TASKS:
      pass
    threading.Thread(target=download, args=(cid,)).start()

while tasks > 0:
  pass
