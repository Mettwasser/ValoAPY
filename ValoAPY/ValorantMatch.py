from typing import Optional

from .BaseApiObject import BaseApiObject

from .ValorantPlayer import ValorantMatchPlayer


class ValorantMatchRound:
    def __init__(
        self,
        winning_team: str,
        bomb_planted: bool,
        bomb_defused: bool,
        planted_by: Optional[str],
        defused_by: Optional[str],
    ):
        self.winning_team = winning_team
        self.bomb_planted = bomb_planted
        self.bomb_defused = bomb_defused
        self.planted_by = planted_by
        self.defused_by = defused_by

    def __str__(self) -> str:
        defused_by = "No one" if self.defused_by is None else self.defused_by
        if self.planted_by is None:
            return f"Team {self.winning_team} won the round through killing the other team."
        return f"Team {self.winning_team} won the round. Spike planted by {self.planted_by} and got defused by {defused_by}"


class ValorantMatch(BaseApiObject):
    def __init__(self, match_json) -> None:
        super().__init__()
        self.match_json = match_json

    @property
    def players(self) -> list[ValorantMatchPlayer]:
        players = []
        for player in self.match_json["players"]["all_players"]:
            players.append(
                ValorantMatchPlayer(
                    puuid=player["puuid"],
                    name=player["name"],
                    tag=player["tag"],
                    region=self.match_json["metadata"]["region"],
                    team=player["team"],
                    account_level=player["level"],
                    character=player["character"],
                    kills=player["stats"]["kills"],
                    deaths=player["stats"]["deaths"],
                    assists=player["stats"]["assists"],
                    creds_spent=player["economy"]["spent"]["overall"],
                    damage_dealt=player["damage_made"],
                    damage_taken=player["damage_received"],
                )
            )
        return players

    @property
    def rounds(self) -> list[ValorantMatchRound]:
        rounds = []
        for round in self.match_json["rounds"]:
            rounds.append(
                ValorantMatchRound(
                    winning_team=round["winning_team"],
                    bomb_planted=round["bomb_planted"],
                    bomb_defused=round["bomb_defused"],
                    planted_by=round["plant_events"]["planted_by"][
                        "display_name"
                    ].split("#")[0]
                    if round["plant_events"]["planted_by"]
                    else None,
                    defused_by=round["defuse_events"]["defused_by"][
                        "display_name"
                    ].split("#")[0]
                    if round["defuse_events"]["defused_by"]
                    else None,
                )
            )
        return rounds

    @property
    def id(self) -> str:
        return self.match_json["metadata"]["matchid"]

    def __str__(self):
        return "Match"
