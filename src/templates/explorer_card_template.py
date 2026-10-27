"""
Template for any explorer.
"""
from abc import ABC, abstractmethod
from enum import Enum, auto

import constants
import graphics
from constants import Fonts, Colors
from Frames.frame import Frame
from Frames.frame_enums import FrameEnums

from templates.renderable_cardinfo import Renderable_CardInfo
from templates.playset_entity import PlaysetEntity
from calculations import Weightlist
"""
class CardTag:
    pass
"""

class ExplorerCardInfo(Renderable_CardInfo):

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
                                height_distributions=[0.1, 0.05, 0.45, 0.1, 0.25, 0.05]
                                ):#equals: headline area, distance, card image area, distance, textbox area, distance)

        #extra info

        page_parts = Renderable_CardInfo.get_info_page_parts(self, frame_dim, font, hmargin, vmargin, chars_per_line, lines_per_page, height_distributions)


        #creating extra info pages
        einfo_text = [  graphics.NP(0),
                        (f"Max. per Deck: {str(self.max_per_deck)}", Colors.MAX_PER_DECK_COLOR), graphics.NL,
                        (f"Keep Duration:{str(self.keep_duration)}", Colors.KEEP_DURATION_COLOR), graphics.NL,
                        graphics.NP(lines_per_page-2),
                        (f"Activation Phases:", Colors.STANDARD_TEXT_COLOR), graphics.NL, graphics.NL
                    ]

        for phase in self.activation_phases:
            einfo_text.append((str(phase), Colors.STANDARD_TEXT_COLOR))
            einfo_text.append(graphics.NL)


        einfo_text.append(graphics.NL)
        einfo_text.append((f"Playable Locations:", Colors.STANDARD_TEXT_COLOR))
        einfo_text.append(graphics.NL)
        einfo_text.append(graphics.NL)

        for location in self.playable_locations:
            einfo_text.append((str(location), Colors.STANDARD_TEXT_COLOR))
            einfo_text.append(graphics.NL)

        einfo_pages = graphics.page_by_chars_color(einfo_text, chars_per_line, lines_per_page)


        textbox_ref = page_parts.textbox

        textbox_ref.add_pages(einfo_pages)

        tag_headline_page = [[[graphics.NP(0), ("Tags", Colors.STANDARD_TEXT_COLOR)]]]
        tag_pages = []

        for tag in self.tags:

            strag = str(tag)
            lines = strag.splitlines()
            for line in lines:
                tag_pages.append((line, tag.tag_color))
                tag_pages.append(graphics.NL)

        tag_pages = graphics.page_by_chars_color(tag_pages, line_length=chars_per_line, paragraph_length=lines_per_page)
        if tag_pages:
            last_page = tag_pages[-1]
            if len(last_page) < lines_per_page:
                last_page.extend([[]] * (lines_per_page - len(last_page)))

            textbox_ref.add_pages(tag_headline_page)
            textbox_ref.add_pages(tag_pages)

        return page_parts


class Explorer_Card_Template(PlaysetEntity):

    @staticmethod
    def info():
        return ExplorerCardInfo()

    def __init__(self, modules, cinfo=None, frame_enum=FrameEnums.UNDEFINED, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):

        super().__init__(frame_enum, data, frame_dim, parent_frame)

        self.info = (cinfo if cinfo is not None else Explorer_Card_Template.info())


    def tick(self, phaseinfo, location):
        super().tick(phaseinfo)
