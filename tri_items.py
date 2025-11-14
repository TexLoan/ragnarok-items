import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Charger le CSV
df = pd.read_csv("items.csv")

# Fonction pour réattribuer un type selon le nom (UARO Pre-Renewal)
def refine_armor_type(row):
    if row['Type'].lower() != "armor":
        return row['Type']  # ne rien changer si ce n'est pas une armure
    
    name = row['Name'].lower()
    
    if any(keyword in name for keyword in ["helmet", "cap", "hat", "hood", "headgear", "circlet", "mask", "tiara"]):
        return "Helmet"
    elif any(keyword in name for keyword in ["armor", "robe", "plate", "coat", "mail", "tunic", "jerkin", "dress", "vest"]):
        return "Body Armor"
    elif any(keyword in name for keyword in ["boots", "shoe", "greaves", "sandal", "knee guard", "leg"]):
        return "Boots"
    elif any(keyword in name for keyword in ["glove", "gauntlet", "mitt", "hand", "wrist guard"]):
        return "Gloves"
    elif any(keyword in name for keyword in ["shield", "buckler", "kiteshield", "tower shield", "small shield"]):
        return "Shield"
    elif any(keyword.lower() in name for keyword in ["costume", "costume:"]):
        return "Costume"
    elif any(keyword.lower() in name for keyword in [
        "ring", "necklace", "amulet", "earring", "bracelet", "belt", "cape", "cloak", "brooch", "medal", "talisman"]):
        return "Accessory"
    else:
        return "Other Armor"

# Appliquer la fonction sur toutes les lignes
df['Type'] = df.apply(refine_armor_type, axis=1)

# Fonction pour récupérer le type réel depuis le site
def get_item_type(item_id):
    url = f"https://db.irowiki.org/db/item-info/{item_id}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Erreur pour l'ID {item_id}: {response.status_code}")
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        type_td = soup.find("td", class_="infoTitle", string="Subtype")
        if type_td:
            type_value_td = type_td.find_next_sibling("td", class_="infoText")
            if type_value_td:
                return type_value_td.text.strip()
    except Exception as e:
        print(f"Exception pour l'ID {item_id}: {e}")
    return None

# Filtrer les items encore en Other Armor
other_armor_df = df[df['Type'] == "Other Armor"]

# Pour chaque item, essayer de récupérer le type réel
for index, row in other_armor_df.iterrows():
    real_type = get_item_type(row['ID'])
    if real_type:
        df.at[index, 'Type'] = real_type
        print(f"ID {row['ID']}: Other Armor -> {real_type}")

# Sauvegarder le CSV des items encore inconnus (si certains restent)
remaining_other_armor_df = df[df['Type'] == "Other Armor"]
remaining_other_armor_df.to_csv("items_other_armor.csv", index=False, encoding="utf-8-sig")

# Sauvegarder le CSV final
df.to_csv("items_refined.csv", index=False, encoding="utf-8-sig")
print("Fichier sauvegardé sous items_refined.csv avec les types d'armures affinés.")
