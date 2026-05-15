import requests
import re
from bs4 import BeautifulSoup

API_KEY = "ef4a116faee84388b23c4b354e43ae73114573cf816"

def get_follower_count(fb_url):
    try:
        api_url = f"https://api.scrape.do?token={API_KEY}&url={fb_url}&render=true"
        
        response = requests.get(api_url, timeout=60)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        body_text = soup.get_text()

        page_name = None
        followers = None
        following = None

        # get page name from title
        title = soup.find("title")
        if title:
            name = title.text
            name = re.sub(r'^\(\d+\)\s*', '', name)
            name = re.sub(r'\s*\|?\s*Facebook$', '', name)
            page_name = name.strip()

        # get followers from JSON data
        match = re.search(r'"text"\s*:\s*"([\d.,]+[KMB]?)\s*followers"', html, re.IGNORECASE)
        if match:
            followers = match.group(1).strip()

        # get following from JSON data
        match = re.search(r'"text"\s*:\s*"([\d.,]+[KMB]?)\s*following"', html, re.IGNORECASE)
        if match:
            following = match.group(1).strip()

        return {
            "url": fb_url,
            "page_name": page_name,
            "followers": followers,
            "following": following,
        }

    except Exception as e:
        print(f"SCRAPER ERROR: {str(e)}")
        return {
            "url": fb_url,
            "page_name": None,
            "followers": None,
            "following": None,
        }


if __name__ == "__main__":
    result = get_follower_count("https://www.facebook.com/natgeo")
    print(result)
