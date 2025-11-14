import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# URL de base
base_url = "https://www.uaro.net/cp/?module=item&p="

# Mets ton cookie de session ici
cookies = { "fluxSessionData": "o7begn2tb36ss3qo8c3vbplhu7",
    "SID": "g.a0002ghv2giqukeirtbB5daC2maFgtAI3PFB3btkoomKZnZyJ-7wGQo_uGgiWiAjgwlach5wuwACgYKAW4SARESFQHGX2MiQ...",
    "SSID": "AK5I8Ss_tLNzZa_IP"}

all_items = []

for page in range(1, 430):  # 430 pages
    print(f"Récupération page {page}")
    try:
        r = requests.get(f"{base_url}{page}", cookies=cookies, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur page {page}: {e}")
        continue

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", class_="horizontal-table")
    if not table:
        print(f"Table non trouvée sur la page {page}")
        continue

    for row in table.find_all("tr")[1:]:  # ignorer l'en-tête
        cols = row.find_all("td")
        if not cols or len(cols) < 6:
            continue
        item_id = cols[0].text.strip()
        name = cols[2].text.strip()
        type_ = cols[3].text.strip()
        buy = cols[4].text.strip()
        sell = cols[5].text.strip()
        weight = cols[6].text.strip()
        attack = cols[7].text.strip()
        defense = cols[8].text.strip()
        slots = cols[9].text.strip()
        refineable = cols[10].text.strip()
        all_items.append({
            "ID": item_id,
            "Name": name,
            "Type": type_,
            "Buy": buy,
            "Sell": sell,
            "Weight": weight,
            "Attack": attack,
            "Defense": defense,
            "Slots": slots,
            "Refineable": refineable
        })

    time.sleep(0.3)  # pause courte pour ne pas surcharger le serveur

# Sauvegarde dans CSV
df = pd.DataFrame(all_items)
df.to_csv("items.csv", index=False, encoding="utf-8-sig")
print("Export terminé : items.csv")
