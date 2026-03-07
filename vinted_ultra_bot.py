import requests
from bs4 import BeautifulSoup
import time
from rapidfuzz import fuzz

WEBHOOK_URL = "https://discord.com/api/webhooks/1479562078976213154/zk8HT1jgoodHyOOSmSMJxyXcY4uJzkwwuHcdiTQtg3qb8CeOnAYjs0idVLVCND_PwmgZ"

max_price = 5000

keywords = [
"iphone","airpods","apple watch","macbook","ipad","ipod",
"ps5","ps4","playstation","nintendo switch","xbox",
"smartwatch","garmin","g-shock","casio","seiko",
"samsung watch","buds","beats","sony xm","bose",
"apple pencil","magic keyboard"
]

typos = [
"iphon","air pod","aple watch","aple","aple wach",
"garminn","casioo","gshock","smarwatch","aple airpods"
]

blocked = [
"uszkodzony","na części","zepsuty","fake","replika",
"nie działa","blokada","icloud"
]

seen = set()

def send_discord(title,price,link):

    data = {
        "embeds":[
            {
                "title":"🔥 OKAZJA VINTED",
                "description":title,
                "url":link,
                "color":65280,
                "fields":[
                    {
                        "name":"Cena",
                        "value":f"{price} zł",
                        "inline":True
                    }
                ]
            }
        ]
    }

    requests.post(WEBHOOK_URL,json=data)


def is_similar(text):

    for word in keywords:

        if fuzz.partial_ratio(word,text) > 85:
            return True

    for word in typos:

        if word in text:
            return True

    return False


def scan():

    headers = {
        "User-Agent":"Mozilla/5.0"
    }

    url = "https://www.vinted.pl/catalog?order=newest_first"

    r = requests.get(url,headers=headers)

    soup = BeautifulSoup(r.text,"html.parser")

    links = soup.find_all("a",href=True)

    for link in links:

        href = link["href"]

        if "/items/" not in href:
            continue

        full = "https://www.vinted.pl"+href

        if full in seen:
            continue

        text = link.get_text().lower()

        if any(word in text for word in blocked):
            continue

        if not is_similar(text):
            continue

        price = None

        for word in text.split():

            if "zł" in word:

                try:
                    price = float(word.replace("zł","").replace(",","."))
                except:
                    pass

        if price and price <= max_price:

            send_discord(text,price,full)

            seen.add(full)


while True:

    print("Skanuję Vinted...")

    try:
        scan()
    except Exception as e:
        print(e)

    time.sleep(20)
