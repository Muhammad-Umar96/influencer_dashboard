import requests
import re
import json
import urllib.parse
from bs4 import BeautifulSoup

API_KEY = "6e3b7237e30242a9936b2ef285174b07816fee17e0c"

def get_facebook_data(fb_url):
    try:
        api_url = f"https://api.scrape.do?token={API_KEY}&url={fb_url}&render=true"
        response = requests.get(api_url, timeout=100)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        page_name = None
        followers = None
        following = None
        image = None
        category = None

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

        og_image = soup.find("meta", property="og:image")
        if og_image:
            image = og_image.get("content")

        # get category
        match = re.search(r'"text"\s*:\s*"Page \\u00b7 ([^"]+)"', html)
        if match:
            category = match.group(1).strip()

        return {
            "platform": "Facebook",
            "url": fb_url,
            "page_name": page_name,
            "followers": followers,
            "following": following,
            "image": image,
            "category": category
        }

    except Exception as e:
        print(f"FACEBOOK SCRAPER ERROR: {str(e)}")
        return {
            "platform": "Facebook",
            "url": fb_url,
            "page_name": None,
            "followers": None,
            "following": None,
            "image": None,
            "category": None
        }

def get_instagram_data(ig_url):
    try:
        # extract username from URL
        username_match = re.search(r'instagram\.com/([^/?]+)', ig_url)
        username = username_match.group(1) if username_match else None

        api_url = f"https://api.scrape.do?token={API_KEY}&url={ig_url}&render=true"
        response = requests.get(api_url, timeout=100)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        page_name = None
        followers = None
        following = None
        image = None
        category = None

        # get page name from title
        title = soup.find("title")
        if title:
            page_name = title.text
            page_name = re.sub(r'\s*photos and videos.*$', '', page_name, flags=re.IGNORECASE)
            page_name = re.sub(r'\s*•\s*Instagram.*$', '', page_name, flags=re.IGNORECASE)
            page_name = re.sub(r'\s*\(@.*?\)', '', page_name)
            page_name = page_name.strip()

        # get followers and following from meta description
        description = soup.find("meta", {"name": "description"})
        if description:
            content = description.get("content", "")
            match = re.search(r'([\d,.]+[KMB]?)\s*Followers', content)
            if match:
                followers = match.group(1).strip()
            match = re.search(r'([\d,.]+[KMB]?)\s*Following', content)
            if match:
                following = match.group(1).strip()

        # get profile image
        og_image = soup.find("meta", property="og:image")
        if og_image:
            image = og_image.get("content")

        # get category via Instagram GraphQL API
        if username:
            try:
                graphql_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
                encoded = urllib.parse.quote_plus(graphql_url)
                proxy_url = f"https://api.scrape.do?token={API_KEY}&url={encoded}"
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    "X-IG-App-ID": "936619743392459",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": "https://www.instagram.com/",
                }
                cat_response = requests.get(proxy_url, headers=headers, timeout=60)
                user = cat_response.json().get("data", {}).get("user", {})
                category = user.get("category_name")
            except Exception as e:
                print(f"CATEGORY ERROR: {str(e)}")
                category = None

        return {
            "platform": "Instagram",
            "url": ig_url,
            "page_name": page_name,
            "followers": followers,
            "following": following,
            "image": image,
            "category": category or ""
        }

    except Exception as e:
        print(f"INSTAGRAM SCRAPER ERROR: {str(e)}")
        return {
            "platform": "Instagram",
            "url": ig_url,
            "page_name": None,
            "followers": None,
            "following": None,
            "image": None,
            "category": None
        }

