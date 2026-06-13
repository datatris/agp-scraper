import os
import json
from playwright.sync_api import sync_playwright

USERNAME = os.environ["DSCTris"]
PASSWORD = os.environ["Sampo11!"]

URL = "https://allegegenpistorwm.wdr2.de/start.php"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Seite öffnen
        page.goto(URL, wait_until="networkidle")

        # Login (Selector ggf. anpassen!)
        page.fill('input[name="username"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)

        page.click('input[type="submit"], button[type="submit"]')

        page.wait_for_load_state("networkidle")

        # Beispiel: HTML speichern
        html = page.content()

        with open("page.html", "w", encoding="utf-8") as f:
            f.write(html)

        # Beispiel: Cookies speichern
        cookies = context.cookies()

        with open("cookies.json", "w") as f:
            json.dump(cookies, f, indent=2)

        print("Fertig")

        browser.close()

if __name__ == "__main__":
    run()
