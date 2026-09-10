from dataclasses import dataclass

from bridge_game.game.bidding_result import BiddingResult
from bridge_game.players.team import Team


@dataclass(frozen=True)
class ContractAssignment:
    bidding_team: Team
    opposing_team: Team
    bidding_team_target: int
    opposing_team_target: int


def assign_contract_to_teams(
    result: BiddingResult,
    players,
    teams,
) -> ContractAssignment:
    if not result.has_contract:
        raise ValueError("Cannot assign teams without a bidding contract")

    if len(teams) != 2:
        raise ValueError("Contract assignment requires exactly 2 teams")

    matching_players = [
        player for player in players
        if player.player_id == result.bidder_id
    ]
    if len(matching_players) != 1:
        raise ValueError("Bidder ID must match exactly one game player")

    bidder = matching_players[0]
    bidding_teams = [
        team
        for team in teams
        if team.player1 is bidder or team.player2 is bidder
    ]
    if len(bidding_teams) != 1:
        raise ValueError("Bidder must belong to exactly one game team")

    bidding_team = bidding_teams[0]
    opposing_team = teams[1] if teams[0] is bidding_team else teams[0]

    return ContractAssignment(
        bidding_team=bidding_team,
        opposing_team=opposing_team,
        bidding_team_target=result.bidder_target,
        opposing_team_target=result.opponent_target,
    )
