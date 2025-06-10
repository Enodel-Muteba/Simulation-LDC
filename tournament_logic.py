import json
import random
from team_manager import Team
from match_simulator import simulate_match, simulate_penalty

def create_groups(teams):
    random.shuffle(teams)
    groups = {}
    for i in range(8):
        groups[chr(65+i)] = teams[i*4:(i+1)*4]
    return groups

def play_group_stage(groups):
    results = {}
    for group_name, teams in groups.items():
        standings = {team.name: {"points": 0, "scored": 0, "conceded": 0, "team": team} for team in teams}
        for i in range(len(teams)):
            for j in range(i+1, len(teams)):
                t1, t2 = teams[i], teams[j]
                g1, g2 = simulate_match(t1, t2)
                standings[t1.name]["scored"] += g1
                standings[t1.name]["conceded"] += g2
                standings[t2.name]["scored"] += g2
                standings[t2.name]["conceded"] += g1
                if g1 > g2:
                    standings[t1.name]["points"] += 3
                elif g2 > g1:
                    standings[t2.name]["points"] += 3
                else:
                    standings[t1.name]["points"] += 1
                    standings[t2.name]["points"] += 1
        sorted_teams = sorted(standings.values(), key=lambda x: (-x["points"], x["conceded"] - x["scored"]))
        results[group_name] = sorted_teams

    with open("group_stage_results.json", "w") as f:
        json.dump({g: [{"team": t["team"].name, "points": t["points"]} for t in res] for g, res in results.items()}, f, indent=2)

    # Sauvegarder qualifiés et éliminés pour affichage après
    qualified = []
    eliminated = []
    for group in results.values():
        qualified.append(group[0]["team"].name)
        qualified.append(group[1]["team"].name)
        for elim in group[2:]:
            eliminated.append(elim["team"].name)
    with open("group_stage_outcomes.json", "w") as f:
        json.dump({
            "qualified_from_groups": qualified,
            "eliminated_from_groups": eliminated
        }, f, indent=2)

    return results

def get_qualified_teams(group_results):
    qualified = []
    for group in group_results.values():
        qualified.append(group[0]["team"])
        qualified.append(group[1]["team"])
    return qualified

def draw_round_of_16(teams):
    random.shuffle(teams)
    return [(teams[i], teams[i+1]) for i in range(0, len(teams), 2)]

def display_qualified_teams(stage):
    """
    Affiche les équipes qualifiées et éliminées à chaque étape.
    stage: 'group', 'round_of_16', 'quarterfinals', 'semifinals', 'final'
    """
    if stage == 'group':
        try:
            with open("group_stage_outcomes.json", "r") as f:
                data = json.load(f)
            print("\n🏟️ Équipes qualifiées à l'issue de la phase de groupes :")
            for team in data.get("qualified_from_groups", []):
                print(f"  - {team}")
            print("\n❌ Équipes éliminées à l'issue de la phase de groupes :")
            for team in data.get("eliminated_from_groups", []):
                print(f"  - {team}")
        except FileNotFoundError:
            print("Fichier group_stage_outcomes.json introuvable.")
    else:
        try:
            with open("knockout_eliminations.json", "r") as f:
                elim_data = json.load(f)
            mapping = {
                'round_of_16': "Huitièmes de finale",
                'quarterfinals': "Quarts de finale",
                'semifinals': "Demi-finales",
                'final': "Finale"
            }
            stage_name = mapping.get(stage)
            if not stage_name:
                print(f"Étape inconnue : {stage}")
                return

            eliminated = elim_data.get(stage_name, [])
            print(f"\n❌ Équipes éliminées en {stage_name} :")
            for team in eliminated:
                print(f"  - {team}")

            # Affiche les qualifiés pour la prochaine étape sauf si finale
            if stage != 'final':
                with open("knockout_results.json", "r") as f:
                    results = json.load(f)
                stages_list = ['round_of_16', 'quarterfinals', 'semifinals', 'final']
                idx = stages_list.index(stage)
                if idx + 1 < len(results):
                    next_round_info = results[idx + 1]
                    print(f"\n🏟️ Équipes qualifiées pour {list(mapping.values())[idx+1]} :")
                    winners = set(m['winner'] for m in next_round_info)
                    for w in winners:
                        print(f"  - {w}")
        except FileNotFoundError:
            print("Aucune donnée d'élimination trouvée.")


