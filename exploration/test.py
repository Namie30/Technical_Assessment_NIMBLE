import requests, json, base64

# URL = "https://www.jcrew.com/p/mens/categories/clothing/tshirts-and-polos/t-shirts/washed-piqueacute-button-down-shirt/CV409?display=standard&fit=Classic&color_name=union-blue&colorProductCode=CV409"
URL = "https://www.amazon.com/"


EMAIL = "your-email-here"
PASSWORD = "your-password-here"
cred = base64.b64encode(f"{EMAIL}:{PASSWORD}".encode()).decode()



payload = {
    "url": URL,
    "method": "GET",
    "country": "US",
    "locale": "en-US",
    "render": True,
    "render_options": { "timeout": 180000 },
    "browser_actions": [
        # 1. open the "Deliver to" popover
        {"click": {"selector": "#nav-global-location-popover-link", "timeout": 20000}},
        {"wait_for_element": {"selector": "#GLUXZipUpdateInput", "timeout": 20000}},

        # 2. type the zip
        {"fill": {
            "selector": "#GLUXZipUpdateInput",
            "value": '90210',
            "mode": "type",
            "typing_interval": 120,
            "click_on_element": True
        }},

        # 3. Apply
        {"click": {"selector": "#GLUXZipUpdate input[type='submit']", "timeout": 15000}},
        {"wait": "2s"},

        # 4. dismiss the confirmation popup (not always shown)
        {"click": {"selector": "button[name='glowDoneButton']", "required": False}},
        {"click": {"selector": "#GLUXConfirmClose", "required": False}},
        {"wait": "2s"},

        # 5. reload so prices/availability reflect the new location
        {"goto": {"url": URL, "wait_until": "networkidle2"}},
        {"wait_for_element": {"selector": "#glow-ingress-line2", "timeout": 20000}},

        {"screenshot": True}
    ],

}

r = requests.post(

    "https://sdk.nimbleway.com/v2/extract",
    headers={"Authorization": f"Basic {cred}", "Content-Type": "application/json"},
    json=payload,
    timeout=180,

)

print(r.status_code)
print(r.text)

data = r.json()

with open("LiveTest.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

with open("Test.html", "w", encoding="utf-8") as f:
    f.write(data["data"]["html"])