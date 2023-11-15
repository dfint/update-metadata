import binascii
import json
from pathlib import Path

import requests

file = Path("./metadata/dict.json")

manifest = json.loads(file.read_text(encoding="utf-8"))

for i, item in enumerate(manifest):
    try:
        data = requests.get(item["csv"]).content
        data += requests.get(item["font"]).content
        data += requests.get(item["encoding"]).content
        checksum = binascii.crc32(data)
    except:
        print(f"Fialed on recalculation {item['language']}")
    else:
        if item["version"] != checksum:
            manifest[i]["version"] = checksum

file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
