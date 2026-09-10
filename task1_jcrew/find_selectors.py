from bs4 import BeautifulSoup
import re

html = open("jcrew.html", encoding="utf-8").read()
soup = BeautifulSoup(html, "html.parser")

print("Title guess:", soup.select_one("h1"))   #For this I got lucky that there was onlt one h1 which I saw from dev tools, thats why I am using it.

# Searchies HTML text directly for anything near "$128"
# idx = html.find("$128")
# print(html[idx-300:idx+50])

# idx2 = html.find("Union Blue")
# print(html[idx2-200:idx2+30])

# print("Price guess:", soup.select_one(".ProductColor__price___K8vPV"))  
# print("Color guess:", soup.select_one(".ProductColor__color-name___caUX_"))  # Nowww even thoughtt that we found this that last "caUX_" looks to me auto genearated soo,
                                                                             # even thought it might work now it will change thats why better approach woudl be to use "data-testid"

print("Price guess:", soup.select_one('[data-testid="price"]'))
print("Color guess:", soup.select_one('[data-testid="color-name"]'))


# Now this was one way of doing things, now lets do checking second way which for me is kind of more intresting and stable, ifff J.crew has JSON-LD block somewhere in the raw HTML

print("\n--- JSON-LD check ---")
scripts = soup.find_all("script", type="application/ld+json")
print("Number of JSON-LD blocks found:", len(scripts))

for tag in scripts:
   # print(tag.string[:500])
   if '"@type":"Product"' in tag.string:
        print(tag.string)            #Now we are talking, name, price, and color are all sitting right there