def get_youtube_data(yt_url):
    try:
        YT_API_KEY = "AIzaSyDJc_K70TwrCA6YjDrfb2XkOQsESBcnuNg"

        match = re.search(r'youtube\.com/@([\w\-]+)', yt_url)
        if not match:
            return {
                "platform": "YouTube",
                "url": yt_url,
                "channel_name": None,
                "subscribers": None,
                "error": "Invalid YouTube URL"
            }

        username = match.group(1)

        # search for channel by username
        search_url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "part": "snippet,statistics",
            "forHandle": username,
            "key": YT_API_KEY
        }

        response = requests.get(search_url, params=params, timeout=30)
        data = response.json()

        if not data.get("items"):
            return {
                "platform": "YouTube",
                "url": yt_url,
                "channel_name": None,
                "subscribers": None,
                "error": "Channel not found"
            }

        channel = data["items"][0]
        page_name = channel["snippet"]["title"]
        subscribers = int(channel["statistics"].get("subscriberCount", 0))
        image = channel["snippet"]["thumbnails"]["high"]["url"]


        # format subscriber count like 1.2M, 500K etc
        if subscribers >= 1_000_000:
            subscribers = f"{subscribers / 1_000_000:.1f}M"
        elif subscribers >= 1_000:
            subscribers = f"{subscribers / 1_000:.1f}K"
        else:
            subscribers = str(subscribers)

        return {
            "platform": "YouTube",
            "url": yt_url,
            "channel_name": page_name,
            "subscribers": subscribers,
            "image": image,
        }

    except Exception as e:
        print(f"YOUTUBE SCRAPER ERROR: {str(e)}")
        return {
            "platform": "YouTube",
            "url": yt_url,
            "channel_name": None,
            "subscribers": None,
        }

def get_tiktok_data(tt_url):
    try:
        api_url = f"https://api.scrape.do?token={API_KEY}&url={tt_url}&render=true"
        response = requests.get(api_url, timeout=100)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        page_name = None
        followers = None
        following = None
        image = None

        # get page name from JSON data (more reliable than title tag)
        match = re.search(r'"nickname"\s*:\s*"([^"]+)"', html)
        if match:
            page_name = match.group(1).strip()

        # fallback: try uniqueId (username) if nickname not found
        if not page_name:
            match = re.search(r'"uniqueId"\s*:\s*"([^"]+)"', html)
            if match:
                page_name = match.group(1).strip()

        # fallback: try title tag
        if not page_name:
            title = soup.find("title")
            if title:
                page_name = title.text
                page_name = re.sub(r'\s*\|.*$', '', page_name)
                page_name = re.sub(r'\s*-.*$', '', page_name)
                page_name = page_name.strip()
                if page_name.lower() == "tiktok":
                    page_name = None

        # get profile image from JSON data
        match = re.search(r'"avatarLarger"\s*:\s*"([^"]+)"', html)
        if match:
            image = match.group(1).replace('\\u002F', '/').strip()

        # fallback to avatarMedium
        if not image:
            match = re.search(r'"avatarMedium"\s*:\s*"([^"]+)"', html)
            if match:
                image = match.group(1).replace('\\u002F', '/').strip()

        # fallback to og:image
        if not image:
            og_image = soup.find("meta", property="og:image")
            if og_image:
                image = og_image.get("content")

        # get followers from JSON data
        match = re.search(r'"followerCount"\s*:\s*(\d+)', html)
        if match:
            count = int(match.group(1))
            if count >= 1_000_000:
                followers = f"{count / 1_000_000:.1f}M"
            elif count >= 1_000:
                followers = f"{count / 1_000:.1f}K"
            else:
                followers = str(count)

        # get following from JSON data
        match = re.search(r'"followingCount"\s*:\s*(\d+)', html)
        if match:
            count = int(match.group(1))
            following = str(count)

        return {
            "platform": "TikTok",
            "url": tt_url,
            "page_name": page_name,
            "followers": followers,
            "following": following,
            "image": image
        }

    except Exception as e:
        print(f"TIKTOK SCRAPER ERROR: {str(e)}")
        return {
            "platform": "TikTok",
            "url": tt_url,
            "page_name": None,
            "followers": None,
            "following": None,
            "image": None
        }

def scrape(url):
    if "instagram.com" in url:
        return get_instagram_data(url)
    elif "facebook.com" in url:
        return get_facebook_data(url)
    elif "youtube.com" in url:
        return get_youtube_data(url)
    elif "tiktok.com" in url:
        return get_tiktok_data(url)
    else:
        return {
            "platform": None,
            "url": url,
            "page_name": None,
            "followers": None,
            "following": None,
            "error": "Unsupported platform. Please use Facebook, Instagram, YouTube or TikTok URL."
        }


if __name__ == "__main__":
    print(scrape("https://www.instagram.com/natgeo"))
    print(scrape("https://www.facebook.com/natgeo"))
    print(scrape("https://www.youtube.com/@natgeo"))
    print(scrape("https://www.tiktok.com/@natgeo"))