import os
import re
import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

BASE_URL = "https://allegegenpistorwm.wdr2.de/tipprunde_punkte_detail.php?id=4833&spieltag="
SEARCH_URL = "https://allegegenpistorwm.wdr2.de/spielstand_einzel.php"

MITSPIELER = [
    "tigerschn",
    "Seitenstiche87",
    "hergis",
    "DSCTris",
    "Saiht_tam",
    "JorinVor",
]


def scrape_spieltage(page):
    all_spieltage = []

    for spieltag in range(1, 38):
        url = f"{BASE_URL}{spieltag}"
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        html = page.content()
        soup = BeautifulSoup(html, "lxml")
        tables = soup.select("table.table")

        # Datum aus <p class="einleitung small"> extrahieren, z.B. "Vorrunde (15.06.26)"
        datum = None
        einleitung = soup.find("p", class_="einleitung small")
        if einleitung:
            match = re.search(r"\((\d{2}\.\d{2}\.\d{2,4})\)", einleitung.get_text())
            if match:
                datum = match.group(1)

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
                    "datum": datum,
                    "Name": spieler,
                    "Begegnung": begegnung,
                    "Tipp": tipp,
                    "Ergebnis": ergebnis,
                    "Punkte": punkte
                })

    return all_spieltage


def scrape_gesamtstand(page):
    gesamtstand = []

    for name in MITSPIELER:
        # Seite laden
        page.goto(SEARCH_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(1500)

        # Formular per JavaScript befüllen und absenden (umgeht Sichtbarkeitsprüfung)
        page.evaluate(f"""
            document.querySelector('input[name="name"]').value = "{name}";
            document.querySelector('input[name="name"]').form.submit();
        """)
        page.wait_for_timeout(2000)

        response_html = page.content()
        soup = BeautifulSoup(response_html, "lxml")

        # Debug: Tabellenstruktur ausgeben
        table = soup.select_one("table.table")
        if not table:
            print(f"[{name}] Kein <table class='table'> gefunden.")
            all_tables = soup.find_all("table")
            print(f"[{name}] Vorhandene Tabellen: {[t.get('class') for t in all_tables]}")
            print(f"[{name}] Response-Anfang: {response_html[:800]}")
            continue

        rows = table.select("tbody tr")
        print(f"[{name}] Tabelle gefunden, {len(rows)} Zeilen")
        for i, row in enumerate(rows[:5]):
            print(f"  Zeile {i}: {[c.get_text(strip=True) for c in row.select('td')]}")
        platz = None

        for row in rows:
            cols = row.select("td")

            # Platz steht nur in der ersten Zeile eines Blocks, danach leer -> FillDown-Logik
            if len(cols) >= 3:
                platz_text = cols[0].get_text(strip=True)
                if platz_text.isdigit():
                    platz = int(platz_text)

                benutzername = cols[1].get_text(strip=True)
                punkte_text = cols[2].get_text(strip=True)

                if benutzername.lower() == name.lower():
                    punkte = int(punkte_text) if punkte_text.isdigit() else None
                    gesamtstand.append({
                        "Benutzername": benutzername,
                        "Platz": platz,
                        "Punkte": punkte
                    })
                    print(f"  {benutzername}: Platz {platz}, {punkte} Punkte")
                    break

    return gesamtstand


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

        # Spieltage scrapen
        print("Scrape Spieltage...")
        all_spieltage = scrape_spieltage(page)

        with open("spieltage.json", "w", encoding="utf-8") as f:
            json.dump(all_spieltage, f, indent=2, ensure_ascii=False)
        print(f"spieltage.json gespeichert ({len(all_spieltage)} Eintraege)")

        # Gesamtstand scrapen
        print("Scrape Gesamtstand...")
        gesamtstand = scrape_gesamtstand(page)

        with open("gesamtstand.json", "w", encoding="utf-8") as f:
            json.dump(gesamtstand, f, indent=2, ensure_ascii=False)
        print(f"gesamtstand.json gespeichert ({len(gesamtstand)} Spieler)")

        browser.close()


if __name__ == "__main__":
    run()
