import os
import json
from playwright.sync_api import sync_playwright

USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

BASE_URL = "https://allegegenpistorwm.wdr2.de/tipprunde_punkte_detail.php?id=4833&spieltag="

TIPPRUNDE_URL = "https://allegegenpistorwm.wdr2.de/spielstand_tipprunde.php"


def scrape_tipprunde(page, teamname):
    page.goto(TIPPRUNDE_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    page.fill('input[name="name"]', teamname)

    page.click('input[type="submit"], button[type="submit"]')

    page.wait_for_timeout(2000)

    html = page.content()

    return {
        "teamname": teamname,
        "html": html,
        "html_length": len(html)
    }


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # LOGIN
        page.goto("https://allegegenpistorwm.wdr2.de/start.php", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        page.locator('input[name="username"]').fill(USERNAME)
        page.locator('input[name="password"]').fill(PASSWORD)

        page.locator('input[type="submit"], button[type="submit"]').first.click()
        page.wait_for_timeout(3000)

        print("Login erfolgreich:", page.url)

        # =========================
        # 1. SPIELTAGE SCRAPEN
        # =========================
        all_spieltage = []

        for spieltag in range(1, 38):
            url = f"{BASE_URL}{spieltag}"

            print("Scrape Spieltag:", spieltag)

            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(1000)

            html = page.content()

            all_spieltage.append({
                "spieltag": spieltag,
                "url": url,
                "html_length": len(html),
                "html": html
            })

        with open("spieltage.json", "w", encoding="utf-8") as f:
            json.dump(all_spieltage, f, indent=2, ensure_ascii=False)

        print("spieltage.json gespeichert")

        # =========================
        # 2. TIPPRUNDE SCRAPEN
        # =========================
        teams = [
            "Die tippen die Römer"
        ]

        all_tipprunden = []

        for team in teams:
            print("Scrape Tipprunde:", team)

            data = scrape_tipprunde(page, team)
            all_tipprunden.append(data)

        with open("tipprunden.json", "w", encoding="utf-8") as f:
            json.dump(all_tipprunden, f, indent=2, ensure_ascii=False)

        print("tipprunden.json gespeichert")

        browser.close()


if __name__ == "__main__":
    run()
