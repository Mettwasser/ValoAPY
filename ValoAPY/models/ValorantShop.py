from .BaseApiObject import BaseApiObject
from difflib import get_close_matches
import enum
from typing import Literal


class ValorantRiotPoints(enum.Enum):
    EU = {
        475: "5€",
        1000: "10€",
        2050: "20€",
        3650: "35€",
        5350: "50€",
        11000: "100€",
    }
    US = {
        475: "5$",
        1000: "10$",
        2050: "20$",
        3650: "35$",
        5350: "50$",
        11000: "100$",
    }
    EU_symbol = "€"
    US_symbol = "$"


class ValorantSkin:
    def __init__(
        self,
        name: str,
        price: int,
        skin_id: str = None,
        val_dict: Literal[
            ValorantRiotPoints.EU, ValorantRiotPoints.US
        ] = ValorantRiotPoints.EU,
    ):
        self.name = name
        self.price = price
        self.id = skin_id
        self.__val_dict = (
            val_dict.value if isinstance(val_dict, ValorantRiotPoints) else val_dict
        )
        if isinstance(self.__val_dict, ValorantRiotPoints):
            self.__symbol = (
                ValorantRiotPoints.EU_symbol.value
                if val_dict == ValorantRiotPoints.EU
                else ValorantRiotPoints.US_symbol.value
            )

    def __criterion(self, dict_items):
        key, value, price = dict_items
        return abs(key - price)

    def __get_price(self, price):
        items = [list(x) + [price] for x in self.__val_dict.items()]
        min_value = int(min(items, key=self.__criterion)[0])
        keys = list(self.__val_dict.keys())

        if price > min_value:
            if keys.index(min_value) == len(self.__val_dict.keys()) - 1:
                price -= min_value
                price_str = self.__get_price(price) + self.__val_dict[min_value]
                numlist = [
                    int(integer)
                    for integer in price_str.split(self.__symbol)
                    if integer.isdigit()
                ]
                return f"{sum(numlist)}{self.__symbol}"

            new_index = keys.index(min_value) + 1
            return self.__val_dict[keys[new_index]]

        return self.__val_dict[min_value]

    @property
    def rl_price(self):
        """Returns the price in real life currency (€/$)"""
        return self.__get_price(self.price)

    def __add__(self, other):
        if self.__val_dict != other.__val_dict:
            raise ValueError(
                f"Cannot add two skins from different regions: {self.name} and {other.name}"
            )
        if not isinstance(other, ValorantSkin):
            raise ValueError(f"Cannot add {type(other)} to a skin")
        return ValorantSkin(f"{self.name} + {other.name}", self.price + other.price)

    def __str__(self):
        return f"{self.name}: {self.price}rp (would need to charge {self.rl_price})"


class ValorantShop(BaseApiObject):
    def __init__(
        self,
        currency_region: Literal[
            ValorantRiotPoints.EU, ValorantRiotPoints.US
        ] = ValorantRiotPoints.EU,
    ) -> None:
        super().__init__()
        self.item_content = self._request("v1/content")
        self.sales = self._request("v1/store-offers")
        self.__val_dict = currency_region

    def skin_from_id(self, skin_id: str) -> ValorantSkin:
        skin_id = skin_id.lower()

        for sale in self.sales["data"]["Offers"]:
            if sale["OfferID"] == skin_id:
                for skin in self.item_content["skinLevels"]:
                    if skin["id"].lower() == skin_id:
                        name = skin["name"]
                        return ValorantSkin(
                            name,
                            list(sale["Cost"].values())[0],
                            skin_id=skin_id,
                            val_dict=self.__val_dict,
                        )

    def get_skin(self, name: str) -> ValorantSkin:
        item_names = [skin["name"] for skin in self.item_content["chromas"]]
        name = get_close_matches(name, item_names)[0]

        if not name:
            raise ValueError(f"No skin found with name {name}")

        for skin in self.item_content["skinLevels"]:

            if name == skin["name"]:
                skin_id = skin["id"].lower()

                for sale in self.sales["data"]["Offers"]:
                    if sale["OfferID"] == skin_id:
                        return ValorantSkin(
                            name,
                            list(sale["Cost"].values())[0],
                            skin_id=skin_id,
                            val_dict=self.__val_dict,
                        )

    def get_skins(self, names: list[str]) -> list[ValorantSkin]:
        return [self.get_skin(name) for name in names]
