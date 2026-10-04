"""
Explorer definitions
"""
import os
import importlib
from enum import Enum, auto
import constants
from constants import Colors

from templates.explorer_template import Explorer_Template, ExplorerInfo
import terminal_functions as terminal
import constants
from deck import Deck

playset_path = os.path.dirname(os.path.abspath(__file__))
playset_name = os.path.basename(playset_path)
asset_path = os.path.join(playset_path, "assets")
standard_asset_path = os.path.join(asset_path, "standard_assets")
card_asset_path = os.path.join(asset_path, "card_assets")


enums = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.enums")


class Basic_Explorer(Explorer_Template):

    @staticmethod
    def info():

        einfo = ExplorerInfo()
        einfo.name = "Basic Explorer"
        einfo.name_color = Colors.LIGHT_ORANGE
        einfo.explorer_enum = enums.ExplorerEnums.BASIC_EXPLORER
        einfo.description = "Basic Explorer. Has no special abilities."

        einfo.card_image_path = os.path.join(card_asset_path, "Basic_Explorer_Card.png")
        einfo.standard_image_path = os.path.join(standard_asset_path, "Basic_Explorer_Standard.png")

        einfo.lives = 10
        einfo.inventory_size = 10.0

        einfo.starting_items = {}
        einfo.starting_supporters = {}
        einfo.starting_cards = {}#{enums.CardEnums.SMALL_REST: 20}
        einfo.starting_blueprints = {}
        einfo.starting_packs = {}
        einfo.unlocked_packs = {}
        einfo.unlockable_packs = {}

        einfo.starting_buildings = {}
        einfo.starting_villagers = {}
        einfo.activation_phases = []

        return einfo

    def __init__(self, modules):

        super().__init__(modules, Basic_Explorer.info())
        self.load_instances()


    def activate_ability(self, phaseinfo):
        pass
