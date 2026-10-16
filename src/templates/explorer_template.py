
"""
Template for any explorer.
"""
import pygame
from abc import ABC, abstractmethod
from enum import Enum, auto

from deck import Deck

import constants
from constants import Colors, Fonts
import graphics

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from templates.playset_entity import PlaysetEntity

from templates.renderable_card import Renderable_Card
from copy import deepcopy

class ExplorerInfo(Renderable_Card):

    def __init__(self,
                name: str = "",
                name_color: tuple = (255, 255, 255),
                explorer_enum = None,
                description: str = "",
                description_color: str = "",
                card_image_path: str = "",
                standard_image_path: str = "",
                lives: int = 5,
                tags = None,
                ability_activation_phases = None,
                inventory_size: float = 10.0,
                starting_items: dict = None,
                starting_supporters: dict = None,
                starting_cards: dict = None,
                starting_blueprints: dict = None,
                starting_packs: dict = None,
                unlocked_packs: dict = None,
                unlockable_packs: dict = None,
                starting_buildings: dict = None,
                starting_villagers: dict = None):


        super().__init__(name, name_color, description, description_color, card_image_path, standard_image_path)
        #reference to the explorer enum
        self.explorer_enum = explorer_enum

        #starting items. these need to be the enums from items_mappings.
        #starting items are {name_enum: amount}
        self.starting_items = (starting_items if starting_items is not None else {})
        #starting supporters.
        #starting supporters are: {name_enum, amount}
        self.starting_supporters = (starting_supporters if starting_supporters is not None else {})
        #starting cards
        #{card_enum: amount}
        self.starting_cards = (starting_cards if starting_cards is not None else {})
        #blueprints, {card_enum: amount}
        self.starting_blueprints = (starting_blueprints if starting_blueprints is not None else {})
        #starting_packs
        #starting packs. these need to be the enums from pack_mappings
        #starting packs are {name_enum: amount}
        self.starting_packs = (starting_packs if starting_packs is not None else {})
        #unlocked packs
        self.unlocked_packs = (unlocked_packs if unlocked_packs is not None else [])
        #unlockable_packs
        self.unlockable_packs = (unlockable_packs if unlockable_packs is not None else [])
        #buildings
        self.starting_buildings = (starting_buildings if starting_buildings is not None else {})
        #villagers
        self.starting_villagers = (starting_villagers if starting_villagers is not None else {})
        #stats
        #lives
        self.lives = lives
        #tags
        self.tags = (tags if tags is not None else [])
        #inventory size
        self.inventory_size = inventory_size
        #ability_activation_phases
        self.activation_phases = (ability_activation_phases if ability_activation_phases is not None else [])

    def get_info_page_parts(self, frame_dim,
                                font=Fonts.MINECRAFT,
                                hmargin=0, vmargin = 0,
                                chars_per_line=50, lines_per_page=5,
                                height_distributions=[0.1, 0.05, 0.45, 0.1, 0.25, 0.05]):#equals: headline area, distance, card image area, distance, textbox area, distance)


        stats_hp = 0.2
        stats_insert_index = 3

        adjust = (stats_hp - height_distributions[stats_insert_index])

        tweight = sum([height_distributions[i] for i in range(len(height_distributions)) if i != stats_insert_index])

        height_distributions = list(map(lambda x: x - (x / tweight) * adjust, height_distributions))
        height_distributions[stats_insert_index] = stats_hp

        areas = self.get_areas(frame_dim, height_distributions, hmargin, vmargin)
        stats_text_area = areas[stats_insert_index]

        page_padding = 2

        stats_page = [
                        [("Lives: ", Colors.RED), (f"{self.lives}", Colors.STANDARD_TEXT_COLOR)],
                        [("Inventory Size: ", Colors.BLUE), (f"{self.inventory_size}", Colors.STANDARD_TEXT_COLOR)]
                        ]

        for i in range(page_padding):
            stats_page.insert(0, [])
            stats_page.append([])

        page_parts = Renderable_Card.get_info_page_parts(self,
                                                        frame_dim,
                                                        font=font,
                                                        hmargin=hmargin,
                                                        vmargin=vmargin,
                                                        chars_per_line=chars_per_line,
                                                        lines_per_page=lines_per_page,
                                                        height_distributions=height_distributions
                                                        )

        tbox = page_parts[2][1][0]
        textbox_ref = page_parts[2][0]

        tag_headline_page = [[[("Tags", Colors.STANDARD_TEXT_COLOR)]]]

        tag_pages = []

        for tag in self.tags:

            tag_pages.append((str(tag), tag.tag_color))

        tag_pages = graphics.page_by_chars_color(tag_pages, line_length=chars_per_line, paragraph_length=lines_per_page)

        textbox_ref.add_pages(tag_headline_page)
        textbox_ref.add_pages(tag_pages)




        rendered_stats_page = graphics.render_page_from_chars_color(
                                    font,
                                    stats_page,
                                    stats_text_area,
                                    text_color=Colors.STANDARD_TEXT_COLOR,
                                    vertical_centered = True
                                )

        rstats = []

        for surf, (x, y) in rendered_stats_page:
            rstats.append((surf, (x + tbox - stats_text_area.x, y)))

        page_parts.append(rstats)

        return page_parts

    def render_info_page_parts(self,
                                screen,
                                page_parts,
                                page_index=-1,
                                background_color=Colors.BLACK,
                                outline_size=None,
                                outline_color=None,
                                full_image_shown=False
                                ):

        Renderable_Card.render_info_page_parts(self,
                                    screen,
                                    page_parts=page_parts[:-1],
                                    page_index=page_index,
                                    background_color=background_color,
                                    outline_size=outline_size,
                                    outline_color=outline_color,
                                    full_image_shown=False
                                    )

        stats_page = page_parts[-1]

        for surf, pos in stats_page:
            screen.blit(surf, pos)

        if full_image_shown:

            full_image, full_image_pos = page_parts[3]

            tsurf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            tsurf.fill((*Colors.BLACK, 180))

            tsurf.blit(full_image, full_image_pos)

            screen.blit(tsurf, (0, 0))




