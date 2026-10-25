"""
Card definitions
"""
import os
import importlib
from enum import Enum, auto
import constants

from templates.explorer_card_template import Explorer_Card_Template, ExplorerCardInfo
from templates.type_enums import TypeEnums
from constants import Colors, INFINITE
import deck


from Frames.frame_enums import FrameEnums

playset_path = os.path.dirname(os.path.abspath(__file__))
playset_name = os.path.basename(playset_path)
asset_path = os.path.join(playset_path, "assets")
standard_asset_path = os.path.join(asset_path, "standard_assets")
card_asset_path = os.path.join(asset_path, "card_assets")


enums = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.enums")
tags = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.tags")

#Example cards
class Example_Card_1(Explorer_Card_Template):

    @staticmethod
    def info():

        cinfo = ExplorerCardInfo(
                        name = "Example Card 1",
                        name_color = Colors.WHITE,
                        card_enum = enums.ExplorerCardEnums.EXAMPLE_CARD_1,
                        description = "Example Card",
                        description_color = [("Example Card", Colors.STANDARD_TEXT_COLOR)],
                        tags = [],
                        standard_selling_reward = {},
                        card_image_path  = os.path.join(card_asset_path, "Example_Card_1.png"),
                        standard_image_path = os.path.join(card_asset_path, "Example_Card_1.png"),
                        max_per_deck = INFINITE,
                        activation_phases = [],
                        keep_duration = 0
        )

        return cinfo

    def __init__(self, modules, entity_type=TypeEnums.EXPLORER_CARD, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):
        super().__init__(modules, entity_type, Example_Card_1.info(), frame_enum, data, frame_dim, parent_frame)

class Example_Card_2(Explorer_Card_Template):

    @staticmethod
    def info():

        cinfo = ExplorerCardInfo(
                        name = "Example Card 2",
                        name_color = Colors.WHITE,
                        card_enum = enums.ExplorerCardEnums.EXAMPLE_CARD_2,
                        description = "Example Card",
                        description_color = [("Example Card", Colors.STANDARD_TEXT_COLOR)],
                        tags = [],
                        standard_selling_reward = {},
                        card_image_path  = os.path.join(card_asset_path, "Example_Card_2.png"),
                        standard_image_path = os.path.join(card_asset_path, "Example_Card_2.png"),
                        max_per_deck = INFINITE,
                        activation_phases = [],
                        keep_duration = 0
        )

        return cinfo

    def __init__(self, modules, entity_type=TypeEnums.EXPLORER_CARD, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):
        super().__init__(modules, entity_type, Example_Card_2.info(), frame_enum, data, frame_dim, parent_frame)

class Example_Card_3(Explorer_Card_Template):

    @staticmethod
    def info():

        cinfo = ExplorerCardInfo(
                        name = "Example Card 3",
                        name_color = Colors.WHITE,
                        card_enum = enums.ExplorerCardEnums.EXAMPLE_CARD_3,
                        description = "Example Card",
                        description_color = [("Example Card", Colors.STANDARD_TEXT_COLOR)],
                        tags = [],
                        standard_selling_reward = {},
                        card_image_path  = os.path.join(card_asset_path, "Example_Card_3.png"),
                        standard_image_path = os.path.join(card_asset_path, "Example_Card_3.png"),
                        max_per_deck = INFINITE,
                        activation_phases = [],
                        keep_duration = 0
        )

        return cinfo

    def __init__(self, modules, entity_type=TypeEnums.EXPLORER_CARD, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):
        super().__init__(modules, entity_type, Example_Card_3.info(), frame_enum, data, frame_dim, parent_frame)

