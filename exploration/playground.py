import requests, json, base64

# URL = "https://www.jcrew.com/p/mens/categories/clothing/tshirts-and-polos/t-shirts/washed-piqueacute-button-down-shirt/CV409?display=standard&fit=Classic&color_name=union-blue&colorProductCode=CV409"
URL = "https://bionovadigesters.com"


EMAIL = "your-email-here"
PASSWORD = "your-password-here"
cred = base64.b64encode(f"{EMAIL}:{PASSWORD}".encode()).decode()

payload = {
    "url": URL,
    "method": "GET",
    "country": "US",
    "locale": "en-US",
    "render": True,
    # "parse": True
    # no "parser" key, this is the whole point of the test
    "formats": ["markdown"]
}

r = requests.post(
    "https://api.webit.live/api/v1/realtime/web",
    headers={"Authorization": f"Basic {cred}", "Content-Type": "application/json"},
    json=payload,
    timeout=180,
)

print(r.status_code)
data = r.json()

with open("bionova_markdown_result.json", "w", encoding="utf-8") as f:
    json.dump(data.get("parsing"), f, indent=2, ensure_ascii=False)

print(json.dumps(data.get("parsing"), indent=2, ensure_ascii=False))
print("RAW RESPONSE TEXT:", r.text)