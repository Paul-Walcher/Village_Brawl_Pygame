"""
Explorer definitions
"""
import os
import importlib
from enum import Enum, auto
import constants

from templates.explorer_template import Explorer_Template, ExplorerInfo
import terminal_functions as terminal
import constants
import deck

playset_path = os.path.dirname(os.path.abspath(__file__))
playset_name = os.path.basename(playset_path)
asset_path = os.path.join(playset_path, "assets")
standard_asset_path = os.path.join(asset_path, "standard_assets")
card_asset_path = os.path.join(asset_path, "card_assets")


enums = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.enums")


class Basic_Explorer(Explorer_Template):

    def __init__(self):

        super().__init__()

        self.name = "Basic Explorer"
        self.name_color = (255, 144, 0)
        self.explorer_enum = enums.ExplorerEnums.BASIC_EXPLORER
        self.description = terminal.text_rgb_string(0, 204, 0) + "Basic Explorer. Has no special abilities." + terminal.color_reset_string()

        self.ability_name = "-"
        self.ability_activation_phases = []

        self.card_image_path = os.path.join(card_asset_path, "Basic_Explorer_Card.png")
        self.standard_image_path = os.path.join(standard_asset_path, "Basic_Explorer_Standard.png")

        self.lives = 10
        self.inventory_size = 10.0

        self.starting_items = {}
        self.starting_supporters = {}
        self.starting_cards = {enums.CardEnums.SMALL_REST: 20}
        self.starting_blueprints = {}
        self.starting_packs = {}
        self.unlocked_packs = {}
        self.unlockable_packs = {}

        self.starting_buildings = {}
        self.starting_villagers = {}

    def info(self, context):

        mappings = context.modules.mappings_module

        einfo = ExplorerInfo()

        einfo.explorer_enum = self.explorer_enum

        einfo.lives = self.lives
        einfo.inventory = []
        #for item_ in self.starting_items:
        #   for i in range(self.starting_items[item_]):
        #       einfo.inventory.append(item_module.items_mappings[item_].info())
        einfo.inventory_max_size = self.inventory_size
        #active supporters
        einfo.inactive_supporters = []
        #for supporter in self.starting_supporters:
        #   for i in range(self.starting_supporters[supporter]):
        #       einfo.inactive_supporters.append(supporter_module.supporter_mappings[supporter].info())
        einfo.inactive_supporters = {}
        einfo.deck = deck.Deck()
        einfo.deck_saves = {}

        einfo.trunk = self.starting_cards.copy()
        #blueprints
        einfo.blueprints = []
        #for blueprint in self.starting_blueprints:
        #   for i in range(self.starting_blueprints[blueprint]):
        #       einfo.blueprints.append(blueprint_module.blueprint_mappings[blueprint].info())

        #packs
        einfo.packs = []
        #for pack in self.starting_packs:
        #   for i in range(self.starting_packs[pack]):
        #       einfo.packs.append(pack_module.pack_mappings[pack].info())

        #unlocked packs
        einfo.unlocked_packs = self.unlocked_packs.copy()

        #unlockable packs
        einfo.unlocked_packs = self.unlockable_packs.copy()

        return einfo


    def activate_ability(self, context, explorer_info, phase):
        pass