class Example_Card_4(Explorer_Card_Template):

    @staticmethod
    def info():

        cinfo = ExplorerCardInfo(
                        name = "Example Card 4",
                        name_color = Colors.WHITE,
                        card_enum = enums.ExplorerCardEnums.EXAMPLE_CARD_4,
                        description = "Example Card",
                        description_color = [("Example Card", Colors.STANDARD_TEXT_COLOR)],
                        tags = [],
                        standard_selling_reward = {},
                        card_image_path  = os.path.join(card_asset_path, "Example_Card_4.png"),
                        standard_image_path = os.path.join(card_asset_path, "Example_Card_4.png"),
                        max_per_deck = INFINITE,
                        activation_phases = [],
                        keep_duration = 0
        )

        return cinfo

    def __init__(self, modules, entity_type=TypeEnums.EXPLORER_CARD, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):
        super().__init__(modules, entity_type, Example_Card_4.info(), frame_enum, data, frame_dim, parent_frame)

class Example_Card_5(Explorer_Card_Template):

    @staticmethod
    def info():

        cinfo = ExplorerCardInfo(
                        name = "Example Card 5",
                        name_color = Colors.WHITE,
                        card_enum = enums.ExplorerCardEnums.EXAMPLE_CARD_5,
                        description = "Example Card",
                        description_color = [("Example Card", Colors.STANDARD_TEXT_COLOR)],
                        tags = [],
                        standard_selling_reward = {},
                        card_image_path  = os.path.join(card_asset_path, "Example_Card_5.png"),
                        standard_image_path = os.path.join(card_asset_path, "Example_Card_5.png"),
                        max_per_deck = INFINITE,
                        activation_phases = [],
                        keep_duration = 0
        )

        return cinfo

    def __init__(self, modules, entity_type=TypeEnums.EXPLORER_CARD, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):
        super().__init__(modules, entity_type, Example_Card_5.info(), frame_enum, data, frame_dim, parent_frame)

class Example_Card_6(Explorer_Card_Template):

    @staticmethod
    def info():

        cinfo = ExplorerCardInfo(
                        name = "Example Card 6",
                        name_color = Colors.WHITE,
                        card_enum = enums.ExplorerCardEnums.EXAMPLE_CARD_6,
                        description = "Example Card",
                        description_color = [("Example Card", Colors.STANDARD_TEXT_COLOR)],
                        tags = [],
                        standard_selling_reward = {},
                        card_image_path  = os.path.join(card_asset_path, "Example_Card_6.png"),
                        standard_image_path = os.path.join(card_asset_path, "Example_Card_6.png"),
                        max_per_deck = INFINITE,
                        activation_phases = [],
                        keep_duration = 0
        )

        return cinfo

    def __init__(self, modules, entity_type=TypeEnums.EXPLORER_CARD, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):
        super().__init__(modules, entity_type, Example_Card_6.info(), frame_enum, data, frame_dim, parent_frame)

class Example_Card_7(Explorer_Card_Template):

    @staticmethod
    def info():

        cinfo = ExplorerCardInfo(
                        name = "Example Card 7",
                        name_color = Colors.WHITE,
                        card_enum = enums.ExplorerCardEnums.EXAMPLE_CARD_7,
                        description = "Example Card",
                        description_color = [("Example Card", Colors.STANDARD_TEXT_COLOR)],
                        tags = [],
                        standard_selling_reward = {},
                        card_image_path  = os.path.join(card_asset_path, "Example_Card_7.png"),
                        standard_image_path = os.path.join(card_asset_path, "Example_Card_7.png"),
                        max_per_deck = INFINITE,
                        activation_phases = [],
                        keep_duration = 0
        )

        return cinfo

    def __init__(self, modules, entity_type=TypeEnums.EXPLORER_CARD, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):
        super().__init__(modules, entity_type, Example_Card_7.info(), frame_enum, data, frame_dim, parent_frame)


