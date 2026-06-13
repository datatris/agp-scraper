import traceback
try:
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
        page.goto("https://allegegenpistorwm.wdr2.de/start.php")
        
        page.wait_for_timeout(2000)
        
        page.locator('input[name="username"]').fill(USERNAME)
        page.locator('input[name="password"]').fill(PASSWORD)
        
        page.locator('input[type="submit"], button[type="submit"]').first.click()
        
        page.wait_for_timeout(3000)
        print("CURRENT URL:", page.url)
        page.screenshot(path="after_login.png")
        all_data = []

        # 3. Loop über Spieltage
        for spieltag in range(1, 38):
            url = f"{BASE_URL}{spieltag}"
            print("Lade:", url)
        
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(1000)
        
            html = page.content()
        
            all_data.append({
                "spieltag": spieltag,
                "url": url,
                "html_length": len(html),
                "html": html
            })

            print("Gespeichert Spieltag", spieltag)

        # 4. speichern
        with open("spieltage.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

        print("Fertig!")

        browser.close()

if __name__ == "__main__":
    run()

import os

print("CURRENT DIR:", os.getcwd())
print("FILES:", os.listdir())

except Exception as e:
    print("FEHLER:", e)
    traceback.print_exc()
    raise
