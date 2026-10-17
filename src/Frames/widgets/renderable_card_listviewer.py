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
from event_queue_manager import Event
from copy import deepcopy

"""

Important!!!

Create a mutable trunk group in the groups

"""


class RenderableCardListviewer(Frame):

    NOTHING_FOCUSED = 0 #nothing is focused
    MAIN_LIST_FOCUSED = 1 #the cards in the list are focused
    MENU_BAR_FOCUSED = 2 #the menu bar is focused
    DROPDOWN_MENU_FOCUSED = 3 #means the dropdown menu is shown
    SEARCHBAR_FOCUSED = 4 #the textinput is focused
    GROUP_SELECTION = 5 #displays the groups available (Should show if a group is a copy group or not)
    FULL_IMAGE_SHOWN = 6 #if the main list is focused, the selected image is shown on fullscreen

    #view states
    SHOW_WITH_AMOUNT = 100
    SHOW_EACH_CARD = 101

    class SortingFunctions:

        """
        Functions to sort cardlists.
        Each cardlist is: [(RenderableCard (Class), amount)]
        """

        @staticmethod
        def no_order(cardlist):
            return [(key, value) for key, value in cardlist.items()]

        @staticmethod
        def name_descending(cardlist):

            clist = [(key, value) for key, value in cardlist.items()]
            clist.sort(key=lambda x: x[0].info().name)
            return clist

        @staticmethod
        def name_ascending(cardlist):

            clist = [(key, value) for key, value in cardlist.items()]
            clist.sort(key=lambda x: x[0].info().name)
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
                cards_per_column=4,
                cards_per_line_added_when_trunk_not_shown = 4,
                cards_per_column_added_when_trunk_not_shown=0,
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
                description_color=Colors.BLACK,
                main_list_view_state=None,
                trunk_view_state=None
                ):

        if len(groups) == 0:
            raise RuntimeError("You need at least one group")
        if len(groups) > max_group_number:
            raise RuntimeError("Too many groups. Adjust your max_group_size")

        super().__init__(FrameEnums.RENDERABLE_CARDLIST_VIEWER_WIDGET, None, frame_dim)

        self.full_cardlist = full_cardlist.copy()
        self.groups = deepcopy(groups)
        #adding the trunk group
        self.groups["Full Cardlist"] = {"cardlist": self.full_cardlist, "mutable": False, "is_copylist": True}
        self.shown_group = (shown_group if shown_group is not None else list(self.groups.keys())[0])
        self.group_name_color = group_name_color
        self.max_group_number = max_group_number
        self.sorting_function = (sorting_function if sorting_function is not None else RenderableCardListviewer.SortingFunctions.name_descending)
        self.max_groups_shown_in_menu = max_groups_shown_in_menu
        self.cards_per_line = cards_per_line
        self.cards_per_column = cards_per_column
        self.cards_per_line_added_when_trunk_not_shown = cards_per_line_added_when_trunk_not_shown
        self.cards_per_column_added_when_trunk_not_shown = cards_per_column_added_when_trunk_not_shown
        self.font = font
        self.description_color = description_color

        self.main_list_yscroll = 0
        self.trunk_yscroll = 0

        self.card_render_cache_main_list = {}
        self.text_render_cache_main_list = {}

        self.label_vmargin = label_vmargin
        self.label_name_width_percentage = 0.8
        self.label_color = label_color
        self.label_alpha = label_alpha

        self.selected_card_index_main_list = 0
        self.selected_card_index_trunk = 0

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

        self.shadow_hoffset_p = 0.075
        self.shadow_voffset_p = 0.075
        self.shadow_alpha = 120

        self.main_list_selected_index = 0
        self.trunk_selected_index = 0

        self.main_list_cards_dict = {}
        self.trunk_list_cards_dict = {}

        self.selected_increase = 0.05
        self.selected_color = Colors.YELLOW
        self.selected_alpha = 160

        self.main_list_view_state = (main_list_view_state if main_list_view_state is not None else RenderableCardListviewer.SHOW_EACH_CARD)
        self.trunk_view_state = (trunk_view_state if trunk_view_state is not None else RenderableCardListviewer.SHOW_WITH_AMOUNT)

        self.full_image_surface = None

        self.event_clock = Clock()
        self.event_delay = 300
        self.event_clock.start()

        self.rerender()


    def left_pressed(self):

        if self.state == RenderableCardListviewer.NOTHING_FOCUSED:
            self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED
        elif self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:


            line_length = self.cards_per_line
            if not self.trunk_shown:
                line_length += self.cards_per_line_added_when_trunk_not_shown

            if not self.main_list_selected_index % line_length:
                self.state = RenderableCardListviewer.NOTHING_FOCUSED
                return

            self.main_list_selected_index -= 1
            self.main_list_selected_index %= self.n_cards_main_list_shown

            idx, rect, _ = self.main_list_cards_dict[self.main_list_selected_index]

            self.main_list_yscroll = -(rect.y - self.main_list_ystart)

    def right_pressed(self):

        if self.state == RenderableCardListviewer.NOTHING_FOCUSED:
            if self.trunk_shown:
                self.state = RenderableCardListviewer.TRUNK_FOCUSED
            else:
                self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED

        elif self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:

            line_length = self.cards_per_line
            if not self.trunk_shown:
                line_length += self.cards_per_line_added_when_trunk_not_shown

            if not (self.main_list_selected_index+1) % line_length:
                self.state = RenderableCardListviewer.NOTHING_FOCUSED
                return

            self.main_list_selected_index += 1
            self.main_list_selected_index %= self.n_cards_main_list_shown

            idx, rect, _ = self.main_list_cards_dict[self.main_list_selected_index]

            self.main_list_yscroll = -(rect.y - self.main_list_ystart)

    def up_pressed(self):

        if self.state == RenderableCardListviewer.NOTHING_FOCUSED:
            self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED

        elif self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:

            line_length = self.cards_per_line
            if not self.trunk_shown:
                line_length += self.cards_per_line_added_when_trunk_not_shown

            if (self.main_list_selected_index - line_length)  < 0:
                self.main_list_selected_index = 0
                self.state = RenderableCardListviewer.NOTHING_FOCUSED
                return

            self.main_list_selected_index -= line_length
            self.main_list_selected_index %= self.n_cards_main_list_shown

            idx, rect, _ = self.main_list_cards_dict[self.main_list_selected_index]

            self.main_list_yscroll = -(rect.y - self.main_list_ystart)

    def down_pressed(self):

        if self.state == RenderableCardListviewer.NOTHING_FOCUSED:
            self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED

        elif self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:

            line_length = self.cards_per_line
            if not self.trunk_shown:
                line_length += self.cards_per_line_added_when_trunk_not_shown

            self.main_list_selected_index += line_length
            self.main_list_selected_index %= self.n_cards_main_list_shown

            idx, rect, _ = self.main_list_cards_dict[self.main_list_selected_index]

            self.main_list_yscroll = -(rect.y - self.main_list_ystart)




    def tick(self):

        self.manage_pygame_events()

        if self.has_focus:

            if self.event_clock.elapsed() > self.event_delay:
                if (self.key_pressed(pygame.K_RIGHT) or self.key_pressed(KeyAlternatives.RIGHT_ALTERNATIVE)):
                    self.right_pressed()
                    self.event_clock.start()

                if (self.key_pressed(pygame.K_LEFT) or self.key_pressed(KeyAlternatives.LEFT_ALTERNATIVE)):
                    self.left_pressed()
                    self.event_clock.start()

                if (self.key_pressed(pygame.K_UP) or self.key_pressed(KeyAlternatives.UP_ALTERNATIVE)):
                    self.up_pressed()
                    self.event_clock.start()

                if (self.key_pressed(pygame.K_DOWN) or self.key_pressed(KeyAlternatives.DOWN_ALTERNATIVE)):
                    self.down_pressed()
                    self.event_clock.start()

                if (self.key_pressed(pygame.K_LCTRL)):

                    if self.key_pressed(pygame.K_v):

                        if self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:

                            if self.main_list_view_state == RenderableCardListviewer.SHOW_WITH_AMOUNT:
                                self.main_list_view_state = RenderableCardListviewer.SHOW_EACH_CARD
                            elif self.main_list_view_state == RenderableCardListviewer.SHOW_EACH_CARD:
                                self.main_list_view_state = RenderableCardListviewer.SHOW_WITH_AMOUNT

                            self.event_clock.start()
                            self.rerender()

            if (self.key_pressed(KeyAlternatives.SHOW_IMAGE_KEY)):

                if self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:
                    self.state = RenderableCardListviewer.FULL_IMAGE_SHOWN_MAIN_LIST
                    cinfo = self.get_main_list_cinfo_from_selected_index()
                    self.render_full_image(cinfo)

            else:
                if self.state == RenderableCardListviewer.FULL_IMAGE_SHOWN_MAIN_LIST:
                    self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED
                elif self.state == RenderableCardListviewer.FULL_IMAGE_SHOWN_TRUNK:
                    self.state = RenderableCardListviewer.TRUNK_FOCUSED

    def get_main_list_cinfo_from_selected_index(self):

        return self.main_list_cards[self.main_list_cards_dict[self.main_list_selected_index][0]][0].info()

    def render_full_image(self, cinfo):

        cw, ch = self.width // 2, int(self.height * 0.9)
        center_frame = pygame.Rect(cw // 2, (self.height - ch) // 2, cw, ch)
        cimage = cinfo.get_card_image_rendered(center_frame)
        cpos = graphics.get_center_with_surface(cimage, center_frame)

        self.full_image_surface.fill((*Colors.BLACK, 200))
        self.full_image_surface.blit(cimage, cpos)



    def rerender(self):

        self.main_list_selected_index = 0
        self.trunk_selected_index = 0

        self.full_image_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.border_width = int(self.border_frame_margin * self.width)
        self.border_height = int(self.border_frame_margin * self.height)

        self.inner_area = pygame.Rect(self.x + self.border_width, self.y + self.border_height,
                                        self.width - 2*self.border_width, self.height - 2*self.border_height)

        self.main_list_area = self.inner_area.copy()

        if (self.trunk_shown):
            self.main_list_area.width = int((1.0 - self.trunk_width_percentage) * self.main_list_area.width)

        self.trunk_separator_width = int(self.inner_area.width * self.trunk_separator_margin)
        self.trunk_separator_height = self.inner_area.height
        self.trunk_separator_frame_dim = pygame.Rect(0, 0, self.trunk_separator_width, self.trunk_separator_height)
        trunk_x = (self.width if not self.trunk_shown else self.main_list_area.x + int(self.trunk_width_percentage * self.inner_area.width))
        #trunk gets a rect starting at 0, 0, because it has a own surface
        self.trunk_area = pygame.Rect(trunk_x, self.inner_area.y, self.inner_area.width - self.main_list_area.width, self.inner_area.height)

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
        self.label_frame.width = int(self.label_name_width_percentage * self.label_frame.width)
        self.label_frame.height = self.label_height
        self.label_frame = graphics.apply_margins(self.label_frame, 0.05, 0.2)

        #rendering the name
        fsize = graphics.get_fontsize(self.font, [self.shown_group], self.label_frame)
        self.label_text = graphics.render_text(self.font, fsize, self.shown_group, self.group_name_color)
        self.label_pos = graphics.get_center_with_surface(self.label_text, self.label_frame)


        gcards = self.groups[self.shown_group]["cardlist"]

        self.n_cards_main_list = sum(gcards.values())

        self.decksize_frame = pygame.Rect(self.label_frame.width + self.label_frame.x, self.label_frame.y,
                                    int((1.0 - self.label_name_width_percentage) * self.label_frame.width),
                                    self.label_height
                                    )
        self.decksize_frame = graphics.apply_margins(self.decksize_frame, 0.2, 0.2)

        decksize_pages = ["Cards:", str(self.n_cards_main_list)]

        self.mainlist_decksize_rendered = graphics.render_page_from_chars(self.font, decksize_pages, self.decksize_frame,
                                                                            text_color=self.group_name_color,
                                                                            centered=True, vertical_centered=True
                                                                        )


        self.main_list_area.y += self.label_height
        self.main_list_area.height -= self.label_height

        self.recalculate_main_list_positions()
        self.prerender()

    def recalculate_main_list_positions(self):

        #clearing caches#
        self.card_render_cache_main_list = {}
        self.text_render_cache_main_list = {}

        cpl = self.cards_per_line + (self.cards_per_line_added_when_trunk_not_shown if not self.trunk_shown else 0)
        cpc = self.cards_per_column + (self.cards_per_column_added_when_trunk_not_shown if not self.trunk_shown else 0)

        self.main_list_hdist_margin = 0.1
        self.main_list_vdist_margin = 0.1

        self.main_list_hdist = int(self.main_list_area.width * self.main_list_hdist_margin)
        self.main_list_vdist = int(self.main_list_area.height * self.main_list_vdist_margin)

        self.main_list_hseparator = self.main_list_hdist // (cpl + 2)
        self.main_list_vseparator = self.main_list_vdist // (cpc + 2)

        self.main_list_cwdith = (self.main_list_area.width - self.main_list_hdist) // cpl
        self.main_list_cheight = (self.main_list_area.height - self.main_list_vdist) // cpc

        self.gcards = self.groups[self.shown_group]["cardlist"]
        self.main_list_cards = self.sorting_function(self.gcards)

        self.cardnum_margin = 0.2
        #rendering all cards, and adding their position
        self.cardnum_height = int(self.cardnum_margin * self.main_list_cheight)
        self.main_list_card_height = 0
        if self.main_list_view_state == RenderableCardListviewer.SHOW_WITH_AMOUNT:
            self.main_list_card_height = self.main_list_cheight - self.cardnum_height
        elif self.main_list_view_state == RenderableCardListviewer.SHOW_EACH_CARD:
            self.main_list_card_height = self.main_list_cheight

        cx = self.main_list_area.x + self.main_list_hseparator
        cy = self.main_list_area.y + self.main_list_vseparator
        self.main_list_yscroll = 0
        self.main_list_xstart = cx
        self.main_list_ystart = cy

        idx = 0
        count = 0
        card_id_index = 0

        self.main_list_cards_dict = {}
        self.main_list_cards_rects = {}

        for cardclass, amount in self.main_list_cards:

            if self.main_list_view_state == RenderableCardListviewer.SHOW_WITH_AMOUNT:

                rrect = pygame.Rect(cx, cy, self.main_list_cwdith, self.main_list_cheight)

                img_rect = rrect.copy()
                img_rect.height = self.main_list_card_height

                img_text = [f"x{amount}"]

                text_rect = rrect.copy()
                text_rect.y += img_rect.height
                text_rect.height -= img_rect.height

                text_rect = graphics.apply_margins(text_rect, 0.2, 0.2)

                if cy not in self.main_list_cards_rects:
                    self.main_list_cards_rects[cy] = []

                self.main_list_cards_rects[cy].append((card_id_index, idx, img_rect, text_rect))
                self.main_list_cards_dict[card_id_index] = (idx, img_rect, text_rect)

                idx += 1
                card_id_index += 1

                cx += self.main_list_cwdith + self.main_list_hseparator

                if not (idx) % cpl:

                    cx = self.main_list_area.x + self.main_list_hseparator
                    cy += self.main_list_cheight + self.main_list_vseparator

            elif self.main_list_view_state == RenderableCardListviewer.SHOW_EACH_CARD:

                for cardcp in range(amount):

                    rrect = pygame.Rect(cx, cy, self.main_list_cwdith, self.main_list_cheight)

                    img_rect = rrect.copy()
                    img_rect.height = self.main_list_card_height

                    if cy not in self.main_list_cards_rects:
                        self.main_list_cards_rects[cy] = []

                    self.main_list_cards_rects[cy].append((card_id_index, idx, img_rect, None))
                    self.main_list_cards_dict[card_id_index] = (idx, img_rect, None)

                    count += 1
                    card_id_index += 1

                    cx += self.main_list_cwdith + self.main_list_hseparator

                    if not (count) % cpl:

                        cx = self.main_list_area.x + self.main_list_hseparator
                        cy += self.main_list_cheight + self.main_list_vseparator

                idx += 1

        self.n_cards_main_list_shown = card_id_index



    def render_list_with_yscroll(self, img_cache, txt_cache,
                                    render_area, card_dims, actual_card_height,
                                    card_rects, card_list, yscroll):

        cwidth, cheight = card_dims

        for cy in card_rects:

            if cy + cheight + yscroll < render_area.y or\
                cy + yscroll > render_area.y + render_area.height:
                continue

            for id_index, i, img_rect, text_rect in card_rects[cy]:

                cinfo = card_list[i][0].info()



                img = None
                if cinfo.card_image_path in img_cache:
                    img = img_cache[cinfo.card_image_path]
                else:

                    img = graphics.render_image(cinfo.card_image_path)
                    hscale, vscale = 0, 0

                    if cinfo.card_width_to_height_ratio > 1.0:
                        hscale = cwidth
                        vscale = (1.0 / cinfo.card_width_to_height_ratio) * cwidth
                    else:
                        vscale = actual_card_height
                        hscale = cinfo.card_width_to_height_ratio * actual_card_height

                    img = pygame.transform.smoothscale(img, (hscale, vscale))
                    img_cache[cinfo.card_image_path] = img

                rcp = img_rect.copy()
                rcp.y += yscroll
                pos = graphics.get_center_with_surface(img, rcp)

                shadow_rect = pygame.Rect(pos[0], pos[1], img.get_width(), img.get_height())
                shadow_rect.x += int(self.shadow_hoffset_p * shadow_rect.width)
                shadow_rect.y += int(self.shadow_voffset_p * shadow_rect.height)

                shadow_color = ((*Colors.BLACK, self.shadow_alpha) if (id_index != self.main_list_selected_index or self.state != RenderableCardListviewer.MAIN_LIST_FOCUSED)\
                                else (*Colors.YELLOW, self.selected_alpha))

                shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                shadow_surf.fill(shadow_color)

                self.surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))

                if self.main_list_selected_index == id_index and self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:

                    #scaling up selected card
                    img_x_inc, img_y_inc = img.get_width() * 0.1, img.get_height() * 0.1
                    img = pygame.transform.smoothscale(img, (img.get_width() + img_x_inc, img.get_height() + img_y_inc))
                    rcp.x -= img_x_inc // 2
                    rcp.y -= img_y_inc
                    rcp.width += img_x_inc
                    rcp.height += img_y_inc

                    pos = graphics.get_center_with_surface(img, rcp)

                self.surface.blit(img, pos)

                amount = card_list[i][1]

                if self.main_list_view_state == RenderableCardListviewer.SHOW_WITH_AMOUNT:
                    trend = None

                    if amount in txt_cache:
                        trend = txt_cache[amount]
                    else:
                        trend = graphics.render_page_from_chars(self.font, [f"x{amount}"], pygame.Rect(0, 0, text_rect.width, text_rect.height),
                                                                self.description_color, centered=True, vertical_centered=True
                                                                )
                        txt_cache[amount] = trend

                    for surf, pos in trend:
                        self.surface.blit(surf, (pos[0] + text_rect.x, pos[1] + text_rect.y + yscroll))



    def prerender(self):

        self.surface.fill(self.main_list_color)
        self.trunk_surface.fill(self.trunk_list_color)
        self.label_surface.fill(self.label_color)

        self.render_list_with_yscroll(self.card_render_cache_main_list, self.text_render_cache_main_list,
                                        self.main_list_area, (self.main_list_cwdith, self.main_list_cheight),
                                        self.main_list_card_height, self.main_list_cards_rects,
                                        self.main_list_cards, self.main_list_yscroll
                                        )

        if self.trunk_shown:
            #drawing separator
            pygame.draw.rect(self.trunk_surface, self.trunk_separator_color, self.trunk_separator_frame_dim)
            self.surface.blit(self.trunk_surface, (self.trunk_area.x, self.trunk_area.y))

        for rect, color in self.border_lines:
            pygame.draw.rect(self.surface, color, rect)

        self.surface.blit(self.label_surface, self.label_surface_pos)
        self.surface.blit(self.label_text, self.label_pos)
        for surf, pos in self.mainlist_decksize_rendered:
            self.surface.blit(surf, pos)

        if self.state == RenderableCardListviewer.FULL_IMAGE_SHOWN_MAIN_LIST\
            or self.state == RenderableCardListviewer.FULL_IMAGE_SHOWN_TRUNK:

            self.surface.blit(self.full_image_surface, (0, 0))



    def render(self, screen):
        self.prerender()
        screen.blit(self.surface, (self.x, self.y))


    def get_surfaces(self):
        return [self.surface]

    def get_surfaces_with_position(self):
        return [(self.surface, (self.x, self.y))]
