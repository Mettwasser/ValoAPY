from typing import Union, Literal
from .BaseApiObject import BaseApiObject


class ValorantPlayer(BaseApiObject):
    def __init__(
        self,
        puuid: str,
        name: str,
        tag: int,
        region: Literal["eu", "na", "ap", "kr"] = "eu",
    ):
        super().__init__()
        self._puuid = puuid
        self.name = name
        self.tag = tag
        self.region = region

    @classmethod
    def from_name(
        cls, name_and_tag: str, region: Literal["eu", "na", "ap", "kr"] = "eu"
    ) -> "ValorantMatchPlayer":
        name, tag = name_and_tag.split("#")
        return cls(None, name, tag, region)

    @classmethod
    def find_player(
        cls, iterable: list["ValorantPlayer"], name: str
    ) -> Union["ValorantPlayer", "ValorantMatchPlayer"]:
        """Searches and returns a ValorantPlayer (or every other child of it) object of the given player name."""
        for player in iterable:
            if player.name == name:
                return player

    @property
    def puuid(self):
        if not self._puuid:
            self._puuid = self._request(f"v1/account/{self.name}/{self.tag}")["data"][
                "puuid"
            ]

        return self._puuid

    @property
    def current_rank(self):
        j = self._request(f"v2/by-puuid/mmr/{self.region}/{self.puuid}")
        return j["data"]["current_data"]["currenttierpatched"]

    @property
    def elo(self):
        j = self._request(f"v2/by-puuid/mmr/{self.region}/{self.puuid}")
        return j["data"]["current_data"]["elo"]

    @property
    def last_match(self):
        return self.last_matches[0]

    @property
    def last_matches(self):
        from .ValorantMatch import ValorantMatch

        j = self._request(f"v3/by-puuid/matches/{self.region}/{self.puuid}")
        return [ValorantMatch(match_data) for match_data in j["data"]]

    def __str__(self):
        return f"[{self.region}] {self.name}#{self.tag} ({self.puuid})"


class ValorantMatchPlayer(ValorantPlayer):
    def __init__(
        self,
        puuid: str,
        name: str,
        tag: int,
        region: Literal["eu", "na", "ap", "kr"],
        team: str,
        account_level: int,
        character: str,
        kills: int,
        deaths: int,
        assists: int,
        creds_spent: int,
        damage_dealt: int,
        damage_taken: int,
    ):
        super().__init__(puuid, name, tag, region)
        self.team = team
        self.account_level = account_level
        self.character = character
        self.kills = kills
        self.deaths = deaths
        self.kda = round(kills / deaths, 2)
        self.assists = assists
        self.creds_spent = creds_spent
        self.damage_dealt = damage_dealt
        self.damage_taken = damage_taken

    def to_player(self) -> "ValorantPlayer":
        """Returns a ValorantPlayer object."""
        return ValorantPlayer(self.puuid, self.name, self.tag, self.region)