class Explorer_Template(PlaysetEntity):


    @staticmethod
    def info():
        return ExplorerInfo()




    def __init__(self, modules, einfo=None, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None, frame_dim=constants.FULLSCREEN, parent_frame=None):

        super().__init__(frame_enum, data, frame_dim, parent_frame)

        #info
        self.info = (einfo if einfo is not None else Explorer_Template.info())

        self.lives = 0 #current lives
        self.inventory_size = 0#inventory_size
        self.inventory = []#current inventory, includes item instances
        self.active_supporters = []#active supporter instances
        self.inactive_supporters = []#supporter instances that can be played, but are inactive.
        self.deck = Deck()#current deck
        self.deck_saves = {}#name: {enum: amount}
        self.trunk = {}#card enum: number of cards, total amount of cards possessed
        self.blueprints = []#blueprint: Blueprint instance
        self.packs = {} #enum: amount
        self.unlocked_packs = [] #list of enums
        self.unlockable_packs = [] #list of enums


        self.load_instances()

    def check_activation(self):
        #receives the data, and if the card can be activated it should return True, else False
        return False

    def initialize_activation(self):
        pass


    def load_instances(self):

        """
        loads the instances from the info, deletes all previous data
        """

        self.lives = self.info.lives
        self.max_inventory_size = self.info.inventory_size

        self.inventory = []
        for key, value in self.info.starting_items.items():
            self.inventory.extend([self.mappings.item_mappings[key](self.modules) for i in range(value)])

        self.active_supporters = []
        self.inactive_supporters = []
        for key, value in self.info.starting_supporters.items():
            self.inactive_supporters.extend([self.mappings.supporter_mappings[key](self.modules) for i in range(value)])

        self.trunk = self.info.starting_cards.copy()

        self.blueprints = []
        for key, value in self.info.starting_blueprints.items():
            self.blueprints.extend([self.mappings.blueprint_mappings[key](self.modules) for i in range(value)])

        self.packs = self.info.starting_packs.copy()
        self.unlocked_packs = self.info.unlocked_packs.copy()
        self.unlockable_packs = self.info.unlockable_packs.copy()

    def inventory_weight(self):
        return sum([item_.info.weight for item_ in self.inventory])

    def free_inventory_weight(self):
        return max(self.max_inventory_size - sum([item_.info.weight for item_ in self.inventory]), 0)


    def add_item(self, item_enum, amount=1):
        #adds an item into the inventory, if the inventory is big enough
        new_item_ref = self.mappings.item_mappings[item_enum]

        if new_item_ref.info().weight > self.free_inventory_weight():
            return False
        else:
            for i in range(amount):
                self.inventory.append(new_item_ref(self.modules))
            return True
