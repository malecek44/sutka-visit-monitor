from playwright.sync_api import sync_playwright
import re
from datetime import datetime

def je_v_otviraci_dobe():
    hodina = datetime.now().hour
    return 6 <= hodina < 22


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
        raise Exception("Nepodařilo se najít data")

    bazen = int(bazen_match.group(1))
    aquapark = int(aquapark_match.group(1))
    obsazenost = int(obsazenost_match.group(1))
    celkem = bazen + aquapark

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(
        f"{timestamp},"
        f"{bazen},"
        f"{aquapark},"
        f"{celkem},"
        f"{obsazenost}"
    )

    browser.close()
