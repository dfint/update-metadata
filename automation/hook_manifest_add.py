# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
#     "toml",
# ]
# ///
import json
from binascii import crc32
from pathlib import Path
from typing import Any, NamedTuple

import toml
from utils import get_from_url

base_dir = Path(__file__).parent.parent  # base directory of the repository

hook_json_path = base_dir / "metadata/hook.json"
hook_v2_json_path = base_dir / "metadata/hook_v2.json"
offsets_toml_path = base_dir / "store/offsets"
config_path = base_dir / "store"

offsets_base_url = "https://raw.githubusercontent.com/dfint/update-data/main/store/offsets/"
lib_download_base_url = "https://github.com/dfint/df-steam-hook-rs/releases/download/"
dfhooks_download_base_url = "https://github.com/DFHack/dfhooks/releases/download/"
config_base_url = "https://raw.githubusercontent.com/dfint/update-data/main/store/"


class ConfigItem(NamedTuple):
    df_checksum: str
    payload_checksum: int
    hook_lib_url: str
    config_url: str
    offsets_url: str
    dfhooks_url: str | None
    
    def dict(self) -> dict[str, Any]:
        item = {
            "df": self.df_checksum,
            "checksum": self.payload_checksum,
            "lib": self.hook_lib_url,
            "config": self.config_url,
            "offsets": self.offsets_url,
        }

        if self.dfhooks_url:
            item["dfhooks"] = self.dfhooks_url

        return item


def update_or_append(manifest_path: str, config_item: ConfigItem):
    hook_manifest = json.loads(manifest_path.read_text())
    for item in hook_manifest:
        if item["df"] == config_item.df_checksum:
            item.update(config_item.dict())
            break
    else:
        # Item with the same checksum not found, add new one
        hook_manifest.append(config_item.dict())

    manifest_path.write_text(json.dumps(hook_manifest, indent=2))


def main(hook_lib_url: str, config_file_name: str, offsets_file_name: str, dfhooks_url: str):
    res_hook = get_from_url(hook_lib_url)
    res_config = (config_path / config_file_name).read_bytes()
    res_offsets = (offsets_toml_path / offsets_file_name).read_bytes()
    res_dfhooks = get_from_url(dfhooks_url)

    offsets_data = toml.loads(res_offsets.decode(encoding="utf-8"))
    df_checksum = offsets_data["metadata"]["checksum"]
    payload_checksum = crc32(res_hook + res_config + res_offsets)
    payload_checksum_v2 = crc32(res_hook + res_config + res_offsets + res_dfhooks)
    
    update_or_append(
        hook_json_path,
        ConfigItem(
            df_checksum,
            payload_checksum,
            hook_lib_url,
            config_base_url + config_file_name,
            offsets_base_url + offsets_file_name,
            None,
        )
    )

    update_or_append(
        hook_v2_json_path,
        ConfigItem(
            df_checksum,
            payload_checksum_v2,
            hook_lib_url,
            config_base_url + config_file_name,
            offsets_base_url + offsets_file_name,
            dfhooks_url,
        )
    )


def run_with_config():
    config = toml.load(base_dir / "automation/hook_manifest_add.toml")
    for lib_variant in config.values():
        for offset_file in lib_variant["offset_files"]:
            main(
                lib_download_base_url + lib_variant["lib"],
                "config.toml",
                offset_file,
                dfhooks_download_base_url + lib_variant["dfhooks"]
            )


if __name__ == "__main__":
    run_with_config()
