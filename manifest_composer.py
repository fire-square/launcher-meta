from requests import get
from os import mkdir, listdir, remove, system
from shutil import rmtree
from tqdm import tqdm
from json import load, loads, dump, dumps
from pathlib import Path
from hashlib import sha1
import re
from traceback import print_exc


def get_command_output(command):
  print(f"Running command: {command}")
  system(command + " > out 2>&1")
  with open("out", "r") as f:
    output = f.read()
  remove("out")
  return output


def find_cid(text):
  # Find CIDv1
  try:
    cid = re.findall(r"baf[a-zA-Z0-9]{56}", text)
    return cid[0]
  except Exception as e:
    print(text)
    raise e


def main(url, version_id):
  MANIFEST_URL = url
  ASSET_PATH = Path("assets")


  with open("cid_db.json", "r") as f:
    cid_db = load(f)


  def download(url: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    response = get(url)
    with open(path, 'wb') as f:
      f.write(response.content)


  rmtree('assets', ignore_errors=True)
  mkdir('assets')


  manifest = loads(get(MANIFEST_URL).text)


  # Download assets
  # Download assetIndex
  print("Downloading assetIndex...")
  assetIndex = get(manifest['assetIndex']["url"]).json()
  original_assetIndex = get(manifest['assetIndex']["url"]).json()

  # Filter assets
  # If hash is not in cid_db, save it
  for key in list(assetIndex['objects']):
    if assetIndex['objects'][key]['hash'] in cid_db:
      del assetIndex['objects'][key]

  # Download assets
  for key in tqdm(assetIndex['objects'].values()):
    download(f"https://resources.download.minecraft.net/{key['hash'][0:2]}/{key['hash']}", ASSET_PATH / "objects" / key['hash'][0:2] / key['hash'])


  # Download client
  if manifest["mainJar"]['downloads']['artifact']["sha1"] in cid_db:
    print("Skipping client...")
  else:
    print("Downloading client...")
    client = download(manifest["mainJar"]['downloads']['artifact']['url'], ASSET_PATH / "client.jar")


  # Download libraries
  print("Downloading libraries...")

  for library in tqdm(manifest['libraries']):
    if library['downloads']['artifact']['sha1'] not in cid_db:
      download(library['downloads']['artifact']['url'], ASSET_PATH / "libraries" / library['downloads']['artifact']['sha1'])

    for classifier in library['downloads'].get('classifiers', {}):
      if library['downloads']["classifiers"][classifier]['sha1'] not in cid_db:
        download(library['downloads']["classifiers"][classifier]['url'], ASSET_PATH / "libraries" / library['downloads']["classifiers"][classifier]['sha1'])


  # Upload to IPFS
  if len(listdir(ASSET_PATH)) == 0:
    print("Nothing to upload...")
  else:
    cid = find_cid(get_command_output("w3 put --no-wrap " + str(ASSET_PATH)))

    # Fill cid_db
    print("Filling cid_db...")

    # Add assetIndex
    for key in tqdm(assetIndex['objects']):
      cid_db[assetIndex['objects'][key]['hash']] = cid + "/objects/" + assetIndex['objects'][key]['hash'][0:2] + "/" + assetIndex['objects'][key]['hash']


    # Add client
    if manifest["mainJar"]['downloads']['artifact']["sha1"] not in cid_db:
      cid_db[manifest["mainJar"]['downloads']['artifact']["sha1"]] = cid + "/client.jar"


    # Add libraries
    for library in tqdm(manifest['libraries']):
      if library['downloads']['artifact']['sha1'] not in cid_db:
        cid_db[library['downloads']['artifact']['sha1']] = cid + "/libraries/" + library['downloads']['artifact']['sha1']

      for classifier in library['downloads'].get('classifiers', {}):
        if library['downloads']["classifiers"][classifier]['sha1'] not in cid_db:
          cid_db[library['downloads']["classifiers"][classifier]['sha1']] = cid + "/libraries/" + library['downloads']["classifiers"][classifier]['sha1']


  rmtree('assets', ignore_errors=True)
  mkdir('assets')


  # Make modified assetIndex
  print("Making modified assetIndex...")
  new_assetIndex = {}
  for key in original_assetIndex['objects']:
    new_assetIndex[key] = {
      "hash": original_assetIndex['objects'][key]['hash'],
      "size": original_assetIndex['objects'][key]['size'],
      "path": cid_db[original_assetIndex['objects'][key]['hash']]
    }

  assetIndex_data = dumps({ "objects": new_assetIndex }, indent=2)
  assetIndex_hash = sha1(assetIndex_data.encode()).hexdigest()
  if assetIndex_hash in cid_db:
    print("Skipping modified assetIndex...")
  else:
    with open(ASSET_PATH / "assetIndex.json", "w") as f:
      f.write(assetIndex_data)

    cid = find_cid(get_command_output("w3 put --no-wrap " + str(ASSET_PATH / "assetIndex.json")))
    cid_db[assetIndex_hash] = cid



  # Modify manifest to use IPFS
  print("Modifying manifest...")

  del manifest['assetIndex']['url']
  manifest['assetIndex']['sha1'] = assetIndex_hash
  manifest['assetIndex']['size'] = len(assetIndex_data)
  manifest['assetIndex']['path'] = cid_db[assetIndex_hash]


  del manifest["mainJar"]['downloads']['artifact']['url']
  manifest["mainJar"]['downloads']['artifact']['path'] = cid_db[manifest["mainJar"]['downloads']['artifact']['sha1']]


  for library in manifest['libraries']:
    del library['downloads']['artifact']['url']
    library['downloads']['artifact']['path'] = cid_db[library['downloads']['artifact']['sha1']]

    for classifier in library['downloads'].get('classifiers', {}):
      del library['downloads']["classifiers"][classifier]['url']
      library['downloads']["classifiers"][classifier]['path'] = cid_db[library['downloads']["classifiers"][classifier]['sha1']]


  # Save manifest
  print("Saving manifest...")
  with open("net.minecraft/" + version_id + ".json", "w") as f:
    dump(manifest, f, indent=2)

  # Save cid_db
  print("Saving cid_db...")
  with open("cid_db.json", "w") as f:
    dump(cid_db, f, indent=2)



version_index = get("https://meta.prismlauncher.org/v1/net.minecraft/index.json").json()
for version in version_index['versions']:
  version_id = version['version']
  # if re.findall(r"^\d+\.\d+\.\d+$", version_id) == []:
  #   print(f"Skipping {version_id}...")
  #   continue
  # skip = False
  # for name in listdir("versions"):
  #   if version_id + ".json" in name:
  #     print(f"Skipping {version_id}...")
  #     skip = True
  #     break
  # if skip:
  #   continue
  print(f"Processing {version_id}...")
  try:
    main(f"https://meta.prismlauncher.org/v1/net.minecraft/{version_id}.json", version_id)
  except Exception:
    print_exc()
    print(f"Failed to process {version_id}...")
