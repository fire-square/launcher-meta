import json
from tqdm import tqdm
import requests
import threading
from sys import argv

with open("cid_db.json", "r") as f:
  cid_db = json.load(f)

run_number = int(argv[1])

MAX_TASKS = 24
GH_JOBS = 20
tasks = 0
cached = 0
errors = 0

def download(cid, count = True):
  global tasks
  global cached
  global errors
  if count:
    tasks += 1
  try:
    url = f"https://ipfs.frsqr.xyz/ipfs/{cid}"
    r = requests.get(url)
    if r.status_code != 200:
      errors += 1
      print(f"Error: {cid} ({hash})")
      print(r.text)
      download(cid, False)
    if r.status_code == 200:
      cache_status = r.headers.get("cf-cache-status", "MISS")
      if cache_status == "HIT":
        global cached
        cached += 1
  except Exception as e:
    errors += 1
    print(f"Error: {cid} ({hash})")
    print(e)
    download(cid, False)
  if count:
    tasks -= 1

total = len(cid_db)
step = int(total / GH_JOBS) + 100

print(f"Range: {step * (run_number - 1)} - {step * run_number} ({step})")

for path in tqdm(list(cid_db.values())[step * (run_number - 1):step * run_number]):
  if tasks < MAX_TASKS:
    threading.Thread(target=download, args=(path,)).start()
  else:
    while tasks >= MAX_TASKS:
      pass
    threading.Thread(target=download, args=(path,)).start()

while tasks > 0:
  pass

print(f"Range: {step * (run_number - 1)} - {step * run_number} ({step})")
print(f"Total: {step}")
print(f"Cached: {cached}")
print(f"Uncached: {step - cached}")
print(f"Cache Rate: {step / cached * 100}%")
print(f"Errors: {errors}")
