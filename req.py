import requests

TOKEN = "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"
OWNER = "dfint"
REPO = "update-data"


headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {TOKEN}",
}

data = '{"event_type": "dict"}'

res = requests.post(f"https://api.github.com/repos/{OWNER}/{REPO}/dispatches", data=data, headers=headers)

print(res.reason)
print(res.content)
