import json
import sys
from binascii import crc32
from pathlib import Path

import toml
from utils import get_from_url

base_dir = Path(__file__).parent.parent  # base directory of the repository
hook_json_path = base_dir / "metadata/hook.json"
hook_v2_json_path = base_dir / "metadata/hook_v2.json"
offsets_json_path = base_dir / "store/offsets"
offsets_base_url = "https://raw.githubusercontent.com/dfint/update-data/main/store/offsets/"


def update_or_append(
    manifest_path: str, df_checksum: int, checksum: int, lib: str, config: str, offsets: str, dfhooks: str | None
):
    hook_manifest = json.loads(manifest_path.read_text())
    for i, item in enumerate(hook_manifest):
        if item["df"] == df_checksum:
            item["checksum"] = checksum
            item["lib"] = lib
            item["config"] = config
            item["offsets"] = offsets
            if dfhooks:
                item["dfhooks"] = dfhooks
            manifest_path.write_text(json.dumps(hook_manifest, indent=2))
            return

    if dfhooks:
        hook_manifest.append(
            {
                "df": df_checksum,
                "checksum": checksum,
                "lib": lib,
                "config": config,
                "offsets": offsets,
                "dfhooks": dfhooks,
            }
        )
    else:
        hook_manifest.append(
            {
                "df": df_checksum,
                "checksum": checksum,
                "lib": lib,
                "config": config,
                "offsets": offsets,
            }
        )
    manifest_path.write_text(json.dumps(hook_manifest, indent=2))


def main(lib: str, config: str, offsets: str, dfhooks: str):
    res_hook = get_from_url(lib)
    res_config = get_from_url(config)
    res_offsets = (offsets_json_path / offsets).read_bytes()
    res_dfhooks = get_from_url(dfhooks)

    offsets_data = toml.loads(res_offsets.decode(encoding="utf-8"))
    df_checksum = offsets_data["metadata"]["checksum"]
    checksum = crc32(res_hook + res_config + res_offsets)
    checksum_v2 = crc32(res_hook + res_config + res_offsets + res_dfhooks)
    update_or_append(hook_json_path, df_checksum, checksum, lib, config, offsets_base_url + offsets, None)
    update_or_append(hook_v2_json_path, df_checksum, checksum_v2, lib, config, offsets_base_url + offsets, dfhooks)


def run_with_config():
    config = toml.load(base_dir / "automation/hook_manifest_add.toml")
    for lib_variant in config.values():
        for offset_file in lib_variant["offset_files"]:
            main(lib_variant["lib_url"], lib_variant["config_url"], offset_file, lib_variant["dfhooks_url"])


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