class Example_Card_8(Explorer_Card_Template):

    @staticmethod
    def info():

        cinfo = ExplorerCardInfo(
                        name = "Example Card 8",
                        name_color = Colors.WHITE,
                        card_enum = enums.ExplorerCardEnums.EXAMPLE_CARD_8,
                        description = "Example Card",
                        description_color = [("Example Card", Colors.STANDARD_TEXT_COLOR)],
                        tags = [],
                        standard_selling_reward = {},
                        card_image_path  = os.path.join(card_asset_path, "Example_Card_8.png"),
                        standard_image_path = os.path.join(card_asset_path, "Example_Card_8.png"),
                        max_per_deck = INFINITE,
                        activation_phases = [],
                        keep_duration = 0
        )

        return cinfo

    def __init__(self, modules, entity_type=TypeEnums.EXPLORER_CARD, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):
        super().__init__(modules, entity_type, Example_Card_8.info(), frame_enum, data, frame_dim, parent_frame)


class Example_Card_9(Explorer_Card_Template):

    @staticmethod
    def info():

        cinfo = ExplorerCardInfo(
                        name = "Example Card 9",
                        name_color = Colors.WHITE,
                        card_enum = enums.ExplorerCardEnums.EXAMPLE_CARD_9,
                        description = "Example Card",
                        description_color = [("Example Card", Colors.STANDARD_TEXT_COLOR)],
                        tags = [],
                        standard_selling_reward = {},
                        card_image_path  = os.path.join(card_asset_path, "Example_Card_9.png"),
                        standard_image_path = os.path.join(card_asset_path, "Example_Card_9.png"),
                        max_per_deck = INFINITE,
                        activation_phases = [],
                        keep_duration = 0
        )

        return cinfo

    def __init__(self, modules, entity_type=TypeEnums.EXPLORER_CARD, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):
        super().__init__(modules, entity_type, Example_Card_9.info(), frame_enum, data, frame_dim, parent_frame)

class Example_Card_10(Explorer_Card_Template):

    @staticmethod
    def info():

        cinfo = ExplorerCardInfo(
                        name = "Example Card 10",
                        name_color = Colors.WHITE,
                        card_enum = enums.ExplorerCardEnums.EXAMPLE_CARD_4,
                        description = "Example Card",
                        description_color = [("Example Card", Colors.STANDARD_TEXT_COLOR)],
                        tags = [],
                        standard_selling_reward = {},
                        card_image_path  = os.path.join(card_asset_path, "Example_Card_10.png"),
                        standard_image_path = os.path.join(card_asset_path, "Example_Card_10.png"),
                        max_per_deck = INFINITE,
                        activation_phases = [],
                        keep_duration = 0
        )

        return cinfo

    def __init__(self, modules, entity_type=TypeEnums.EXPLORER_CARD, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):
        super().__init__(modules, entity_type, Example_Card_10.info(), frame_enum, data, frame_dim, parent_frame)



class Small_Rest(Explorer_Card_Template):

    @staticmethod
    def info():

        cinfo = ExplorerCardInfo()

        cinfo.name = "Small Rest"
        cinfo.name_color = Colors.STANDARD_TEXT_COLOR

        cinfo.card_enum = enums.ExplorerCardEnums.SMALL_REST
        cinfo.description = "This card generates 1 Rest Token."
        cinfo.description_color = [("This card generates 1 Rest Token", Colors.STANDARD_TEXT_COLOR)]
        cinfo.tags = [
                        tags.Healing_Tag(healing_factor=0),
                        tags.Healing_Token(),
                        tags.Healing_Token_Generator(amount_generated=1)
                    ]


        cinfo.card_image_path = os.path.join(card_asset_path, "Small_Rest_Card.png")
        cinfo.standard_image_path = os.path.join(standard_asset_path, "Small_Rest_Standard.png")

        cinfo.max_per_deck = 40
        cinfo.activation_phases = []

        return cinfo


    def __init__(self, modules, entity_type=TypeEnums.EXPLORER_CARD, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):
        super().__init__(modules, entity_type, Small_Rest.info(), frame_enum, data, frame_dim, parent_frame)

    def tick(self, phaseinfo, location):
        #superclass tick
        Explorer_Card_Template.tick(self, phaseinfo, location)

    def render(self, screen):
        pass
