from bridge_game.players.player import Player
from bridge_game.players.team import Team


def test_team_creation():
    player1 = Player(1, "Alice", "North")
    player2 = Player(3, "Charlie", "South")

    team = Team("Team A", player1, player2)

    assert team.name == "Team A"
    assert team.player1 == player1
    assert team.player2 == player2


def test_team_contains_players():
    player1 = Player(1, "Alice", "North")
    player2 = Player(3, "Charlie", "South")
    player3 = Player(2, "Bob", "East")

    team = Team("Team A", player1, player2)

    assert player1 in team
    assert player2 in team
    assert player3 not in team