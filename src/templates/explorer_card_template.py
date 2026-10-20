"""
Template for any explorer.
"""
from abc import ABC, abstractmethod
from enum import Enum, auto

import constants
from constants import Fonts, Colors
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
                playable_locations = None,
                activation_phases: list = None,
                keep_duration=0
                    ):


        super().__init__(name, name_color, description, description_color, card_image_path, standard_image_path)

        self.card_enum = None

        self.tags = (tags if tags is not None else [])
        self.max_per_deck = max_per_deck
        self.activation_phases = (activation_phases if activation_phases is not None else [])
        self.playable_locations = (playable_locations if playable_locations is not None else [])
        self.keep_duration = keep_duration

    def get_info_page_parts(self, frame_dim,
                                font=Fonts.MINECRAFT,
                                hmargin=0, vmargin = 0,
                                chars_per_line=50, lines_per_page=5,
                                height_distributions=[0.1, 0.05, 0.45, 0.1, 0.25, 0.05]):#equals: headline area, distance, card image area, distance, textbox area, distance)

        page_parts = Renderable_Card.get_info_page_parts(self, frame_dim, dont, hmargin, vmargin, chars_per_line, lines_per_page, height_distributions)

        textbox_ref = page_parts[2][0]

        tag_headline_page = [[[("Tags", Colors.STANDARD_TEXT_COLOR)]]]

        tag_pages = []

        for tag in self.tags:

            strag = str(tag)
            lines = strag.splitlines()
            for line in lines:
                tag_pages.append((line, tag.tag_color))
                tag_pages.append(graphics.NL)

        tag_pages = graphics.page_by_chars_color(tag_pages, line_length=chars_per_line, paragraph_length=lines_per_page)

        last_page = tag_pages[-1]
        if len(last_page) < lines_per_page:
            last_page.extend([[]] * (lines_per_page - len(last_page)))

        return page_parts


class Explorer_Card_Template(PlaysetEntity):

    @staticmethod
    def info():
        return CardInfo()

    def __init__(self, modules, cinfo=None, frame_enum=FrameEnums.UNDEFINED, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):

        super().__init__(frame_enum, data, frame_dim, parent_frame)

        self.info = (cinfo if cinfo is not None else Explorer_Card_Template.info())


    def tick(self, phaseinfo, location):
        super().tick(phaseinfo)
