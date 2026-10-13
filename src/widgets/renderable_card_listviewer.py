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

    NOTHING_FOCUSED = 0
    MAIN_LIST_FOCUSED = 1
    TRUNK_FOCUSED = 2
    TRUNK_MENU_BAR_FOCUSED = 3

    class SortingFunctions:

        @staticmethod
        def no_order(cardlist):
            return [(key, value) for key, value in cardlist.items()]

        @staticmethod
        def name_descending(cardlist):

            clist = [(key, value) for key, value in cardlist.items()]
            clist.sort(key=lambda x: x[0].name)
            return clist

        @staticmethod
        def name_ascending(cardlist):

            clist = [(key, value) for key, value in cardlist.items()]
            clist.sort(key=lambda x: x[0].name)
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
                font=Fonts.MINECRAFT,
                max_group_number=25,
                cards_per_line=4,
                cards_per_column=3,
                sorting_function=None,
                max_groups_shown_in_menu=10,
                trunk_shown=False,
                search_while_typing=True,
                trunk_width_percentage=0.5,
                border_frame_margin=0.02,
                label_vmargin=0.1,
                label_color=Colors.BLACK,
                label_alpha=230,
                group_name_color=Colors.WHITE,
                border_frame_color=Colors.DARK_CYAN,
                border_frame_outline_margin = 0.2,
                border_frame_outline_color=Colors.BLACK,
                main_list_color=Colors.CYAN,
                trunk_list_color=Colors.BRIGHT_BLUE,
                trunk_separator_margin=0.005,
                trunk_separator_color=Colors.BLACK,
                trunk_menu_bar_margin=0.2,
                trunk_menu_bar_color=Colors.DARK_SLATE_GRAY,
                trunk_menu_bar_hmargin=0.2,
                trunk_menu_bar_vmargin=0.1,
                inner_frame_hmargin=0.1,
                inner_frame_vmargin=0.05,
                trunk_menu_bar_textinput_width_percentage=0.6,
                trunk_menu_bar_option_dropdown_width_percentage=0.3,
                description_color=Colors.BLACK
                ):

        if len(groups) == 0:
            raise RuntimeError("You need at least one group")
        if len(groups) > max_group_number:
            raise RuntimeError("Too many groups. Adjust your max_group_size")

        super().__init__(frame_dim)

        self.full_cardlist = full_cardlist.copy()
        self.groups = deepcopy(groups)
        self.shown_group = (shown_group if shown_group is not None else list(self.groups.keys())[0])
        self.group_name_color = group_name_color
        self.max_group_number = max_group_number
        self.sorting_function = (sorting_function if sorting_function is not None else RenderableCardListviewer.SortingFunctions.name_descending)
        self.max_groups_shown_in_menu = max_groups_shown_in_menu
        self.cards_per_line = cards_per_line
        self.cards_per_column = cards_per_column
        self.font = font
        self.description_color = description_color

        self.card_render_cache = {}
        self.text_render_cache = {}

        self.label_vmargin = label_vmargin
        self.label_color = label_color
        self.label_alpha = label_alpha

        self.selected_card_index_main_list = 0 #column, row
        self.selected_card_index_trunk = 0 #column, row

        self.state = RenderableCardListviewer.NOTHING_FOCUSED

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

        self.inner_frame_hmargin = inner_frame_hmargin
        self.inner_frame_vmargin = inner_frame_vmargin

        self.trunk_menu_bar_textinput_width_percentage = trunk_menu_bar_textinput_width_percentage
        self.trunk_menu_bar_option_dropdown_width_percentage = trunk_menu_bar_option_dropdown_width_percentage

        self.rerender()

    def tick(self):
        pass

    def rerender(self):

        self.border_width = int(self.border_frame_margin * self.width)
        self.border_height = int(self.border_frame_margin * self.height)

        self.inner_area = pygame.Rect(self.x + self.border_width, self.y + self.border_height,
                                        self.width - 2*self.border_width, self.height - 2*self.border_height)

        self.main_list_area = self.inner_area.copy()
        self.main_list_area.width = int((1.0 - self.trunk_width_percentage) * self.main_list_area.width)

        self.trunk_separator_width = int(self.inner_area.width * self.trunk_separator_margin)
        self.trunk_separator_height = self.inner_area.height
        self.trunk_separator_frame_dim = pygame.Rect(0, 0, self.trunk_separator_width, self.trunk_separator_height)
        trunk_x = self.inner_area.x + (self.inner_area.width if not self.trunk_shown else self.main_list_area.width)
        #trunk gets a rect starting at 0, 0, because it has a own surface
        self.trunk_area = pygame.Rect(trunk_x, self.inner_area.y, int(self.trunk_width_percentage * self.inner_area.width), self.inner_area.height)

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.trunk_surface = pygame.Surface((self.trunk_area.width, self.trunk_area.height), pygame.SRCALPHA)

        self.border_outline_width = int(self.border_width * self.border_frame_outline_margin)
        self.border_outline_height = int(self.border_height * self.border_frame_outline_margin)

        blen = min(self.border_outline_width, self.border_outline_height)
        self.inner_border_corners = [(self.border_width-blen, self.border_height - blen),
                                (self.width - self.border_width, self.border_height - blen),
                                (self.width - self.border_width, self.height - self.border_height + blen),
                                (self.border_width - blen, self.height - self.border_height)
                            ]
        #(rect, color)
        self.border_lines = [
                                (pygame.Rect(0, 0, self.width, self.border_height), self.border_frame_color),
                                (pygame.Rect(self.width - self.border_width, 0, self.border_width, self.height), self.border_frame_color),
                                (pygame.Rect(0, 0, self.border_width, self.height), self.border_frame_color),
                                (pygame.Rect(0, self.height - self.border_height, self.width, self.border_height), self.border_frame_color),
                                #outer outline
                                (pygame.Rect(0, 0, self.width, self.border_outline_height), self.border_frame_outline_color),
                                (pygame.Rect(self.width - self.border_outline_width, 0, self.border_outline_width, self.height), self.border_frame_outline_color),
                                (pygame.Rect(0, 0, self.border_outline_width, self.height), self.border_frame_outline_color),
                                (pygame.Rect(0, self.height - self.border_outline_height, self.width, self.border_outline_height), self.border_frame_outline_color)
                                #inner outline
                            ]

        def rs(p1, p2):

            x = p1[0]
            y = p1[1]

            w = p2[0] - p1[0]
            if w == 0:
                w = blen

            h = p2[1] - p1[1]
            if h == 0:
                h = blen

            if w < 0 or h < 0:

                x = p2[0]
                y = p2[1]

                w = p1[0] - p2[0]
                if w == 0:
                    w = blen

                h = p1[1] - p2[1]
                if h == 0:
                    h = blen


            return pygame.Rect(x, y, w, h)

        for i in range(len(self.inner_border_corners)+1):

            i1 = i % len(self.inner_border_corners)
            i2 = (i+1) % len(self.inner_border_corners)

            p1, p2 = self.inner_border_corners[i1], self.inner_border_corners[i2]

            self.border_lines.append((rs(p1, p2), self.border_frame_outline_color))

        #rendering the Name Label
        self.label_height = int(self.inner_area.height * self.label_vmargin)
        self.label_surface = pygame.Surface((self.main_list_area.width, self.label_height), pygame.SRCALPHA)
        self.label_surface.set_alpha(self.label_alpha)
        self.label_surface_pos = (self.inner_area.x, self.inner_area.y)

        self.label_frame = self.main_list_area.copy()
        self.label_frame.height = self.label_height
        self.label_frame = graphics.apply_margins(self.label_frame, 0.05, 0.2)

        #rendering the name
        fsize = graphics.get_fontsize(self.font, [self.shown_group], self.label_frame)
        self.label_text = graphics.render_text(self.font, fsize, self.shown_group, self.group_name_color)
        self.label_pos = graphics.get_center_with_surface(self.label_text, self.label_frame)

        self.main_list_area.y += self.label_height
        self.main_list_area.height -= self.label_height

        self.main_list_hdist_margin = 0.2
        self.main_list_vdist_margin = 0.2

        self.main_list_hdist = int(self.main_list_area.width * self.main_list_hdist_margin)
        self.main_list_vdist = int(self.main_list_area.height * self.main_list_vdist_margin)

        self.main_list_hseparator = self.main_list_hdist // (self.cards_per_line + 2)
        self.main_list_vseparator = self.main_list_vdist // (self.cards_per_column + 2)

        self.main_list_cwdith = (self.main_list_area.width - self.main_list_hdist) // self.cards_per_line
        self.main_list_cheight = (self.main_list_area.height - self.main_list_vdist) // self.cards_per_column

        self.gcards = self.groups[self.shown_group]["cardlist"]
        self.main_list_cards = self.sorting_function(self.gcards)

        self.cardnum_margin = 0.2
        #rendering all cards, and adding their position
        self.cardnum_height = int(self.cardnum_margin * self.main_list_cheight)
        self.main_list_card_height = self.main_list_cheight - self.cardnum_height

        cx = self.main_list_area.x + self.main_list_hseparator
        cy = self.main_list_area.y + self.main_list_vseparator

        idx = 0

        self.main_list_cards_rects = []
        for cinfo, amount in self.main_list_cards:

            rrect = pygame.Rect(cx, cy, self.main_list_cwdith, self.main_list_cheight)

            img_rect = rrect.copy()
            img_rect.height = self.main_list_card_height

            img_text = [f"x{amount}"]

            text_rect = rrect.copy()
            text_rect.y += img_rect.height
            text_rect.height -= img_rect.height

            text_rect = graphics.apply_margins(text_rect, 0.1, 0.1)

            self.main_list_cards_rects.append((img_rect, text_rect))

            idx += 1

            cx += self.main_list_cwdith + self.main_list_hseparator

            if not (idx) % self.cards_per_line:

                cx = self.main_list_area.x + self.main_list_hseparator
                cy += self.main_list_cheight + self.main_list_vseparator




        self.render()



    def render(self):

        self.surface.fill(self.main_list_color)
        self.trunk_surface.fill(self.trunk_list_color)
        self.label_surface.fill(self.label_color)

        for i in range(len(self.main_list_cards_rects)):

            img_rect, text_rect = self.main_list_cards_rects[i]

            if self.main_list_area.colliderect(img_rect):
                cinfo = self.main_list_cards[i][0]
                img = None
                if cinfo.card_image_path in self.card_render_cache:
                    img = self.card_render_cache[cinfo.card_image_path]
                else:

                    img = graphics.render_image(cinfo.card_image_path)
                    hscale, vscale = 0, 0

                    if cinfo.width_to_height_ratio > 1.0:
                        hscale = self.main_list_cwdith
                        vscale = (1.0 / cinfo.width_to_height_ratio) * self.main_list_cwdith
                    else:
                        vscale = self.main_list_card_height
                        hscale = cinfo.width_to_height_ratio * self.main_list_card_height

                    img = pygame.transform.smoothscale(img, (hscale, vscale))
                    self.card_render_cache[cinfo.card_image_path] = img

                self.surface.blit(img, (img_rect.x, img_rect.y))

            if self.main_list_area.colliderect(text_rect):
                amount = self.main_list_cards[i][1]
                trend = None

                if amount in self.text_render_cache:
                    trend = self.text_render_cache[amount]
                else:
                    trend = graphics.render_page_from_chars(self.font, [f"x{amount}"], pygame.Rect(0, 0, text_rect.width, text_rect.height),
                                                            self.description_color, centered=True, vertical_centered=True
                                                            )
                    self.text_render_cache[amount] = trend

                for surf, pos in trend:
                    self.surface.blit(surf, (pos[0] + text_rect.x, pos[1] + text_rect.y))

        if self.trunk_area.x < self.width:
            #drawing separator
            pygame.draw.rect(self.trunk_surface, self.trunk_separator_color, self.trunk_separator_frame_dim)
            self.surface.blit(self.trunk_surface, (self.trunk_area.x, self.trunk_area.y))

        for rect, color in self.border_lines:
            pygame.draw.rect(self.surface, color, rect)

        self.surface.blit(self.label_surface, self.label_surface_pos)
        self.surface.blit(self.label_text, self.label_pos)


    def get_surfaces(self):
        return [self.surface]

    def get_surfaces_with_position(self):
        return [(self.surface, (self.x, self.y))]
