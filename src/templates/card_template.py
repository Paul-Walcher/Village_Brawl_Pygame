"""
Template for any explorer.
"""
from abc import ABC, abstractmethod
from enum import Enum, auto

"""
class CardTag:
    pass
"""

class CardInfo:

    def __init__(self):

        self.card_enum = None
        

class Card_Template(ABC):

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

    self.name = name
    self.name_color = name_color
    self.card_enum = card_enum
    self.description = description
    self.tags = (tags if tags is not None else [])
    self.standard_selling_reward = (standard_selling_reward if standard_selling_reward is not None else {})
    self.card_image_path = card_image_path
    self.standard_image_path = standard_image_path
    self.max_per_deck = max_per_deck
    self.activation_phases = (activation_phases if activation_phases is not None else [])


    @abstractmethod
    def activate(self, context, cardinfo, phase, location):
        """
        Returns an Activation Result
        """
        pass

    @abstractmethod
    def info(self, context):
        pass
