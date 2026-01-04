from playwright.sync_api import sync_playwright
import re
import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo

CSV_FILE = "data.csv"
TIMEZONE = ZoneInfo("Europe/Prague")


def je_v_otviraci_dobe():
    """
    Vrací True, pokud je aktuální čas v ČR mezi 6:00 a 22:00
    """
    now = datetime.now(TIMEZONE)
    return 6 <= now.hour < 22


# Pokud je mimo otvírací dobu, korektně skončíme
if not je_v_otviraci_dobe():
    print("Mimo otvírací dobu – skript končí")
    exit(0)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://www.sutka.eu/")
    page.wait_for_timeout(5000)

    text = page.inner_text("body")

    bazen_match = re.search(r"(\d+)\s*\(Bazén\)", text)
    aquapark_match = re.search(r"(\d+)\s*\(Aquapark\)", text)
    obsazenost_match = re.search(r"(\d+)%\s*obsazenost", text)

    if not (bazen_match and aquapark_match and obsazenost_match):
        raise Exception("Nepodařilo se najít všechna data na stránce")

    bazen = int(bazen_match.group(1))
    aquapark = int(aquapark_match.group(1))
    obsazenost = int(obsazenost_match.group(1))
    celkem = bazen + aquapark

    timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(
                ["timestamp", "bazen", "aquapark", "celkem", "obsazenost"]
            )

        writer.writerow(
            [timestamp, bazen, aquapark, celkem, obsazenost]
        )

    print(
        f"Zapsáno do CSV: "
        f"{timestamp},{bazen},{aquapark},{celkem},{obsazenost}"
    )

    browser.close()
