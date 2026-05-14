from playwright.sync_api import sync_playwright
import re

def get_follower_count(fb_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York"
        )
        page = context.new_page()

        try:
            page.goto(fb_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            try:
                page.keyboard.press("Escape")
                page.wait_for_timeout(1000)
            except:
                pass

            content = page.content()
            body_text = page.locator("body").inner_text()

            followers = None
            following = None
            page_name = None

            # get page name from H1 inside main
            try:
                page_name = page.get_by_role("main").locator("h1").inner_text()
                page_name = page_name.strip()
            except:
                pass

            # get followers from body text
            match = re.search(r'([\d.,]+[KMB]?)\s*[Ff]ollowers', body_text)
            if match:
                followers = match.group(1).strip()

            # get following from body text
            match = re.search(r'([\d.,]+[KMB]?)\s*[Ff]ollowing', body_text)
            if match:
                following = match.group(1).strip()

            browser.close()

            return {
                "url": fb_url,
                "page_name": page_name,
                "followers": followers,
                "following": following,
            }

        except Exception as e:
            browser.close()
            return {
                "url": fb_url,
                "page_name": None,
                "followers": None,
                "following": None,
                "status": f"error: {str(e)}"
            }


if __name__ == "__main__":
    result = get_follower_count("https://www.facebook.com/nasa")
    print(result)