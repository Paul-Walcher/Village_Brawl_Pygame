"""
Card definitions
"""
import os
import importlib
from enum import Enum, auto
import constants

from templates.explorer_card_template import Explorer_Card_Template, CardInfo
import constants
import deck

playset_path = os.path.dirname(os.path.abspath(__file__))
playset_name = os.path.basename(playset_path)
asset_path = os.path.join(playset_path, "assets")
standard_asset_path = os.path.join(asset_path, "standard_assets")
card_asset_path = os.path.join(asset_path, "card_assets")


enums = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.enums")
tags = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.tags")

Card_Tags = tags.Card_Tags

class Small_Rest(Explorer_Card_Template):

    @staticmethod
    def info():

        cinfo = CardInfo()

        cinfo.name = "Small Rest"
        cinfo.name_color = constants.Colors.WHITE

        cinfo.card_enum = enums.ExplorerCardEnums.SMALL_REST
        cinfo.description = "This card generates 1 Rest Token."
        cinfo.tags = [
                        Card_Tags.HEALING,
                        Card_Tags.HEALING_TOKEN,
                        Card_Tags.HEALING_TOKEN_GENERATOR
                    ]

        cinfo.standard_selling_reward = []

        cinfo.card_image_path = os.path.join(card_asset_path, "Small_Rest_Card.png")
        cinfo.standard_image_path = os.path.join(standard_asset_path, "Small_Rest.png")

        cinfo.max_per_deck = 40
        cinfo.activation_phases = []

        return cinfo


    def __init__(self, modules):

        super().__init__(modules, Small_Rest.info())



    def activate(self, phaseinfo):
        pass
