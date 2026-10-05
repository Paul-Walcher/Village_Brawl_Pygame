"""
Template for any explorer.
"""
from abc import ABC, abstractmethod
from enum import Enum, auto

from templates.activatable import Activatable, ActivationResult, ActivationResultEnums
"""
class CardTag:
    pass
"""

class CardInfo:

    def __init__(self,
                name: str = "",
                name_color: tuple = (255, 255, 255),
                card_enum = None,
                description: str = "",
                tags: list = None,
                standard_selling_reward = None,
                card_image_path: str = "",
                standard_image_path: str = "",
                max_per_deck: int = 4,
                activation_phases: list = None
                    ):


        self.card_enum = None

        self.name = name
        self.name_color = name_color
        self.description = description
        self.tags = (tags if tags is not None else [])
        self.standard_selling_reward = (standard_selling_reward if standard_selling_reward is not None else [])#list of dictionaries
        self.card_image_path = card_image_path
        self.standard_image_path = standard_image_path
        self.max_per_deck = max_per_deck
        self.activation_phases = (activation_phases if activation_phases is not None else [])


class Explorer_Card_Template(Activatable):

    @staticmethod
    def info():
        return CardInfo()

    def __init__(self, modules, info=None):

        self.modules = modules
        self.mappings = modules.mappings
        self.enums = modules.enums
        self.tags = modules.tags

        self.info = (info if info is not None else Card_Template.info())

        super().__init__(self.info.activation_phases)
