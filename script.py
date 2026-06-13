import os
import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

BASE_URL = "https://allegegenpistorwm.wdr2.de/tipprunde_punkte_detail.php?id=4833&spieltag="

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Login
        page.goto("https://allegegenpistorwm.wdr2.de/start.php", wait_until="domcontentloaded")

        page.wait_for_timeout(2000)

        page.locator('input[name="username"]').fill(USERNAME)
        page.locator('input[name="password"]').fill(PASSWORD)

        page.locator('input[type="submit"], button[type="submit"]').first.click()

        page.wait_for_timeout(3000)

        all_spieltage = []

        # Spieltage scrapen
        for spieltag in range(1, 38):
            url = f"{BASE_URL}{spieltag}"
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(1000)

            html = page.content()
            
            soup = BeautifulSoup(html, "lxml")
            
            tables = soup.select("table.table")
            
            for table in tables:
            
                spieler = table.get("id", "").replace("_", "")
            
                rows = table.select("tbody tr")
            
                for row in rows:
            
                    cols = row.select("td")
            
                    if len(cols) < 4:
                        continue
            
                    begegnung = cols[0].get_text(" ", strip=True)
                    tipp = cols[1].get_text(" ", strip=True)
                    ergebnis = cols[2].get_text(" ", strip=True)
                    punkte = cols[3].get_text(" ", strip=True)
            
                    if punkte == "-":
                        punkte = None
            
                    all_spieltage.append({
                        "spieltag": spieltag,
                        "Name": spieler,
                        "Begegnung": begegnung,
                        "Tipp": tipp,
                        "Ergebnis": ergebnis,
                        "Punkte": punkte
                    })

        # JSON INS REPO SPEICHERN
        with open("spieltage.json", "w", encoding="utf-8") as f:
            json.dump(all_spieltage, f, indent=2, ensure_ascii=False)

        browser.close()

if __name__ == "__main__":
    run()
