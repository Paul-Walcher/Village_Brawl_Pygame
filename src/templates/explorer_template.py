
"""
Template for any explorer.
"""
from abc import ABC, abstractmethod
from enum import Enum, auto

from deck import Deck

from templates.activatable import Activatable, ActivationResult, ActivationResultEnums

class ExplorerInfo:

    def __init__(self,
                name: str = "",
                name_color: tuple = (255, 255, 255),
                explorer_enum = None,
                description: str = "",
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
                starting_villagers: dict = None):

        #reference to the explorer enum
        self.explorer_enum = explorer_enum

        #name
        self.name = name
        #namecolor, shown in the selection screen
        self.name_color = (255, 255, 255)
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
        self.activation_phases = (ability_activation_phases if ability_activation_phases is not None else [])

    def copy(self):

        ecopy = ExplorerInfo()

        ecopy.name = self.name
        ecopy.name_color = self.name_color
        ecopy.description = self.description
        ecopy.card_image_path = self.card_image_path
        ecopy.standard_image_path = self.standard_image_path

        ecopy.starting_items = self.starting_items.copy()
        ecopy.starting_supporters = self.starting_supporters.copy()
        ecopy.starting_cards = self.starting_cards.copy()
        ecopy.starting_blueprints = self.starting_blueprints.copy()
        ecopy.starting_packs = self.starting_packs.copy()
        ecopy.unlocked_packs = self.unlocked_packs.copy()
        ecopy.unlockable_packs = self.unlockable_packs.copy()
        ecopy.starting_buildings = self.starting_buildings.copy()
        ecopy.starting_villagers = self.starting_villagers.copy()
        ecopy.lives = self.lives
        ecopy.inventory_size = self.inventory_size
        ecopy.activation_phases = self.activation_phases.copy()

        return ecopy


class Explorer_Template(Activatable):


    @staticmethod
    def info():
        return ExplorerInfo()



    def __init__(self, modules, einfo=None):

        #info
        self.info = (einfo if einfo is not None else Explorer_Template.info())
        self.modules = modules
        self.mappings = modules.mappings
        self.enums = modules.enums
        self.tags = modules.tags

        self.lives = 0 #current lives
        self.inventory_size = 0#inventory_size
        self.inventory = []#current inventory, includes item instances
        self.active_supporters = []#active supporter instances
        self.inactive_supporters = []#supporter instances that can be played, but are inactive.
        self.deck = Deck()#current deck
        self.deck_saves = {}#name: {enum: amount}
        self.trunk = {}#card enum: number of cards, total amount of cards possessed
        self.blueprints = []#blueprint: Blueprint instance
        self.packs = {} #enum: amount
        self.unlocked_packs = [] #list of enums
        self.unlockable_packs = [] #list of enums

        super().__init__(self.info.activation_phases)

    def load_instances(self):

        """
        loads the instances from the info, deletes all previous data
        """

        self.lives = self.info.lives
        self.max_inventory_size = self.info.inventory_size

        self.inventory = []
        for key, value in self.info.starting_items.items():
            self.inventory.extend([self.mappings.item_mappings[key]() for i in range(value)])

        self.active_supporters = []
        self.inactive_supporters = []
        for key, value in self.info.starting_supporters.items():
            self.inactive_supporters.extend([self.mappings.supporter_mappings[key]() for i in range(value)])

        self.trunk = self.info.starting_cards.copy()

        self.blueprints = []
        for key, value in self.info.starting_blueprints.items():
            self.blueprints.extend([self.mappings.blueprint_mappings[key]() for i in range(value)])

        self.packs = self.info.starting_packs.copy()
        self.unlocked_packs = self.info.unlocked_packs.copy()
        self.unlockable_packs = self.info.unlockable_packs.copy()

    def inventory_weight(self):
        return sum([item_.info.weight for item_ in self.inventory])

    def free_inventory_weight(self):
        return max(self.max_inventory_size - sum([item_.info.weight for item_ in self.inventory]), 0)


    def add_item(self, item_enum, amount=1):
        #adds an item into the inventory, if the inventory is big enough
        new_item_ref = self.mappings.item_mappings[item_enum]

        if new_item_ref.info().weight > self.free_inventory_weight():
            return False
        else:
            for i in range(amount):
                self.inventory.append(new_item_ref())
            return True
