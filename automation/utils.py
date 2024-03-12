from functools import cache

import requests


@cache
def get_from_url(url: str) -> bytes:
    response = requests.get(url)
    response.raise_for_status()
    return response.content
