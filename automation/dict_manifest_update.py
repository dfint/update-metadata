import binascii
import json
from pathlib import Path

import requests

file = Path("./metadata/dict.json")

manifest = json.loads(file.read_text(encoding="utf-8"))

for i, item in enumerate(manifest):
    try:
        res1 = requests.get(item["csv"])
        res1.raise_for_status()
        data = res1.content
        res2 = requests.get(item["font"])
        res2.raise_for_status()
        data += res2.content
        res3 = requests.get(item["encoding"])
        res3.raise_for_status()
        data += res3.content
        checksum = binascii.crc32(data)
    except:
        print(f"Fialed on recalculation {item['language']}")
    else:
        if item["checksum"] != checksum:
            manifest[i]["checksum"] = checksum

file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
