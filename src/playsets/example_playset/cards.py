"""
Card definitions
"""
import os
import importlib
from enum import Enum, auto
import constants

from templates.card_template import Card_Template, CardInfo
import terminal_functions as terminal
import constants
import deck

playset_path = os.path.dirname(os.path.abspath(__file__))
playset_name = os.path.basename(playset_path)
asset_path = os.path.join(playset_path, "assets")
standard_asset_path = os.path.join(asset_path, "standard_assets")
card_asset_path = os.path.join(asset_path, "card_assets")


enums = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.enums")


class CardTag:

    HEALING = "Healing"

    HEALING_TOKEN_GENERATOR = "Healing Token Generator"
    HEALING_TOKEN_CONSUMER = "Healing Token Consumer"
    HEALING_TOKEN = "Healing Token"

class Small_Rest(Card_Template):

    def __init__(self):

        super().__init__()

        self.name = "Small Rest"
        self.name_color = constants.Colors.WHITE

        self.card_enum = enums.CardEnums.SMALL_REST
        self.description = "This card generates 1 Rest Token."
        self.card_enum = enums.CardEnums.SMALL_REST
        self.tags = [
                        CardTag.HEALING,
                        CardTag.HEALING_TOKEN,
                        CardTag.HEALING_TOKEN_GENERATOR
                    ]
        self.standard_selling_reward = {}

        self.card_image_path = os.path.join(card_asset_path, "Small_Rest_Card.png")
        self.standard_image_path = os.path.join(standard_asset_path, "Small_Rest.png")

        self.max_per_deck = 40
        self.activation_phases = []


    def activate(self, context, cardinfo, phase, location):
        pass

    def info(self, context):

        mappings = context.modules.mappings_module

        cinfo = CardInfo()
        cinfo.card_enum = self.card_enum

        return cinfo
