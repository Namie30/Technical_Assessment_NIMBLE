import requests, json
import base64


URL = "https://www.jcrew.com/p/mens/categories/clothing/tshirts-and-polos/t-shirts/washed-piqueacute-button-down-shirt/CV409?display=standard&fit=Classic&color_name=union-blue&colorProductCode=CV409"   # your PDP

# cred = base64.b64encode(f"{API_KEY}:".encode()).decode()

# Credentials from the task brief - replace with real values before running.
#
# In production these would be environment variables or a secrets manager
# rather than inline placeholders. Kept inline here for a self-contained
# submission that's easy to read and run without extra setup.
EMAIL = "your-email-here"
PASSWORD = "your-password-here"

cred = base64.b64encode(f"{EMAIL}:{PASSWORD}".encode()).decode()

payload = {
    "url": URL,
    "method": "GET",
    "country": "US",
    "locale": "en-US",
    "render": True,
    "parse": True,
    "parser": {
    "title": {
        "type": "item",
        "selectors": ["h1"]
    },
    "price": {
        "type": "item",
        "selectors": ['[data-testid="price"]']
    },
    "color": {
        "type": "item",
        "selectors": ['[data-testid="color-name"]']
    }
}
}

r = requests.post(
    "https://api.webit.live/api/v1/realtime/web",
    headers={
        "Authorization": f"Basic {cred}",
        "Content-Type": "application/json",
    },
    json=payload,
    timeout=180,
)

print(r.status_code)
data = r.json()

# print(data.keys())
#print(data.get("status"), data.get("msg"))

print(data.get("status"))
print(data.get("parsing"))

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(data.get("parsing"), f, indent=2, ensure_ascii=False)

# open("jcrew.html", "w", encoding="utf-8").write(data["html_content"])