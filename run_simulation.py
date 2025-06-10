from team_manager import generate_teams, load_teams
from tournament_logic import (
    create_groups, play_group_stage, get_qualified_teams,
    draw_round_of_16, play_knockout_stage,
    display_qualified_teams, afficher_finale,
    get_champion, get_final_loser
)
from stats_generator import generate_statistics, save_statistics
from stats_generator import generate_statistics, save_statistics, save_champion_history

def ask_to_continue(stage_name):
    while True:
        answer = input(f"\nVoulez-vous lancer la phase des {stage_name} ? (o/n) : ").strip().lower()
        if answer in ("o", "n"):
            return answer == "o"
        print("Réponse invalide, tapez 'o' pour oui ou 'n' pour non.")

def run_full_simulation():
    print("🔁 Génération des équipes...")
    generate_teams()
    teams = load_teams()

    print("\n🎲 Création des groupes...")
    groups = create_groups(teams)

    print("\n⚽ Phase de groupes...")
    group_results = play_group_stage(groups)

    print("\n✅ Qualification...")
    qualified = get_qualified_teams(group_results)
    display_qualified_teams('group')

    # Huitièmes de finale
    if ask_to_continue("huitièmes de finale"):
        round_of_16 = draw_round_of_16(qualified)
        winners_16 = play_knockout_stage(round_of_16, "Huitièmes de finale")
        display_qualified_teams('round_of_16')
    else:
        print("Simulation arrêtée après la phase de groupes.")
        return

    # Quarts de finale
    if ask_to_continue("quarts de finale"):
        quarters = [(winners_16[i], winners_16[i+1]) for i in range(0, len(winners_16), 2)]
        winners_quarters = play_knockout_stage(quarters, "Quarts de finale")
        display_qualified_teams('quarterfinals')
    else:
        print("Simulation arrêtée après les huitièmes de finale.")
        return

    # Demi-finales
    if ask_to_continue("demi-finales"):
        semis = [(winners_quarters[i], winners_quarters[i+1]) for i in range(0, len(winners_quarters), 2)]
        winners_semis = play_knockout_stage(semis, "Demi-finales")
        display_qualified_teams('semifinals')
    else:
        print("Simulation arrêtée après les quarts de finale.")
        return

    # Finale
    if ask_to_continue("finale"):
        final = [(winners_semis[0], winners_semis[1])]
        winners_final = play_knockout_stage(final, "Finale")
        display_qualified_teams('final')

        champion = get_champion()
        final_loser = get_final_loser()


        print(f"\n🏆 Le champion de la compétition est : {champion}")
        print(f"🥈 L'équipe finaliste (perdante) est : {final_loser}")
        champion = get_champion()
        final_loser = get_final_loser()
        print(f"\n🏆 Le champion de la compétition est : {champion}")
        print(f"🥈 L'équipe finaliste (perdante) est : {final_loser}")

        # Sauvegarder l'historique de la saison
        save_champion_history(champion)

        print("\n📊 Génération des statistiques...")
        stats = generate_statistics(group_results, winners_final)
        save_statistics(stats)
        print("📁 Statistiques sauvegardées dans 'stats.json'.")

        print("\n✅ Simulation terminée.")
    else:
        print("Simulation arrêtée après les demi-finales.")

if __name__ == "__main__":
    run_full_simulation()
    afficher_finale()
