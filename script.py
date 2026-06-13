import os
import json
from playwright.sync_api import sync_playwright

USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

BASE_URL = "https://allegegenpistorwm.wdr2.de/tipprunde_punkte_detail.php?id=4833&spieltag="

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 1. Login Seite öffnen
        page.goto("https://allegegenpistorwm.wdr2.de/start.php", wait_until="networkidle")

        # 2. Login ausführen
        page.fill('input[name="username"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.click('input[type="submit"], button[type="submit"]')
        page.wait_for_load_state("networkidle")

        all_data = []

        # 3. Loop über Spieltage
        for spieltag in range(1, 5):
            url = f"{BASE_URL}{spieltag}"
            print(f"Scrape Spieltag {spieltag}: {url}")

            page.goto(url, wait_until="networkidle")

            # optional: kleine Pause gegen Rate-Limits
            page.wait_for_timeout(800)

            html = page.content()

            all_data.append({
                "spieltag": spieltag,
                "html": html
            })

        # 4. speichern
        with open("spieltage.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

        print("Fertig!")

        browser.close()

if __name__ == "__main__":
    run()
