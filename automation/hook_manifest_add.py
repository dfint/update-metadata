import json
from binascii import crc32
from pathlib import Path
from sys import argv

import requests
import toml

if len(argv) < 4:
    raise Exception("Not enought args")

lib = argv[1]
config = argv[2]
offsets = argv[3]

if not lib.endswith(".dll") and not argv[1].endswith(".so"):
    raise Exception("First arg must be an url to hook lib")

if not config.endswith("config.toml"):
    raise Exception("First arg must be an url to config.toml")

if not offsets.endswith(".toml"):
    raise Exception("First arg must be an url to offsets file")


def update_or_append(df_checksum: int, checksum: int, lib: str, config: str, offsets: str):
    hook_manifest = json.loads(Path("./metadata/hook.json").read_text(encoding="utf-8"))
    for i, item in enumerate(hook_manifest):
        if item["df"] == df_checksum:
            hook_manifest[i]["checksum"] = checksum
            hook_manifest[i]["lib"] = lib
            hook_manifest[i]["config"] = config
            hook_manifest[i]["offsets"] = offsets
            Path("./metadata/hook.json").write_text(
                json.dumps(hook_manifest, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            return
    hook_manifest.append(
        {
            "df": df_checksum,
            "checksum": checksum,
            "lib": lib,
            "config": config,
            "offsets": offsets,
        }
    )
    Path("./metadata/hook.json").write_text(json.dumps(hook_manifest, indent=2, ensure_ascii=False), encoding="utf-8")


try:
    res_hook = requests.get(lib)
    res_hook.raise_for_status()
    res_config = requests.get(config)
    res_config.raise_for_status()
    res_offsets = requests.get(offsets)
    res_offsets.raise_for_status()
    offsets_data = toml.loads(res_offsets.content.decode(encoding="utf-8"))
    df_checksum = offsets_data["metadata"]["checksum"]
    checksum = crc32(res_hook.content + res_config.content + res_offsets.content)
    update_or_append(df_checksum, checksum, lib, config, offsets)
except:
    raise Exception("Unable to download data")
