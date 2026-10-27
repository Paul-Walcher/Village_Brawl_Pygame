from enum import Enum, auto

class TypeEnums(Enum):
    """
    The different enums for the card types.
    """

    GENERAL_CARD = auto()
    GENERAL_SUPPORTER = auto()

    BIOME_CARD = auto()
    BIOME = auto()

    BLUEPRINT = auto()
    BOSS_CARD = auto()
    BOSS = auto()
    BUILDING = auto()
    EXPLORER_CARD = auto()
    EXPLORER = auto()
    ITEM = auto()
    MINIBOSS_CARD = auto()
    MINIBOSS = auto()
    OBJECTIVE = auto()
    PACK = auto()
    SCENARIO = auto()
    EXPLORER_SUPPORTER = auto()
    VILLAGE_SUPPORTER = auto()
    VILLAGE_BOSS_CARD = auto()
    VILLAGE_BOSS = auto()
    VILLAGE_CARD = auto()
    VILLAGE = auto()
    VILLAGER = auto()

class Locations(Enum):
    """
    Location enums, encode the current location of the explorer.
    """

    ANY = auto()

    VILLAGE = auto()
    OUTSIDE = auto() #any biome

    #example biomes
    PLAINS = auto()
