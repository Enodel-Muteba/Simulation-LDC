
import json
import random

TEAM_FILE = "teams.json"

class Team:
    def __init__(self, name, strength):
        self.name = name
        self.strength = strength

    def to_dict(self):
        return {"name": self.name, "strength": self.strength}

    @staticmethod
    def from_dict(data):
        return Team(data["name"], data["strength"])

def generate_teams():
    team_names = ['Real Madrid', 'Manchester City', 'Bayern Munich', 'Barcelona', 'Liverpool', 'Chelsea', 'Juventus', 'Paris Saint-Germain', 'Manchester United', 'Arsenal', 'AC Milan', 'Inter Milan', 'Atletico Madrid', 'Borussia Dortmund', 'RB Leipzig', 'Napoli', 'Ajax', 'Porto', 'Benfica', 'Sevilla', 'Roma', 'Lazio', 'Sporting CP', 'Galatasaray', 'Celtic', 'Rangers', 'Shakhtar Donetsk', 'Club Brugge', 'Red Bull Salzburg', 'Olympiacos', 'Fenerbahce', 'PSV Eindhoven']
    teams = [Team(name, random.randint(50, 100)) for name in team_names]
    save_teams(teams)

def save_teams(teams):
    with open(TEAM_FILE, "w") as f:
        json.dump([t.to_dict() for t in teams], f, indent=2)

def load_teams():
    with open(TEAM_FILE, "r") as f:
        data = json.load(f)
    return [Team.from_dict(d) for d in data]
