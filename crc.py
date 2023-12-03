import binascii

import requests

crc32 = 0

# files = ["./store/dict.csv", "./store/curses.png", "./store/encoding.toml"]

buffer = b""

# files = [
#     "E:\\Games\\DF 50.10 steam\\dfint-data\\dictionary.csv",
#     "E:\\Games\\DF 50.10 steam\\data\\art\\curses_640x300.png",
#     "E:\\Games\\DF 50.10 steam\\dfint-data\\encoding.toml",
# ]

urls = [
    "https://raw.githubusercontent.com/dfint/autobuild/main/translation_build/csv_with_objects/Russian/dfint_dictionary.csv",
    "https://raw.githubusercontent.com/dfint/update-data/main/store/fonts/russian.png",
    "https://raw.githubusercontent.com/dfint/update-data/main/store/encodings/russian.toml",
]

for url in urls:
    data = requests.get(url).content
    buffer += data


# for file_name in files:
#     with open(file_name, "rb") as file:
#         data = file.read()
#         print(len(data))
#         buffer += data
#         crc32 = binascii.crc32(data, crc32)

print(len(buffer))
print(binascii.crc32(buffer))
