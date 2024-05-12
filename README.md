# Update Data

Data backend for [dfint installer](https://github.com/dfint/installer).

- `metadata/hook.json` contains info about releases of [df-steam-hook-rs](https://github.com/dfint/df-steam-hook-rs), configs, offset files
- `metadata/hook_v2.json` metadata for installer 0.2.0 and higher, also contains info about [dfhooks](https://github.com/DFHack/dfhooks) library
- `metadata/dict.json` contains info about localization languages: url of their csv files, font files, encoding specific configs
- `store` directory contains files referenced from metadata, like encoding specific configs, offsets for different DF versions, and other misc. stuff.
