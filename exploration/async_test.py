import requests, json, base64, time

EMAIL = "your-email-here"
PASSWORD = "your-password-here"
cred = base64.b64encode(f"{EMAIL}:{PASSWORD}".encode()).decode()

headers = {"Authorization": f"Basic {cred}", "Content-Type": "application/json"}

payload = {
    "url": "https://www.example.com"
    # no storage_type/storage_url  this selects Push/Pull delivery
}

r = requests.post(
    "https://api.webit.live/api/v1/async/web",
    headers=headers,
    json=payload,
    timeout=60,
)

print(r.status_code)
print(r.text)

task = r.json().get("task", {})
task_id = task.get("id")
print("Task ID:", task_id)

# Poll for completion
if task_id:
    status_url = f"https://api.webit.live/api/v1/tasks/{task_id}"
    for _ in range(10):
        time.sleep(5)
        s = requests.get(status_url, headers=headers)
        state = s.json().get("task", {}).get("state")
        print("State:", state)
        if state in ("success", "failed"):
            print(json.dumps(s.json(), indent=2))
            break