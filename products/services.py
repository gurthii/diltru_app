import requests
import time
from bs4 import BeautifulSoup as bs
from rest_framework.exceptions import APIException

def get_site_product(url): #"Returns dictionary with product name and price for given product URL"
    headers = {
        "User-Agent": "DiltruPriceBot/1.0 (+https://github.com/gurthii/diltru_app)",
        "Accept-Language": "en-US,en;q=0.5",
    } # identifies my bot to the site as per their robots.txt
    
    try:
        time.sleep(0.5) # to prevent exceedig 200 requests per minute limit

        response = requests.get(url, headers=headers, timeout=10)

        # handling a 403 forbidden error (blocked by Jumia)    
        if response.status_code == 403:
            print("Access denied by Jumia. Revise User-Agen rules.")
            return None

        response.raise_for_status()
            
        soup = bs(response.content, 'html.parser')

        name_tag = soup.find('h1')
        name = name_tag.text.strip() if name_tag else "Product name not found."

        price_tag = soup.find(class_="-b -ubpt -tal -fs24 -prxs")
        if price_tag:
            raw_price = price_tag.text.split(" ")[-1].replace(",", "")
            price = float(raw_price)
        else:
            price = 0.0
        sku = None
        sku_tag = soup.find("span", string="SKU").parent
        sku = sku_tag.get_text(strip=True).replace("SKU:", "").strip()

        return {
            "name" : name,
            "price" : price,
            "sku" : sku
        }
    
    except requests.exceptions.RequestException as err:
        print(f"Network error: {err}")
        return None
