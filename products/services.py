import requests
import time
from bs4 import BeautifulSoup as bs
from rest_framework.exceptions import ValidationError

def get_site_product(url):
    """
    Scrapes Jumia Kenya for product details.
    Returns a dict: {'name': str, 'price': float, 'sku': str} or None.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DiltruBot/1.0)",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    try:
        # Rate limiting protection
        time.sleep(1) 
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 403:
            print("Error: Access denied by Jumia (403).")
            return None

        response.raise_for_status()
        soup = bs(response.content, 'html.parser')

        # 1. Extract Name
        name_tag = soup.find('h1')
        name = name_tag.text.strip() if name_tag else "Unknown Product"

        # 2. Extract Price (Jumia specific class)
        # Note: Jumia classes change often. If this breaks, we update this line.
        price_tag = soup.find(class_="-b -ubpt -tal -fs24 -prxs")
        if price_tag:
            # "KSh 25,000" -> "25000"
            raw_price = price_tag.text.split(" ")[-1].replace(",", "")
            price = float(raw_price)
        else:
            price = 0.0
   
        # 3. Extract SKU (Critical for our new database logic)
        # Jumia usually lists SKU in a 'span' sibling to 'SKU:'
        sku_tag = soup.find("span", string="SKU")
        if sku_tag:
            sku = sku_tag.parent.get_text(strip=True).replace("SKU:", "").strip()
        else:
            sku = None

        return {
            "name": name,
            "price": price,
            "sku": sku,
            'is_available': True
        }
    
    except Exception as e:
        print(f"Scraping Error: {e}")
        return None