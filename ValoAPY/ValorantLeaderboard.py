from typing import Literal
from .BaseApiObject import BaseApiObject
from .ValorantPlayer import ValorantPlayer


class ValorantLeaderboard(BaseApiObject):
    def __init__(self, region: Literal["eu", "na", "ap", "kr"] = "eu", data=None):
        super().__init__()
        self.region = region
        self._data = data

    @property
    def data(self):
        if not self._data:
            self._data = self._request(f"v1/leaderboard/{self.region}")
        return self._data

    @classmethod
    def from_data(cls, data: dict, region):
        return cls(region, data)

    @property
    def top10(self):
        return self.players[:10]

    @property
    def players(self) -> list[ValorantPlayer]:
        players = []
        for player in self.data:
            players.append(
                ValorantPlayer(
                    player["puuid"],
                    player["gameName"],
                    player["tagLine"],
                )
            )
        return players

    def get_avg_ranked_rating(self, range_of_players: int = 1000) -> int:
        if range_of_players > 1000:
            raise ValueError("range_of_players can't exceed 1000")
        avg_ranked_rating = 0
        for player in self.data[:range_of_players]:
            avg_ranked_rating += player["rankedRating"]
        return avg_ranked_rating / range_of_players

    def __str__(self):
        return "\n".join([f"{k}: {v}" for k, v in enumerate(self.top10)])
