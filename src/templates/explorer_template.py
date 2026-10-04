
"""
Template for any explorer.
"""
from abc import ABC, abstractmethod
from enum import Enum, auto

class ExplorerInfo:

    def __init__(self):

        #reference to the explorer enum
        self.explorer_enum = None

        self.lives = 0 #current lives
        self.inventory = []#current inventory, includes items
        self.inventory_max_size = 0
        self.active_supporters = []#active supporters
        self.inactive_supporters = []#supporters that can be played, but are inactive
        self.deck = None#current deck
        self.deck_saves = {}#name: list of cards
        self.trunk = {}#card enum: number of cards, total amount of cards possessed
        self.blueprints = []#blueprint: Blueprint_Info
        self.packs = []#list of packinfo
        self.unlocked_packs = []#list of enums
        self.unlockable_packs = []# PackUnlockInfo

    def copy(self):

        ecopy = ExplorerInfo()

        ecopy.explorer_enum = self.explorer_enum
        ecopy.lives = self.lives
        ecopy.inventory = self.inventory.copy()
        ecopy.inventory_max_size = self.inventory_max_size
        ecopy.active_supporters = self.active_supporters.copy()
        ecopy.inactive_supporters = self.inactive_supporters.copy()
        ecopy.deck = self.deck.copy()
        ecopy.trunk = self.trunk.copy()
        ecopy.blueprints = self.blueprints.copy()
        ecopy.packs = self.packs.copy()
        ecopy.unlocked_packs = self.unlocked_packs.copy()
        ecopy.unlockable_packs = self.unlockable_packs.copy()

        return ecopy


class Explorer_Template(ABC):
    def __init__(self,  name: str = "",
                        name_color: tuple = (255, 255, 255),
                        explorer_enum = None,
                        description: str = "",
                        ability_name: str = "",
                        card_image_path: str = "",
                        standard_image_path: str = "",
                        lives: int = 5,
                        ability_activation_phases = None,
                        inventory_size: float = 10.0,
                        starting_items: dict = None,
                        starting_supporters: dict = None,
                        starting_cards: dict = None,
                        starting_blueprints: dict = None,
                        starting_packs: dict = None,
                        unlocked_packs: dict = None,
                        unlockable_packs: dict = None,
                        starting_buildings: dict = None,
                        starting_villagers: dict = None
                        ):

        #name
        self.name = name
        #namecolor, shown in the selection screen
        self.name_color = (255, 255, 255)
        #the name enum
        self.explorer_enum = explorer_enum
        #description
        self.description = description
        #card image path
        self.card_image_path = card_image_path
        #standard image path
        self.standard_image_path = standard_image_path
        #starting items. these need to be the enums from items_mappings.
        #starting items are {name_enum: amount}
        self.starting_items = (starting_items if starting_items is not None else {})
        #starting supporters.
        #starting supporters are: {name_enum, amount}
        self.starting_supporters = (starting_supporters if starting_supporters is not None else {})
        #starting cards
        #{card_enum: amount}
        self.starting_cards = (starting_cards if starting_cards is not None else {})
        #blueprints, {card_enum: amount}
        self.starting_blueprints = (starting_blueprints if starting_blueprints is not None else {})
        #starting_packs
        #starting packs. these need to be the enums from pack_mappings
        #starting packs are {name_enum: amount}
        self.starting_packs = (starting_packs if starting_packs is not None else {})
        #unlocked packs
        self.unlocked_packs = (unlocked_packs if unlocked_packs is not None else [])
        #unlockable_packs
        self.unlockable_packs = (unlockable_packs if unlockable_packs is not None else [])
        #buildings
        self.starting_buildings = (starting_buildings if starting_buildings is not None else {})
        #villagers
        self.starting_villagers = (starting_villagers if starting_villagers is not None else {})
        #stats
        #lives
        self.lives = lives
        #inventory size
        self.inventory_size = inventory_size
        #ability_activation_phases
        self.ability_activation_phases = (ability_activation_phases if ability_activation_phases is not None else [])

    @abstractmethod
    def activate_ability(self, context, explorer_info, phase):
        pass


    @abstractmethod
    def info(self, context):
        """
        returns the explorer info
        """
        pass
