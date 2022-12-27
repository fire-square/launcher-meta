import json
import requests
import time
import os

with open("cid_db.json", "r") as f:
  cid_db = json.load(f)

CID_DB_SIZE = len(cid_db)

download_start = time.time()
r = requests.get("http://ipfs.frsqr.xyz/ipfs/bafybeidwcbpvbjmkdaxbc6dqhorv2ttvcyrszinmgidwjh5wlquvbnw4cq/client.jar") # 1.19.3 client. Around 22MB
download_end = time.time()

DOWNLOAD_TIME = download_end - download_start

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
# HELP minecraft_versions Number of Minecraft versions
# TYPE minecraft_versions gauge
minecraft_versions {VERSIONS}

# HELP minecraft_unique_cids Number of unique CIDs
# TYPE minecraft_unique_cids gauge
minecraft_unique_cids {UNIQUE_CIDS}

# HELP minecraft_cid_db_size Number of files in the CID database
# TYPE minecraft_cid_db_size gauge
minecraft_cid_db_size {CID_DB_SIZE}

# HELP minecraft_download_time Time to download a file from IPFS
# TYPE minecraft_download_time gauge
minecraft_download_time {DOWNLOAD_TIME}

# HELP minecraft_download_size Size of the file downloaded from IPFS
# TYPE minecraft_download_size gauge
minecraft_download_size 22
"""

print(prometheus_data)
