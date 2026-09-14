import requests, json

API_KEY = ""  # heisenbug-hunter

payload = {
    "url": "https://bionovadigesters.com",
    "render": True,
    "formats": ["markdown"]
}

r = requests.post(
    "https://sdk.nimbleway.com/v2/extract",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json=payload,
    timeout=180,
)

print(r.status_code)
print(r.text)

with open("bionova_v2_markdown.json", "w", encoding="utf-8") as f:
    json.dump(r.json(), f, indent=2, ensure_ascii=False)