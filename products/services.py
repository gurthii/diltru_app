"""
Web scraping service for Jumia Kenya product pages.
"""
import logging
import time

from curl_cffi import requests
from bs4 import BeautifulSoup as bs

logger = logging.getLogger(__name__)

# Browser-like headers to avoid being blocked by Jumia
# SCRAPING_HEADERS = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/91.0.4472.124 Safari/537.36"
#     ),
# }
SCRAPING_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

def get_site_product(url):
    """
    Scrape a Jumia Kenya product page for basic details.

    Args:
        url: Full Jumia product URL.

    Returns:
        dict with keys ``name``, ``price``, ``sku``, ``is_available``,
        ``image_url`` on success, or ``None`` on failure.
    """
    try:
        # Rate-limiting protection — be polite to Jumia's servers
        time.sleep(1)
        response = requests.get(url, impersonate="chrome120", timeout=10)

        if response.status_code == 403:
            logger.error("Access denied (403) for URL: %s", url)
            return None

        response.raise_for_status()
        soup = bs(response.content, 'html.parser')

        # --- Name ---
        name_tag = soup.find('h1')
        name = name_tag.text.strip() if name_tag else "Unknown Product"
        
        # --- Image ---
        image_url = _extract_image_url(soup)

        # --- Price (Jumia-specific class — may change over time) ---
        price_tag = soup.find(class_="-b -ubpt -tal -fs24 -prxs")
        if price_tag:
            # "KSh 25,000" -> "25000"
            raw_price = price_tag.text.split(" ")[-1].replace(",", "")
            price = float(raw_price)
        else:
            price = 0.0
   
        # --- SKU ---
        sku_tag = soup.find("span", string="SKU")
        if sku_tag:
            sku = sku_tag.parent.get_text(strip=True).replace("SKU:", "").strip()
        else:
            sku = None

        return {
            "name": name,
            "price": price,
            "sku": sku,
            "is_available": True,
            "image_url": image_url,
        }
    
    except Exception:
        logger.exception("Scraping failed for %s", url)
        return None


def _extract_image_url(soup):
    """
    Try to pull the main product image from the parsed page.

    Strategy:
        1. Look for the standard Jumia full-width image tag.
        2. Fall back to the first image inside the gallery container.
    """
    img_tag = soup.find('img', class_="-fw")
    if img_tag:
        url = img_tag.get('data-src') or img_tag.get('src')
        if url:
            return url

    # Fallback: first image in the gallery div
    gallery = soup.find('div', id='imgs')
    if gallery:
        first_img = gallery.find('img')
        if first_img:
            return first_img.get('data-src') or first_img.get('src')

    return None