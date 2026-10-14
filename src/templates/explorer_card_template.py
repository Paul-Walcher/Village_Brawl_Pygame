"""
Template for any explorer.
"""
from abc import ABC, abstractmethod
from enum import Enum, auto

import constants
from Frames.frame import Frame
from Frames.frame_enums import FrameEnums

from templates.renderable_card import Renderable_Card
from templates.playset_entity import PlaysetEntity
"""
class CardTag:
    pass
"""

class CardInfo(Renderable_Card):

    def __init__(self,
                name: str = "",
                name_color: tuple = (255, 255, 255),
                card_enum = None,
                description: str = "",
                description_color: str = None,
                tags: list = None,
                standard_selling_reward = None,
                card_image_path: str = "",
                standard_image_path: str = "",
                max_per_deck: int = 4,
                activation_phases: list = None
                    ):


        super().__init__(name, name_color, description, description_color, card_image_path, standard_image_path)

        self.card_enum = None

        self.tags = (tags if tags is not None else [])
        self.max_per_deck = max_per_deck
        self.activation_phases = (activation_phases if activation_phases is not None else [])


class Explorer_Card_Template(PlaysetEntity):

    @staticmethod
    def info():
        return CardInfo()

    def __init__(self, modules, cinfo=None, frame_enum=FrameEnums.UNDEFINED, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):

        super().__init__(frame_enum, data, frame_dim, parent_frame)

        self.info = (cinfo if cinfo is not None else Explorer_Card_Template.info())


    def tick(self, phase_info, location):
        super().tick(phaseinfo)

    def get_selling_reward(self):
        #list of (enum: (amount, type))
        return {}
