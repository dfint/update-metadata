import binascii
import json
from pathlib import Path

from utils import get_from_url

base_dir = Path(__file__).parent.parent  # base directory of the repository
hook_json_path = base_dir / "metadata/hook.json"

manifest = json.loads(hook_json_path.read_text(encoding="utf-8"))

for i, item in enumerate(manifest):
    try:
        data = get_from_url(item["lib"]) + get_from_url(item["config"]) + get_from_url(item["offsets"])
        checksum = binascii.crc32(data)
    except Exception as ex:
        print(f"Failed on recalculation {item['language']}:\n", ex)
    else:
        if item.get("checksum") != checksum:
            manifest[i]["checksum"] = checksum

hook_json_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
