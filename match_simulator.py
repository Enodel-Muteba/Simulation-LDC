import random

def simulate_match(team1, team2):
    s1 = random.gauss(team1.strength, 10)
    s2 = random.gauss(team2.strength, 10)
    g1 = max(0, int(random.gauss(s1 / 25, 1)))
    g2 = max(0, int(random.gauss(s2 / 25, 1)))
    return g1, g2

def simulate_penalty():
    return random.choice([True, False])