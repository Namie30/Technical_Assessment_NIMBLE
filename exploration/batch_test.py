import requests, json, base64, time

EMAIL = "your-email-here"
PASSWORD = "your-password-here"
cred = base64.b64encode(f"{EMAIL}:{PASSWORD}".encode()).decode()

headers = {"Authorization": f"Basic {cred}", "Content-Type": "application/json"}

payload = {
    "requests": [
        {"url": "https://www.example.com"},
        {"url": "https://www.wikipedia.org"}
    ]
    # no storage_type/storage_url — Push/Pull again, kept small on purpose
}

r = requests.post(
    "https://api.webit.live/api/v1/batch/web",
    headers=headers,
    json=payload,
    timeout=60,
)

print(r.status_code)
print(r.text)