def play_knockout_stage(matches, stage_name):
    """
    Joue une phase à élimination directe.
    stage_name: str, ex: "Huitièmes de finale", "Quarts de finale", "Demi-finales", "Finale"
    Retourne la liste des vainqueurs de cette phase.
    """
    winners = []
    eliminated = []
    round_info = []
    for t1, t2 in matches:
        g1, g2 = simulate_match(t1, t2)
        if g1 == g2:
            # Prolongation
            pg1, pg2 = simulate_match(t1, t2)
            g1 += pg1
            g2 += pg2
            if g1 == g2:
                # Tirs au but
                winner = t1 if simulate_penalty() else t2
                loser = t2 if winner == t1 else t1
                round_info.append({
                    "match": f"{t1.name} vs {t2.name}",
                    "score": f"{g1}-{g2} (ap + tab)",
                    "winner": winner.name,
                    "loser": loser.name
                })
            else:
                winner = t1 if g1 > g2 else t2
                loser = t2 if winner == t1 else t1
                round_info.append({
                    "match": f"{t1.name} vs {t2.name}",
                    "score": f"{g1}-{g2} (ap)",
                    "winner": winner.name,
                    "loser": loser.name
                })
        else:
            winner = t1 if g1 > g2 else t2
            loser = t2 if winner == t1 else t1
            round_info.append({
                "match": f"{t1.name} vs {t2.name}",
                "score": f"{g1}-{g2}",
                "winner": winner.name,
                "loser": loser.name
            })
        winners.append(winner)
        eliminated.append(loser.name)

    # Charger ou créer le fichier knockout_eliminations.json pour sauvegarder éliminés
    try:
        with open("knockout_eliminations.json", "r") as f:
            elim_data = json.load(f)
    except FileNotFoundError:
        elim_data = {}

    elim_data[stage_name] = eliminated
    with open("knockout_eliminations.json", "w") as f:
        json.dump(elim_data, f, indent=2)

    # Sauvegarder les résultats de la phase
    try:
        with open("knockout_results.json", "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        results = []

    results.append(round_info)
    with open("knockout_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return winners

def afficher_finale():
    try:
        with open("knockout_results.json", "r") as f:
            results = json.load(f)
        final_round = results[-1]
        if final_round:
            match = final_round[0]
            print("\n🏁 Finale :")
            print(f"  Match : {match['match']}")
            print(f"  Score : {match['score']}")
            print(f"  🏆 Vainqueur : {match['winner']}")
            print(f"  ❌ Perdant : {match['loser']}")
    except Exception as e:
        print(f"Erreur lors de l'affichage de la finale : {e}")


def play_knockout_stage(matches, stage_name):
    """
    Joue une phase à élimination directe.
    stage_name: str, ex: "Huitièmes de finale", "Quarts de finale", etc.
    Retourne la liste des vainqueurs de cette phase.
    """
    winners = []
    eliminated = []
    round_info = []

    print(f"\n🎯 {stage_name} - Résultats des matchs :")

    for t1, t2 in matches:
        g1, g2 = simulate_match(t1, t2)
        match_str = f"{t1.name} vs {t2.name}"
        display_score = f"{g1}-{g2}"

        if g1 == g2:
            # Prolongation
            pg1, pg2 = simulate_match(t1, t2)
            g1 += pg1
            g2 += pg2
            if g1 == g2:
                # Tirs au but
                winner = t1 if simulate_penalty() else t2
                loser = t2 if winner == t1 else t1
                display_score += f" → {pg1}-{pg2} (tab)"
            else:
                winner = t1 if g1 > g2 else t2
                loser = t2 if winner == t1 else t1
                display_score += f" → {pg1}-{pg2} (ap)"
        else:
            winner = t1 if g1 > g2 else t2
            loser = t2 if winner == t1 else t1

        print(f"🔹 {match_str} : {display_score} → 🏅 Gagnant : {winner.name}")

        round_info.append({
            "stage": stage_name,
            "match": match_str,
            "score": display_score,
            "winner": winner.name,
            "loser": loser.name
        })

        winners.append(winner)
        eliminated.append(loser.name)

    # 🔸 Sauvegarde des éliminés
    try:
        with open("knockout_eliminations.json", "r") as f:
            elim_data = json.load(f)
    except FileNotFoundError:
        elim_data = {}
    elim_data[stage_name] = eliminated
    with open("knockout_eliminations.json", "w") as f:
        json.dump(elim_data, f, indent=2)

    # 🔸 Sauvegarde des résultats de la phase
    try:
        with open("knockout_results.json", "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        results = []
    results.append(round_info)
    with open("knockout_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # 🔸 Sauvegarde des rencontres
    try:
        with open("knockout_matches.json", "r") as f:
            matches_data = json.load(f)
    except FileNotFoundError:
        matches_data = []
    matches_data.extend(round_info)
    with open("knockout_matches.json", "w") as f:
        json.dump(matches_data, f, indent=2)

    return winners

def get_final_loser():
    try:
        with open("knockout_results.json", "r") as f:
            results = json.load(f)
        final_round = results[-1]  # dernier round = finale
        if final_round:
            return final_round[0].get("loser")
    except (FileNotFoundError, IndexError, KeyError):
        return None

def get_champion():
    """
    Récupère et retourne l'équipe championne (vainqueur de la finale).
    """
    try:
        with open("knockout_results.json", "r") as f:
            results = json.load(f)
        final_round = results[-1]  # dernier round = finale
        if final_round:
            return final_round[0].get("winner")
    except (FileNotFoundError, IndexError, KeyError):
        return None
