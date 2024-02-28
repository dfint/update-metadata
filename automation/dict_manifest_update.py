import binascii
import json
from pathlib import Path

import requests

base_dir = Path(__file__).parent.parent  # base directory of the repository
dict_json_path = base_dir / "metadata/dict.json"

manifest = json.loads(dict_json_path.read_text(encoding="utf-8"))

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
    except Exception as ex:
        print(f"Fialed on recalculation {item['language']}:\n", ex)
    else:
        if item["checksum"] != checksum:
            manifest[i]["checksum"] = checksum

dict_json_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
