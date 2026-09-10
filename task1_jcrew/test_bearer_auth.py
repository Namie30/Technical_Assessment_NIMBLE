import requests

# Replace with your own API key.
# Would normally be an env var; but I inlined here for simplicity.
API_KEY = " "   

r = requests.post(
    "https://api.webit.live/api/v1/realtime/web",
    headers={
        "Authorization": f"Bearer {API_KEY}",       # Just doing it for fun and to kill my curiosity
        "Content-Type": "application/json",
    },
    json={"url": "https://www.example.com"},
    timeout=60,
)

print("Status:", r.status_code)     # It worked, intresting we got 200 status code
print(r.text)