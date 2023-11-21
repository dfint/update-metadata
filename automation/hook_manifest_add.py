import json
from binascii import crc32
from pathlib import Path
import sys

import requests
import toml


base_dir = Path(__file__).parent.parent  # base directory of the repository
hook_json_path = base_dir / "metadata/hook.json"


def update_or_append(df_checksum: int, checksum: int, lib: str, config: str, offsets: str):
    hook_manifest = json.loads(hook_json_path.read_text())
    for i, item in enumerate(hook_manifest):
        if item["df"] == df_checksum:
            hook_manifest[i]["checksum"] = checksum
            hook_manifest[i]["lib"] = lib
            hook_manifest[i]["config"] = config
            hook_manifest[i]["offsets"] = offsets
            hook_json_path.write_text(json.dumps(hook_manifest, indent=2))
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
    hook_json_path.write_text(json.dumps(hook_manifest, indent=2))


def main(lib: str, config: str, offsets: str):
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
    except Exception as ex:
        raise ex


def run_with_config():
    config = toml.load(base_dir / "automation/hook_metadata_update.toml")
    for lib_variant in config.values():
        for offset_url in lib_variant["offset_urls"]:
            print(lib_variant["lib_url"], lib_variant["config_url"], offset_url)
            main(lib_variant["lib_url"], lib_variant["config_url"], offset_url)


def run():
    args = sys.argv[1:]
    
    if not args:
        run_with_config()
        return
    
    if len(args) < 3:
        raise Exception("Not enought args")

    lib, config, offsets = args

    if not lib.endswith(".dll") and not lib.endswith(".so"):
        raise Exception("First arg must be an url to hook lib")

    if not config.endswith("config.toml"):
        raise Exception("First arg must be an url to config.toml")

    if not offsets.endswith(".toml"):
        raise Exception("First arg must be an url to offsets file")

    main(lib, config, offsets)


if __name__ == "__main__":
    run()
