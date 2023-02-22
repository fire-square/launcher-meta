import json
from tqdm import tqdm
import requests
import threading
import time
import os

with open("cid_db.json", "r") as f:
  cid_db = json.load(f)

MAX_TASKS = 24
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
    url = f"https://ipfs.cofob.dev/ipfs/{cid}"
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

start = time.time()

for path in tqdm(cid_db.values()):
  if tasks < MAX_TASKS:
    threading.Thread(target=download, args=(path,)).start()
  else:
    while tasks >= MAX_TASKS:
      pass
    threading.Thread(target=download, args=(path,)).start()

while tasks > 0:
  pass

end = time.time()
download_time = end - start

CID_DB_SIZE = len(cid_db)

cids = []
for sha in cid_db:
  path = cid_db[sha]
  cid = path.split("/")[0]
  cids.append(cid)
cids = list(set(cids))

UNIQUE_CIDS = len(cids)

d = os.listdir("net.minecraft")

VERSIONS = len(d)

prometheus_data = f"""
# HELP minecraft_assets_download_time Time to download all assets from IPFS
# TYPE minecraft_assets_download_time gauge
minecraft_assets_download_time {download_time}

# HELP minecraft_cached Number of cached assets
# TYPE minecraft_cached gauge
minecraft_cached {cached}

# HELP minecraft_errors Number of errors
# TYPE minecraft_errors gauge
minecraft_errors {errors}

# HELP minecraft_versions Number of Minecraft versions
# TYPE minecraft_versions gauge
minecraft_versions {VERSIONS}

# HELP minecraft_unique_cids Number of unique CIDs
# TYPE minecraft_unique_cids gauge
minecraft_unique_cids {UNIQUE_CIDS}

# HELP minecraft_cid_db_size Number of files in the CID database
# TYPE minecraft_cid_db_size gauge
minecraft_cid_db_size {CID_DB_SIZE}
"""

with open("metrics.txt", "w") as f:
  f.write(prometheus_data)
