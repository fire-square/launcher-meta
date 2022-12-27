import json
from tqdm import tqdm
import requests
import threading

with open("cid_db.json", "r") as f:
  cid_db = json.load(f)

MAX_TASKS = 100
tasks = 0
cached = 0
errors = 0

def download(cid):
  global tasks
  global cached
  global errors
  tasks += 1
  try:
    url = f"https://ipfs.frsqr.xyz/ipfs/{cid}"
    r = requests.get(url)
    if r.status_code != 200:
      errors += 1
      print(f"Error: {cid} ({hash})")
      print(r.text)
    if r.status_code == 200:
      cache_status = r.headers.get("Cache-Status")
      if cache_status == "HIT":
        global cached
        cached += 1
  except Exception as e:
    errors += 1
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

total = len(cid_db)
print(f"Total: {total}")
print(f"Cached: {cached}")
print(f"Uncached: {total - cached}")
print(f"Cache Rate: {total / cached * 100}%")
print(f"Errors: {errors}")
