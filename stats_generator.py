import json
import random

import json
import json
import os
from datetime import datetime

def save_champion_history(current_champion):
    """
    Sauvegarde le champion actuel dans un fichier d'historique.
    """
    history_file = "historique_champions.json"

    # Charger l'historique existant s'il existe
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = {}

    # Générer un identifiant de saison (par exemple "Saison 2025")
    season = datetime.now().strftime("Saison %Y")

    # Ajouter ou mettre à jour le champion pour la saison
    history[season] = current_champion

    # Sauvegarder dans le fichier
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def generate_statistics(group_results, final_round):
    team_stats = {}

    # Statistiques de la phase de groupes
    for group in group_results.values():
        for t in group:
            name = t["team"].name
            if name not in team_stats:
                team_stats[name] = {"scored": 0, "conceded": 0}
            team_stats[name]["scored"] += t["scored"]
            team_stats[name]["conceded"] += t["conceded"]

    # Ajouter les infos du champion et finaliste
    champion = final_round[0].name  # final_round[0] est l'objet Team gagnant
    final_stats = {
        "champion": champion,
        "best_team": max(team_stats.items(), key=lambda x: x[1]["scored"] - x[1]["conceded"])[0],
        "top_scorer": None,  # À compléter si tu ajoutes un système de joueurs
        "top_player": None   # Idem
    }

    return {"teams": team_stats, "summary": final_stats}

def save_statistics(stats):
    with open("stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)



def save_statistics(stats, filename="stats.json"):
    with open(filename, "w") as f:
        json.dump(stats, f, indent=2)
