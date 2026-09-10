import json

with open("investigation_log.jsonl", encoding="utf-8") as f:
    lines = f.readlines()

# Find the most recent entry that has real set-cookie data
for line in reversed(lines):
    entry = json.loads(line)
    headers = entry.get("response", {}).get("headers", {})
    set_cookie = headers.get("set-cookie", "")
    if "bm_s=" in set_cookie:
        print("Found in test:", entry["test"])
        # Parses each cookie out properly
        cookies = {}
        for part in set_cookie.split("\n"):
            if "=" in part:
                key_value = part.split(";")[0]  # drop Domain=, Path=, etc.
                if "=" in key_value:
                    k, v = key_value.split("=", 1)
                    cookies[k.strip()] = v.strip()
        
        for name in ["bm_s", "_abck", "bm_sz", "bm_so"]:
            if name in cookies:
                print(f"\n{name}:")
                print(cookies[name])
        break