from enum import Enum


class SearchTypesEnum(str, Enum):
    ALL = "ALL"
    GROCERY = ("GROCERY",)
    ELECTRONICS = "ELECTRONICS"
    FNB = "FNB"
