from bridge_game.game.final_result import create_final_result
from bridge_game.players.player import Player
from bridge_game.players.team import Team


def test_final_team_scores_are_derived_from_individual_scores():
    north = Player(1, "North", "North")
    east = Player(2, "East", "East")
    south = Player(3, "South", "South")
    west = Player(4, "West", "West")
    players = [north, east, south, west]
    teams = [Team("NS", north, south), Team("EW", east, west)]

    for player, points in zip(players, [420, 390, 365, 330]):
        player.add_score(points)

    result = create_final_result(players, teams)

    assert result.individual_scores == {1: 420, 2: 390, 3: 365, 4: 330}
    assert result.team_scores == {teams[0]: 785, teams[1]: 720}
    assert result.winning_team is teams[0]
    assert all(not hasattr(team, "score") for team in teams)
