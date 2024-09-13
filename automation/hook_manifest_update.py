# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
# ]
# ///
import binascii
import json
from pathlib import Path

from utils import get_from_url


def main():
    base_dir = Path(__file__).parent.parent  # base directory of the repository
    hook_json_path = [
        base_dir / "metadata/hook.json",
        base_dir / "metadata/hook_v2.json",
    ]

    for path in hook_json_path:
        manifest = json.loads(path.read_text(encoding="utf-8"))

        for item in manifest:
            print(f"Recalculating checksum for {item["df"]=}...")
            try:
                data = get_from_url(item["lib"]) + get_from_url(item["config"]) + get_from_url(item["offsets"])
                if item.get("dfhooks"):
                    data += get_from_url(item["dfhooks"])
                checksum = binascii.crc32(data)
            except Exception as ex:
                print(f"Failed on recalculation {item["df"]=}")
                raise
            else:
                if item.get("checksum") != checksum:
                    item["checksum"] = checksum

        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
