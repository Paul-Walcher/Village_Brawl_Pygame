from constants import R_ID, id_t

class TypeEnums:
    """
    The different enums for the card types.
    """

    GENERAL_CARD: id_t = R_ID()
    GENERAL_SUPPORTER: id_t = R_ID()

    BIOME_CARD: id_t = R_ID()
    BIOME: id_t = R_ID()

    BLUEPRINT: id_t = R_ID()
    BOSS_CARD: id_t = R_ID()
    BOSS: id_t = R_ID()
    BUILDING: id_t = R_ID()
    EXPLORER_CARD: id_t = R_ID()
    EXPLORER: id_t = R_ID()
    ITEM: id_t = R_ID()
    MINIBOSS_CARD: id_t = R_ID()
    MINIBOSS: id_t = R_ID()
    OBJECTIVE: id_t = R_ID()
    PACK: id_t = R_ID()
    SCENARIO: id_t = R_ID()
    EXPLORER_SUPPORTER: id_t = R_ID()
    VILLAGE_SUPPORTER: id_t = R_ID()
    VILLAGE_BOSS_CARD: id_t = R_ID()
    VILLAGE_BOSS: id_t = R_ID()
    VILLAGE_CARD: id_t = R_ID()
    VILLAGE: id_t = R_ID()
    VILLAGER: id_t = R_ID()

class Locations:
    """
    Location enums, encode the current location of the explorer.
    """

    ANY = R_ID()

    VILLAGE = R_ID()
    OUTSIDE = R_ID() #any biome

    #example biomes
    PLAINS = R_ID()

type card_enum_t = id_t
type type_enum_t = id_t
type identifier_t = tuple[type_enum_t, card_enum_t]
