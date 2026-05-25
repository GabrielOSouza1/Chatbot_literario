import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from web_scraper import scrape_page

SOURCES = {
    "Mistborn": [
        "https://mistborn.fandom.com/wiki/Mistborn_Wiki",
        "https://mistborn.fandom.com/wiki/Vin",
        "https://mistborn.fandom.com/wiki/Kelsier",
        "https://mistborn.fandom.com/wiki/Allomancy",
        "https://mistborn.fandom.com/wiki/The_Final_Empire",
        "https://mistborn.fandom.com/wiki/Sazed",
        "https://coppermind.net/wiki/Mistborn_(series)",
        "https://coppermind.net/wiki/Kelsier",
        "https://coppermind.net/wiki/Vin",
    ],
    "O Caminho dos Reis": [
        "https://stormlightarchive.fandom.com/wiki/The_Stormlight_Archive_Wiki",
        "https://stormlightarchive.fandom.com/wiki/Kaladin",
        "https://stormlightarchive.fandom.com/wiki/Shallan_Davar",
        "https://stormlightarchive.fandom.com/wiki/Dalinar_Kholin",
        "https://stormlightarchive.fandom.com/wiki/Stormlight",
        "https://coppermind.net/wiki/The_Way_of_Kings",
        "https://coppermind.net/wiki/Kaladin",
    ],
    "O Nome do Vento": [
        "https://kingkiller.fandom.com/wiki/Kvothe",
        "https://kingkiller.fandom.com/wiki/The_Name_of_the_Wind",
        "https://kingkiller.fandom.com/wiki/Sympathy",
        "https://kingkiller.fandom.com/wiki/Denna",
        "https://kingkiller.fandom.com/wiki/University",
    ],
    "A Guerra dos Tronos": [
        "https://awoiaf.westeros.org/index.php/A_Game_of_Thrones",
        "https://awoiaf.westeros.org/index.php/Jon_Snow",
        "https://awoiaf.westeros.org/index.php/Daenerys_Targaryen",
        "https://awoiaf.westeros.org/index.php/Tyrion_Lannister",
        "https://gameofthrones.fandom.com/wiki/Jon_Snow",
        "https://gameofthrones.fandom.com/wiki/Daenerys_Targaryen",
    ],
    "Star Wars": [
        "https://starwars.fandom.com/wiki/Star_Wars",
        "https://starwars.fandom.com/wiki/Luke_Skywalker",
        "https://starwars.fandom.com/wiki/Darth_Vader",
        "https://starwars.fandom.com/wiki/The_Force",
        "https://starwars.fandom.com/wiki/Yoda",
        "https://starwars.fandom.com/wiki/Obi-Wan_Kenobi",
    ],
    "Fundação": [
        "https://foundation.fandom.com/wiki/Foundation_Wiki",
        "https://foundation.fandom.com/wiki/Hari_Seldon",
        "https://foundation.fandom.com/wiki/Psychohistory",
        "https://foundation.fandom.com/wiki/The_Foundation",
    ],
    "O Senhor dos Anéis": [
        "https://lotr.fandom.com/wiki/The_Lord_of_the_Rings",
        "https://lotr.fandom.com/wiki/Frodo_Baggins",
        "https://lotr.fandom.com/wiki/Gandalf",
        "https://lotr.fandom.com/wiki/Aragorn",
        "https://lotr.fandom.com/wiki/The_One_Ring",
        "https://lotr.fandom.com/wiki/Sauron",
    ],
}

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge_base_pt.json")
DELAY_ENTRE_URLS = 1.5


def build():
    kb = {}
    total = 0

    for topic, urls in SOURCES.items():
        print(f"\n📚 Minerando: {topic}")
        for url in urls:
            if not url:
                continue
            print(f"  🔗 {url}")
            try:
                blocks = scrape_page(url, topic)
                for block in blocks:
                    intent = block.get("intent", "curiosidades")
                    kb.setdefault(intent, []).append(block)
                    total += 1
                print(f"     ✅ {len(blocks)} blocos coletados")
            except Exception as e:
                print(f"     ❌ Erro: {e}")
            time.sleep(DELAY_ENTRE_URLS)

    output_path = os.path.abspath(OUTPUT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Base salva em '{output_path}' com {total} blocos no total.")
    for intent, items in kb.items():
        print(f"   {intent}: {len(items)} entradas")


if __name__ == "__main__":
    build()