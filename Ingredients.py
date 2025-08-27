from bs4 import BeautifulSoup
import requests
import json
import random
import time
import pandas as pd
import csv

base ="https://www.halfbakedharvest.com/sitemap_index.xml"
header = {"User-Agent": "ingredient_bot/1.0 (+mailto:jakehowell@duck.com; for educational purposes)"}

def parseXML(url):
    site_mapXML = requests.get(url, headers = header,)

    soup = BeautifulSoup(site_mapXML.text, "xml")

    site_maps = []
    for loc_tag in soup.find_all("loc"):
        loc_tag = loc_tag.get_text(strip = True)
        if loc_tag[-3:] == "jpg" or loc_tag[-3:] == "png" or loc_tag[-4:] == "jpeg":
            continue
        elif loc_tag[-3:] != "jpg" or loc_tag[-3:] == "png" and loc_tag not in site_maps:
            site_maps.append(loc_tag)
    return site_maps

site_map = parseXML(base)
print(site_map)

links = []
links.append(parseXML(site_map[1]))

df = pd.read_csv("output.csv")

s = requests.Session()
counter = 0
number_of_links = 50
errlog = []

for url in links[0]:
    if url in set(df['url'].values):
        print(f"Url: {url}, already exists in dataset")
        continue
    resp = s.get(url, headers = header)
    soup = BeautifulSoup(resp.text, "html.parser")

    scripts = soup.find("script", type = "application/ld+json")
    try:
        data = json.loads(scripts.string)
    except AttributeError:
        errlog.append(url)
        continue
    info = data["@graph"][0]
    headline = info["headline"]
    keywords = info["keywords"]
    date_published = info["datePublished"]

    ingredients = soup.find_all("span", class_ = "wprm-recipe-ingredient-name")
    ingredient_list = [span.get_text(strip=True) for span in ingredients]
    
    if url not in df['url']: 
        df.loc[len(df)] = [headline, date_published, url, ingredient_list, keywords]

    resp.raise_for_status()  # raise for 4xx/5xx
    print(f"Success: {url} (status {resp.status_code})")

    counter += 1
    if counter >= number_of_links:
        break
    else:
        print(f"{number_of_links - counter} more links.")

    delay = random.uniform(1, 5)
    print(f"Sleeping {delay:.2f}s before next request...")
    time.sleep(delay)

df.to_csv("output.csv", index= False)
with open("err.csv", "a", newline= '') as file:
    writer = csv.writer(file)
    writer.writerow(errlog)

print(df.info())