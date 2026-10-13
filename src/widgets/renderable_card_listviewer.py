import os
import pygame
import threading

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import (
    PLAYSETS_FOLDER,
    Colors,
    Fonts,
    Fontsizes,
    KeyAlternatives,
    FrameDataID
)
import graphics
from clock import Clock
from modules import Modules
import constants
from widgets.widget import Widget
from event_queue_manager import Event
from copy import deepcopy

class RenderableCardListviewer(Widget):

    class SortingFunctions:

        @staticmethod
        def name_descending(cardlist):

            clist = [(key, value) for key, value in cardlist.items()]
            clist.sort(key=lambda x: x[0])
            return clist

        @staticmethod
        def name_ascending(cardlist):

            clist = [(key, value) for key, value in cardlist.items()]
            clist.sort(key=lambda x: x[0])
            clist.reverse()
            return clist

        @staticmethod
        def amount_descending(cardlist):

            clist = [(key, value) for key, value in cardlist.items()]
            clist.sort(key=lambda x: x[1])
            return clist

        @staticmethod
        def amount_ascending(cardlist):

            clist = [(key, value) for key, value in cardlist.items()]
            clist.sort(key=lambda x: x[1])
            clist.reverse()
            return clist


    def __init__(self,
                frame_dim,
                full_cardlist, #is RenderableCard: amount
                groups,  #must include at least one group. is {name: {"cardlist": {renderable_card: amount}, "mutable": True}}
                shown_group=None,
                max_group_number=25,
                cards_per_line=5,
                cards_per_column=5,
                sorting_function=RenderableCardListviewer.SortingFunctions.name_descending,
                max_groups_shown_in_menu=10,
                trunk_shown=False,
                search_while_typing=True,
                trunk_width_percentage=0.5,
                border_frame_margin=0.05,
                border_frame_color=Colors.DARK_CYAN,
                border_frame_outline_margin = 0.1,
                border_frame_outline_color=Colors.BLACK,
                main_list_color=Colors.CYAN,
                trunk_list_color=Colors.CYAN,
                trunk_separator_margin=0.05,
                trunk_separator_color=Colors.BLACK,
                trunk_menu_bar_margin=0.2,
                trunk_menu_bar_color=Colors.DARK_SLATE_GRAY,
                trunk_menu_bar_hmargin=0.2,
                trunk_menu_bar_vmargin=0.1,
                trunk_menu_bar_textinput_width_percentage=0.6,
                trunk_menu_bar_option_dropdown_width_percentage=0.3
                ):

        if len(groups) == 0:
            raise RuntimeError("You need at least one group")
        if len(groups) > max_group_number:
            raise RuntimeError("Too many groups. Adjust your max_group_size")

        super().__init__(frame_dim)

        self.full_cardlist = full_cardlist.copy()
        self.groups = deepcopy(groups)
        self.shown_group = (shown_group if shown_group is not None else list(self.groups.keys())[0])
        self.max_group_number = max_group_number
        self.sorting_function = sorting_function
        self.max_groups_shown_in_menu = max_groups_shown_in_menu
        self.cards_per_line = cards_per_line
        self.cards_per_column = cards_per_column

        self.trunk_shown = trunk_shown
        self.search_while_typing = search_while_typing

        self.border_frame_margin = border_frame_margin
        self.border_frame_color = border_frame_color
        self.border_frame_outline_margin = border_frame_outline_margin
        self.border_frame_outline_color = border_frame_outline_color

        self.main_list_color = main_list_color
        self.trunk_list_color = trunk_list_color

        self.trunk_separator_margin = trunk_separator_margin
        self.trunk_separator_color = trunk_separator_color

        self.trunk_width_percentage = trunk_width_percentage
        self.trunk_menu_bar_margin = trunk_menu_bar_margin
        self.trunk_menu_bar_color = trunk_menu_bar_color
        self.trunk_menu_bar_hmargin = trunk_menu_bar_hmargin
        self.trunk_menu_bar_vmargin = trunk_menu_bar_vmargin

        self.trunk_menu_bar_textinput_width_percentage = trunk_menu_bar_textinput_width_percentage
        self.trunk_menu_bar_option_dropdown_width_percentage = trunk_menu_bar_option_dropdown_width_percentage

        self.rerender()

    def tick(self):
        pass

    def rerender(self):

        self.inner_area = graphics.apply_margins(self.frame_dim, self.border_frame_margin, self.border_frame_margin)

        self.main_list_area = self.inner_area.copy()
        self.main_list_area.width = int((1.0 - self.trunk_width_percentage) * self.main_list_area.width)

        trunk_x = self.inner_area.x + (self.inner_area.width if not self.trunk_shown else self.main_list_area.width)
        #trunk gets a rect starting at 0, 0, because it has a own surface
        self.trunk_area = pygame.Rect(trunk_x, self.inner_area.y, int(self.trunk_width_percentage * self.main_list_area.width), self.inner_area.height)

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.trunk_surface = pygame.Surface((self.trunk_area.width, self.trunk_area.height), pygame.SRCALPHA)


        self.render()

    def render(self):

        self.surface.fill(self.main_list_color)
        self.trunk_surface.fill(self.trunk_list_color)

        self.surface.blit(self.trunk_surface, (self.trunk_area.x, self.trunk_area.y))


    def get_surfaces(self):
        return [self.surface]

    def get_surfaces_with_position(self):
        return [(self.surface, (self.x, self.y))]
