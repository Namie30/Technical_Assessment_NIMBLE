import requests
import base64
import time
import json
from datetime import datetime

def log_result(test_name, status_code, response_body):
    entry = {
        "test": test_name,
        "timestamp": datetime.now().isoformat(),
        "http_status": status_code,
        "response": response_body
    }
    with open("investigation_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# Credentials from the task brief - replace with real values before running.
#
# In production these would be environment variables or a secrets manager
# rather than inline placeholders. Kept inline here for a self-contained
# submission that's easy to read and run without extra setup.
EMAIL = "your-email-here"
PASSWORD = "your-password-here"

cred = base64.b64encode(f"{EMAIL}:{PASSWORD}".encode()).decode()

payload = {
    "country": "US",   # This is good tells Nimble to use US IP due to Home Depot being a US retailer and not to look suspicious suspicious to Akamai
    "url": "apionline.homedepot.com/federation-gateway/graphql?opname=storeFulfillment",
    "driver": "vx10-pro",
    "cookies": [
        {"key": "bm_s", "value": "PLACEHOLDER_stale_cookie_value_here"}
    ],
    "body": "{\"operationName\":\"storeFulfillment\",\"variables\":{\"itemId\":325573249,\"keyword\":\"10001\",\"requestContext\":{\"calculationOverride\":14}},\"query\":\"query storeFulfillment { ... }\"}"
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

# print("BASELINE TEST")
print("DRIVER TEST (vx10-pro)")
print("Status:", r.status_code)
print(r.json())
log_result("driver_vx10_pro", r.status_code, r.json())

'''
                 # TRY 1

print("\n--- NETWORK CAPTURE TEST ---")

payload_capture = {
    "country": "US",
    "url": "https://www.homedepot.com/",
    "render": True,
    "network_capture": [
        {
            "method": "POST",
            "url": {
                "type": "contains",
                "value": "storeFulfillment"
            }
        }
    ]
}

r_capture = requests.post(
    "https://api.webit.live/api/v1/realtime/web",
    headers={
        "Authorization": f"Basic {cred}",
        "Content-Type": "application/json",
    },
    json=payload_capture,
    timeout=180,
)

print("Status:", r_capture.status_code)
# print(r_capture.json())
# log_result("network_capture_homedepot_home", r_capture.status_code, r_capture.json())
print("Network capture results:", r_capture.json().get("network_capture"))
log_result("network_capture_homedepot_home", r_capture.status_code, r_capture.json())


                      # TRY 2

print("\n--- NETWORK CAPTURE TEST (product page) ---")
print("Starting at:", time.strftime("%H:%M:%S"))

payload_capture2 = {
    "country": "US",
    "url": "https://www.homedepot.com/p/GE-4-5-cu-ft-Top-Load-Washer-in-White-with-Dual-Action-Agitator-and-Cold-Plus-Sanitize-with-Oxi-GTW485ASWWB/328425526",
    "render": True,
    "network_capture": [
        {
            "method": "POST",
            "url": {
                "type": "contains",
                "value": "storeFulfillment"
            }
        }
    ]
}

try:
    r_capture2 = requests.post(
        "https://api.webit.live/api/v1/realtime/web",
        headers={
            "Authorization": f"Basic {cred}",
            "Content-Type": "application/json",
        },
        json=payload_capture2,
        timeout=60,
    )
    print("Status:", r_capture2.status_code)
    print("Network capture results:", r_capture2.json().get("network_capture"))
    log_result("network_capture_product_page", r_capture2.status_code, r_capture2.json())
except requests.exceptions.ReadTimeout:
    print("TIMED OUT after 60s")
    log_result("network_capture_product_page", "TIMEOUT", {"error": "read timeout after 60s"})


                          # TRY 3

print("\n--- DEDICATED E-COMMERCE ENDPOINT TEST ---")

payload_ecommerce = {
    "vendor": "homedepot",
    "url": "https://www.homedepot.com/p/GE-4-5-cu-ft-Top-Load-Washer-in-White-with-Dual-Action-Agitator-and-Cold-Plus-Sanitize-with-Oxi-GTW485ASWWB/328425526",
    "country": "US",
    "zip": "10001",
    "parse": True,
}

try:
    r_ecom = requests.post(
        "https://api.webit.live/api/v1/realtime/ecommerce",
        headers={
            "Authorization": f"Basic {cred}",
            "Content-Type": "application/json",
        },
        json=payload_ecommerce,
         timeout=90,
         # timeout=180,
    )
    print("Status:", r_ecom.status_code)
    data = r_ecom.json()
    print("Response status:", data.get("status"))
    print("Parsed entities:", list(data.get("parsing", {}).get("entities", {}).keys()) if data.get("parsing") else None)
    log_result("dedicated_ecommerce_homedepot", r_ecom.status_code, data)
except requests.exceptions.ReadTimeout:
    print("TIMED OUT after 90s")
    log_result("dedicated_ecommerce_homedepot", "TIMEOUT", {"error": "read timeout after 90s"})

    
                               # TRY 4

print("\n--- DEDICATED E-COMMERCE ENDPOINT TEST (simple product) ---")

payload_ecommerce2 = {
    "vendor": "homedepot",
    "url": "https://www.homedepot.com/p/The-Home-Depot-5-Gallon-Orange-Homer-Bucket-05GLHD2/100087613",
    "country": "US",
    "zip": "10001",
    "parse": True,
}

try:
    r_ecom2 = requests.post(
        "https://api.webit.live/api/v1/realtime/ecommerce",
        headers={
            "Authorization": f"Basic {cred}",
            "Content-Type": "application/json",
        },
        json=payload_ecommerce2,
        timeout=90,
    )
    print("Status:", r_ecom2.status_code)
    data2 = r_ecom2.json()
    print("Response status:", data2.get("status"))
    print("Parsed entities:", list(data2.get("parsing", {}).get("entities", {}).keys()) if data2.get("parsing") else None)
    log_result("dedicated_ecommerce_simple_product", r_ecom2.status_code, data2)
except requests.exceptions.ReadTimeout:
    print("TIMED OUT after 90s")
    log_result("dedicated_ecommerce_simple_product", "TIMEOUT", {"error": "read timeout after 90s"})

    
                            # TRY 5

print("\n--- HTTP_REQUEST INSIDE RENDER_FLOW TEST ---")
print("Starting at:", time.strftime("%H:%M:%S"))

payload_http_request = {
    "country": "US",
    "url": "https://www.homedepot.com/p/The-Home-Depot-5-Gallon-Orange-Homer-Bucket-05GLHD2/100087613",
    "render": True,
    "render_flow": [
        {
            "wait": {"delay": 3000}
        },
        {
            "http_request": {
                "url": "https://apionline.homedepot.com/federation-gateway/graphql?opname=storeFulfillment",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                },
                "timeout": 15000
            }
        }
    ]
}

try:
    r_flow = requests.post(
        "https://api.webit.live/api/v1/realtime/web",
        headers={
            "Authorization": f"Basic {cred}",
            "Content-Type": "application/json",
        },
        json=payload_http_request,
        timeout=90,
    )
    print("Status:", r_flow.status_code)
    data_flow = r_flow.json()
    print("Render flow result:", data_flow.get("render_flow"))
    log_result("http_request_in_render_flow", r_flow.status_code, data_flow)
except requests.exceptions.ReadTimeout:
    print("TIMED OUT after 90s")
    log_result("http_request_in_render_flow", "TIMEOUT", {"error": "read timeout after 90s"})
    

                           # TRY 6

print("\n--- METHOD FIX TEST (explicit POST) ---")

payload_method_fix = {
    "country": "US",
    "url": "apionline.homedepot.com/federation-gateway/graphql?opname=storeFulfillment",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json"
    },
    "cookies": [
        {"key": "bm_s", "value": "PLACEHOLDER_stale_cookie_value_here"}
    ],
    "body": "{\"operationName\":\"storeFulfillment\",\"variables\":{\"itemId\":325573249,\"keyword\":\"10001\",\"requestContext\":{\"calculationOverride\":14}},\"query\":\"query storeFulfillment { ... }\"}"
}

try:
    r_method = requests.post(
        "https://api.webit.live/api/v1/realtime/web",
        headers={
            "Authorization": f"Basic {cred}",
            "Content-Type": "application/json",
        },
        json=payload_method_fix,
        timeout=200,
    )
    print("Status:", r_method.status_code)
    print(r_method.json())
    log_result("method_fix_post", r_method.status_code, r_method.json())
except requests.exceptions.ReadTimeout:
    print("TIMED OUT after 200s")
    log_result("method_fix_post", "TIMEOUT", {"error": "read timeout after 200s"})


                             # TRY 7

# Cookies below were captured live from TRY 1's session during testing.
# Left in place to show what was actually sent, they're expired session
# tokens, so re-running this requires capturing fresh ones.

print("\n--- METHOD FIX + REAL FRESH COOKIE TEST ---")

payload_fresh_cookie = {
    "country": "US",
    "url": "apionline.homedepot.com/federation-gateway/graphql?opname=storeFulfillment",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json"
    },
    "cookies": [
        {"key": "bm_s", "value": "YAAQDsfdF3nT3nagAQAA8oXUhwb6AHyUgdcm33dd2gooe0hY7YAXO716bztIevd0BkeT9udGDKB70VBZQ33pFbj69hyyh3yQtvZgY3JMou1EXU1ckWkMqoCuz4lC7ufGqAURW8QhSYapoNhCIcz9blLdvrEDfpPw6heqNBBx6laaMcsj3+/BWcE2kS/raMy6pyoaf8yWQJT4wfxeQgHYkQNNf69uLLySYZyjW8JQtvkDJdRtmvWAUWmtzhOB8z3VU11uX1o0HbfHApl3fPW6eJ7xyibXigKQdnctBGZK79AOEga8diepCepbQb7rtSCNC0azi82zBlVnViZ6acV1zSt0vSvd/h1haWoam2uVj8jFijYNbICUw+UhprF9KJbgFdSRHoNuPhAt/s3CzOAFFmxDTHaaXSufpmQgQq44emz90vzrHUKVgH5kxILw/CxK1chSLyJ1y4Q5hqoEXjnUNYKVZ6LRkwrJ8HHJKD1/HhJe00YomAA/fU7kXM8cORfIywqsIBTGLHphpKreJcpiymYC3bVX0g0B6zBU0Cs91bPKt8EExQ2MAYCX8mZ1/T++23TdlqnJIIUaZGAspYYz+TCXaUW7/hhw7vK+3/+3tqAmuQPjcQjKX3wTrf/6UCT+0TnjnsYfblgNQPoKl3z/ifjxhSJYDpStpQHT7TYSuPw+e6tKahTm807TINzHLfGZl+AAEh7bANg+OZY44M2aX9qj/jGXpJ/OyF6GLH2PkwOP3A8GAFnOE4I2ZuThMj0raNu4J84HaRVGSq/wcwCvmxwYuozvekFZmfBSoJq743RYqQSjC4TIsiUuhDubKRt6ivlhfKEXJkdoh7SPhE1Di18O4FrLoB+p0yfrkRiW+icyIFuJm+FTGIOsTvcVtcO1FlXvIcORO4rnxTTHnNpSDZ9YRu6VbLowAT5ZimGJGfAVqq0/gp2ex2tC6HWnRTbG"},
        {"key": "_abck", "value": "A76EFB36B40068BEA5E84B111FE180E9~-1~YAAQDsfdF3fT3nagAQAA8oXUhxDduYz6U18DrXGYDd0Y1LBOJ8kGTEQU3if8D+vmrU3E1kE2EnkOtfbTeKWQZlOekFP7mQJE3rz1XcAbzJKu3bKy2ubjy67utvhabCY2V3czhJGvyfzc0KMZJ4Jp8cJ1q76ir4qrhYIWZd9B+bX58m5U9SGTmXXfvRHWbvR4yfoSTq51zdLPJT+LMNWVTf1dD2mYJxfkhjN7xmPyXRuVK/biPVup35hSCNyUqhury1prwTnp/HuFjBDGR5lNYtNJp9vq0+MeGAYqsY/aybdkTl0GRea0eVHRCA1Uo6mZsu6lBcqBpaFEWX09NaBcKGFnpZ/STLG0ozGxvgHoYnu8YSLga2veeHovKch+LV2/l4M4vXT2yjtV1K/Z89iuV3DhA9kBzLefccErEYuuoels5jS01g8GNARAwyc78RqyvSW0/VdMv+IAcYk=~-1~-1~-1~-1~-1"},
        {"key": "bm_sz", "value": "857B2D02A1322DB6FFBA57638255D4F8~YAAQDsfdF3vT3nagAQAA8oXUhwEsYWnA/4JZ0+DTqAWaaEi06l1JSRvZr/QH8OT7WHuhld9lODp5rawC7wLLcFhhyJjT6iJ5SEo2tiBAEQL7RR6OZHbbO24QDZqYZ+nXwZjRB4g+GG1hGH8UWYCxlxpru7PbkD+Yjdjt5GIUGjDj+Af/fvsLjaSL3LvVYkgm+ehZoc7LAlz5oqWzmMpW9LoTvmWntpJ91QS32mPgViyRe/rFDmk005gQnuAY7Eo1/w6tZsVJ7RMcfWowvjbW79Tpk67quctPCWQUb3LaEEFkAlcyaci9Z46n5YN5FwEzbw9qsG6EBcn1yzOUhC73FubAeohe1TFzXs9QrwbprUEra/y0MxrifTa9pOdkGHKTVdJY/EqO53evsyGtMwaLHA==~3551302~3683633"}
    ],
    "body": "{\"operationName\":\"storeFulfillment\",\"variables\":{\"itemId\":325573249,\"keyword\":\"10001\",\"requestContext\":{\"calculationOverride\":14}},\"query\":\"query storeFulfillment { ... }\"}"
}

try:
    r_fresh = requests.post(
        "https://api.webit.live/api/v1/realtime/web",
        headers={
            "Authorization": f"Basic {cred}",
            "Content-Type": "application/json",
        },
        json=payload_fresh_cookie,
        timeout=90,
    )
    print("Status:", r_fresh.status_code)
    print(r_fresh.json())
    log_result("method_fix_fresh_cookie", r_fresh.status_code, r_fresh.json())
except requests.exceptions.ReadTimeout:
    print("TIMED OUT after 90s")
    log_result("method_fix_fresh_cookie", "TIMEOUT", {"error": "read timeout after 90s"})

    
                        # TRY 8   
    
print("\n--- SAME-SESSION: GET COOKIES + IMMEDIATE HTTP_REQUEST ---")

payload_same_session = {
    "country": "US",
    "url": "https://www.homedepot.com/p/The-Home-Depot-5-Gallon-Orange-Homer-Bucket-05GLHD2/100087613",
    "render": True,
    "render_flow": [
        {"wait": {"delay": 2000}},
        {"get_cookies": {"timeout": 1000}},
        {
            "http_request": {
                "url": "https://apionline.homedepot.com/federation-gateway/graphql?opname=storeFulfillment",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "timeout": 15000
            }
        }
    ]
}

try:
    r_same = requests.post(
        "https://api.webit.live/api/v1/realtime/web",
        headers={"Authorization": f"Basic {cred}", "Content-Type": "application/json"},
        json=payload_same_session,
        timeout=200,
    )
    print("Status:", r_same.status_code)
    data_same = r_same.json()
    print("Render flow result:", data_same.get("render_flow"))
    log_result("same_session_cookies_and_request", r_same.status_code, data_same)
except requests.exceptions.ReadTimeout:
    print("TIMED OUT after 200s")
    log_result("same_session_cookies_and_request", "TIMEOUT", {"error": "read timeout after 200s"})
    
    
                        # TRY 9   

print("\n--- DIRECT CALL + ORIGIN/REFERER + NY GEO TEST ---")

payload_headers_fix = {
    "country": "US",
    "state": "NY",
    "url": "apionline.homedepot.com/federation-gateway/graphql?opname=storeFulfillment",
    "driver": "vx10-pro",
    # "method": "POST",
    "headers": {
        "Content-Type": "application/json",
        "Origin": "https://www.homedepot.com",
        "Referer": "https://www.homedepot.com/p/The-Home-Depot-5-Gallon-Orange-Homer-Bucket-05GLHD2/100087613"
    },
    "cookies": [
        {"key": "bm_s", "value": "PLACEHOLDER_stale_cookie_value_here"}
    ],
    "body": "{\"operationName\":\"storeFulfillment\",\"variables\":{\"itemId\":325573249,\"keyword\":\"10001\",\"requestContext\":{\"calculationOverride\":14}},\"query\":\"query storeFulfillment { ... }\"}"
}

try:
    r_headers = requests.post(
        "https://api.webit.live/api/v1/realtime/web",
        headers={"Authorization": f"Basic {cred}", "Content-Type": "application/json"},
        json=payload_headers_fix,
        timeout=90,
    )
    print("Status:", r_headers.status_code)
    print(r_headers.json())
    log_result("origin_referer_ny_geo_test", r_headers.status_code, r_headers.json())
except requests.exceptions.ReadTimeout:
    print("TIMED OUT after 90s")
    log_result("origin_referer_ny_geo_test", "TIMEOUT", {"error": "read timeout after 90s"})


'''

                          # TRY 10

print("\n--- TRY 10: is_xhr TEST ---")
print("Starting at:", time.strftime("%H:%M:%S"))

payload_xhr = {
    "country": "US",
    "state": "NY",
    "url": "https://apionline.homedepot.com/federation-gateway/graphql?opname=storeFulfillment",
    "method": "POST",
    "is_xhr": True,
    "headers": {
        "Content-Type": "application/json",
        "Origin": "https://www.homedepot.com",
        "Referer": "https://www.homedepot.com/"
    },
    "body": "{\"operationName\":\"storeFulfillment\",\"variables\":{\"itemId\":325573249,\"keyword\":\"10001\",\"requestContext\":{\"calculationOverride\":14}},\"query\":\"query storeFulfillment { ... }\"}"
}

try:
    r_xhr = requests.post(
        "https://api.webit.live/api/v1/realtime/web",
        headers={"Authorization": f"Basic {cred}", "Content-Type": "application/json"},
        json=payload_xhr,
        timeout=90,
    )
    print("Status:", r_xhr.status_code)
    print(r_xhr.json())
    log_result("is_xhr_test", r_xhr.status_code, r_xhr.json())
except requests.exceptions.ReadTimeout:
    print("TIMED OUT after 90s")
    log_result("is_xhr_test", "TIMEOUT", {"error": "read timeout after 90s"})

   
