html = open("jcrew.html", encoding="utf-8").read()

print("File length:", len(html))
print("Contains 'Access Denied':", "Access Denied" in html)
print("Contains 'captcha' (case-insensitive):", "captcha" in html.lower())

idx = html.lower().find("captcha")
print(html[idx-200:idx+200])