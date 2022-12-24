from hashlib import sha1
from requests import get
from sys import argv

url = ("https://ipfs.frsqr.xyz/ipfs/" + argv[1]) if argv[1].startswith('bafy') else argv[1]
response = get(url)
print(sha1(response.content).hexdigest())
