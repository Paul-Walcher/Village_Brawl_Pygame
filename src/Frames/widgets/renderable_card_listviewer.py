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
    FrameDataID,
    R_ID,
    MENU_BUTTON_UNFOCUSED_IMAGE,
    MENU_BUTTON_FOCUSED_IMAGE
)
import graphics
from clock import Clock
from modules import Modules
import constants
from event_queue_manager import Event
from copy import deepcopy


class RenderableCardListviewer(Frame):

    IS_COPYLIST_KEY = "is_copylist"
    MUTABLE_KEY = "mutable"
    CARDLIST_KEY = "cardlist"

    FULL_CARDLIST_NAME = "Full Cardlist"

    NOTHING_FOCUSED = R_ID() #nothing is focused
    MAIN_LIST_FOCUSED = R_ID() #the cards in the list are focused
    MENU_BAR_FOCUSED = R_ID() #the menu bar is focused
    MENU_BUTTON_FOCUSED = R_ID() #menu button in the menu label
    DROPDOWN_MENU_FOCUSED = R_ID() #means the dropdown menu is shown
    SEARCHBAR_FOCUSED = R_ID() #the textinput is focused
    GROUP_SELECTION = R_ID() #displays the groups available (Should show if a group is a copy group or not)
    FULL_IMAGE_SHOWN = R_ID() #if the main list is focused, the selected image is shown on fullscreen

    #animation states
    MOVING_ONE_ROW_UP = R_ID()
    MOVING_ONE_ROW_DOWN = R_ID()
    MOVING_ALL_ROWS_UP = R_ID()
    #view states
    SHOW_WITH_AMOUNT = R_ID()
    SHOW_EACH_CARD = R_ID()

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
                frame_dim,  #frame dimension, into which it is rendered into
                full_cardlist, #a dictionary of {RenderableCard(Class): amount}
                groups,  #must include at least one group. is {name: {"cardlist": {renderable_card: amount}, "mutable": (False/True), "is_copylist": (False/True)}}
                shown_group=None, #the name of the first shown group, must be the name of a group or None

                font=Fonts.MINECRAFT,
                max_group_number=25, #maximum number of groups allowed, gets enforced on loading in and when trying to create a neww group

                #card dimensions
                cards_per_line=8,
                cards_per_column=4,
                #the sorting function that is employed for all groups, when the groups are shown
                sorting_function=None,
                #determines if while typing the searched up cards should be shown
                search_while_typing=True,
                #what percentage of the height is used of the menu_label, and what percentage of width is used
                menu_label_menu_button_hmargin=0.2,
                menu_label_decksize_text_hmargin=0.2,
                menu_label_vmargin=0.1,
                #distances inside the label, so the text wont be right at the border
                menu_label_inner_hmargin=0.05,
                menu_label_inner_vmargin=0.05,
                menu_label_color=Colors.BLACK,
                menu_label_text_color=Colors.WHITE,
                #alpha of the menu label
                menu_label_alpha=200,
                #margins for the main list
                main_list_hmargin=0.1,
                main_list_vmargin=0.1,
                #how much the cards should be separated, based on the cardlist width and height
                main_list_separator_h_percentage=0.1,
                main_list_separator_v_percentage=0.1,
                #menu label assets
                menu_button_unfocused_image=MENU_BUTTON_UNFOCUSED_IMAGE,
                menu_button_focused_image=MENU_BUTTON_FOCUSED_IMAGE,
                #in which color the group name will be shown
                group_name_color=Colors.WHITE,
                #what percentage of width and height is used for the border
                border_frame_margin=0.02,
                #fill color of the border
                border_frame_color=Colors.DARK_CYAN,
                #the frame outline is drawn once on the outer edge and once in the inner edge
                border_frame_outline_margin = 0.2,
                border_frame_outline_color=Colors.BLACK,
                #background color of the list
                main_list_color=Colors.CYAN,
                #margins for the cards inside the main list
                inner_frame_hmargin=0.1,
                inner_frame_vmargin=0.05,
                #description text shown under a card
                card_text_description_color=Colors.BLACK,
                #either showing with amount or not
                main_list_view_state=None,
                #shadow offsets for the cards
                cardshadow_hoffset_p=0.075,
                cardshadow_voffset_p=0.075,
                cardshadow_alpha=120,
                selected_card_size_increase_percentage=0.05,
                selected_cardshadow_color=Colors.YELLOW,
                selected_cardshadow_alpha=120,
                #margin between timage and any text rendered below
                subtext_margin=0.2,
                #delay between inputs
                key_delay=200,#ms
                rowscrolling_duration=300,#ms when scrolling one row upor down, this is the duration it takes
                rowscrolling_all_duration=500#ms #rowscrolling all rows up
                ):

        if len(groups) == 0:
            raise RuntimeError("You need at least one group")
        if len(groups) > max_group_number:
            raise RuntimeError("Too many groups. Adjust your max_group_size")
        if cards_per_line <= 0 or cards_per_column <= 0:
            raise RuntimeError("cards_per_line and cards_per_column have to be greater than 0")

        super().__init__(FrameEnums.RENDERABLE_CARDLIST_VIEWER_WIDGET, None, frame_dim)

        #deepcopying, to avoid altering the references
        self.full_cardlist = full_cardlist.copy()
        self.groups = deepcopy(groups)
        #adding the trunk group
        self.shown_group = shown_group
        self.group_name_color = group_name_color
        self.max_group_number = max_group_number
        self.sorting_function = (sorting_function if sorting_function is not None else RenderableCardListviewer.SortingFunctions.name_descending)
        self.cards_per_line = cards_per_line
        self.cards_per_column = cards_per_column
        self.font = font
        self.card_text_description_color = card_text_description_color
        self.search_while_typing = search_while_typing

        self.menu_label_vmargin = menu_label_vmargin
        self.menu_label_inner_hmargin = menu_label_inner_hmargin
        self.menu_label_inner_vmargin = menu_label_vmargin
        self.menu_label_menu_button_hmargin = menu_label_menu_button_hmargin
        self.menu_label_decksize_text_hmargin = menu_label_decksize_text_hmargin
        self.menu_label_color = menu_label_color
        self.menu_label_text_color = menu_label_text_color
        self.menu_label_alpha = menu_label_alpha
        self.menu_button_unfocused_image = menu_button_unfocused_image
        self.menu_button_focused_image = menu_button_focused_image

        self.main_list_hmargin = main_list_hmargin
        self.main_list_vmargin = main_list_vmargin
        #how much the cards should be separated, based on the cardlist width and height
        self.main_list_separator_h_percentage = main_list_separator_h_percentage
        self.main_list_separator_v_percentage = main_list_separator_v_percentage

        self.border_frame_margin = border_frame_margin
        self.border_frame_color = border_frame_color
        self.border_frame_outline_margin = border_frame_outline_margin
        self.border_frame_outline_color = border_frame_outline_color

        self.main_list_color = main_list_color

        self.inner_frame_hmargin = inner_frame_hmargin
        self.inner_frame_vmargin = inner_frame_vmargin

        self.cardshadow_hoffset_p = cardshadow_hoffset_p
        self.cardshadow_voffset_p = cardshadow_voffset_p
        self.cardshadow_alpha = cardshadow_alpha

        #margin for the distance between the card image and any text rendered below
        self.subtext_margin = subtext_margin
        #current view state
        self.main_list_view_state = (main_list_view_state if main_list_view_state is not None else RenderableCardListviewer.SHOW_EACH_CARD)

        #index of the selected card
        self.selected_card_index = 0
        #setting the state of the widget
        self.state = RenderableCardListviewer.NOTHING_FOCUSED
        #saved scroll amount
        self.main_list_yscroll = 0
        #cache for rendering cards
        self.card_render_cache = {}
        self.text_render_cache = {}
        #dictionary of the main list cards
        self.main_list_cards_dict = {}
        #rectangles, where each y value is associated with: (index inside the main list, idndex for self.main_list_cards, image_rect, subtext_rect)
        self.main_list_cards_rects = {}
        #for remembering what was rendered
        self.rendered_rows = []
        #the list of the currently loaded cards of the group, loaded as [(cardclass, amount)],
        #where the cards will be rendered from front to back
        self.main_list_cards = []
        #the percentage of the sizeincrease when a card is in the selected state
        self.selected_card_size_increase_percentage = selected_card_size_increase_percentage
        self.selected_cardshadow_color = selected_cardshadow_color
        self.selected_cardshadow_alpha = selected_cardshadow_alpha
        #the surface onto which everything will be rendered
        self.surface = None
        #the surface, which will be shown when a images full image is required
        self.full_image_surface = None
        #menu label
        self.menu_label_surface = None
        self.menu_label_height = -1
        #dimensions of the menu label
        self.menu_label_frame = None
        #frame with the distances to the edges calculated in
        self.inner_menu_label_frame = None
        #frames for the menu label
        self.menu_button_frame = None
        self.deckname_frame = None
        self.decksize_frame = None
        #the main list frame for the cardlist
        self.main_list_frame = None
        #rendered items
        self.menu_button_unfocused_image_rendered = None
        self.menu_button_unfocused_image_rendered_pos = None
        self.menu_button_focused_image_rendered = None
        self.menu_button_focused_image_rendered_pos = None
        #deckname surface and positions
        self.deckname_rendered_and_positions = None
        #decksize text and positions
        self.decksize_rendered_and_positions = None

        #frame after applying the margins
        self.inner_main_list_frame = None
        #full width and height of the separator area
        self.main_list_hseparator_width = -1
        self.main_list_vseparator_height = -1
        #actual distance between cards
        self.main_list_hseparator_size = -1
        self.main_list_vseparator_size = -1
        #cardwidth and height when rendered to the list
        self.main_list_cwdith = -1
        self.main_list_cheight = -1
        #subtext height is the height of the subtext,
        #cardimage_height the height of the card.
        #same for subtext width and cardimage height
        self.subtext_width = -1
        self.subtext_height = -1
        self.cardimage_width = -1
        self.cardimage_height = -1
        #scroll variable
        self.main_list_yscroll = 0
        #and copy
        self.main_list_yscroll_copy = 0
        #the amount of visible cards in the list
        self.n_cards_shown = 0

        #additional render variables
        #actual border with and height
        self.border_width = -1
        self.border_height = -1
        #border outline width and height
        self.border_outline_width = -1
        self.border_outline_height = -1
        self.used_border_outline_size = -1
        #the corners for the rectangle for the inner outline
        self.inner_border_corners = []
        #border lines are the  rectangles to be drawn to render the boarder
        self.border_lines = []
        #the inner area is the frame inside without the border, a pygame.Rect
        self.inner_area = None
        #the frame of the main list, where the cards are shown
        self.cardlist_frame = None
        #adding the full cardlist
        self.groups[RenderableCardListviewer.FULL_CARDLIST_NAME] = {RenderableCardListviewer.CARDLIST_KEY: self.full_cardlist,
                                                                    RenderableCardListviewer.MUTABLE_KEY: False,
                                                                    RenderableCardListviewer.IS_COPYLIST_KEY: True}
        self.shown_group = (shown_group if shown_group is not None else list(self.groups.keys())[0])

        #key clock for all key triggers
        self.key_clock = Clock()
        self.key_delay = key_delay

        #rowscrolling clock
        self.rowscrolling_clock = Clock()
        self.rowscrolling_duration = rowscrolling_duration
        self.rowscrolling_all_duration = rowscrolling_all_duration

        self.key_clock.start()
        self.rerender()

    def rerender(self):

        #resetting card index
        self.selected_card_index = 0
        #creating the full image surface
        self.full_image_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        #getting border width and height
        self.border_width = int(self.border_frame_margin * self.width)
        self.border_height = int(self.border_frame_margin * self.height)
        #the inner area is the frame inside without the border
        self.inner_area = pygame.Rect(self.x + self.border_width, self.y + self.border_height,
                                        self.width - 2*self.border_width, self.height - 2*self.border_height)
        #creating the own surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        #calculating actual border outline sizes
        self.border_outline_width = int(self.border_width * self.border_frame_outline_margin)
        self.border_outline_height = int(self.border_height * self.border_frame_outline_margin)
        #selecting
        self.used_border_outline_size = min(self.border_outline_width, self.border_outline_height)
        #the inner border corners
        self.inner_border_corners = [
                                    (self.border_width-self.used_border_outline_size, self.border_height - self.used_border_outline_size),
                                    (self.width - self.border_width, self.border_height - self.used_border_outline_size),
                                    (self.width - self.border_width, self.height - self.border_height + self.used_border_outline_size),
                                    (self.border_width - self.used_border_outline_size, self.height - self.border_height)
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

                                #inner outline will be calculated
                            ]

        #helper function, connects the inner border corners
        def rs(p1, p2):

            x = p1[0]
            y = p1[1]

            w = p2[0] - p1[0]
            if w == 0:
                w = self.used_border_outline_size

            h = p2[1] - p1[1]
            if h == 0:
                h = self.used_border_outline_size

            if w < 0 or h < 0:

                x = p2[0]
                y = p2[1]

                w = p1[0] - p2[0]
                if w == 0:
                    w = self.used_border_outline_size

                h = p1[1] - p2[1]
                if h == 0:
                    h = self.used_border_outline_size


            return pygame.Rect(x, y, w, h)

        for i in range(len(self.inner_border_corners)+1):

            i1 = i % len(self.inner_border_corners)
            i2 = (i+1) % len(self.inner_border_corners)

            p1, p2 = self.inner_border_corners[i1], self.inner_border_corners[i2]

            self.border_lines.append((rs(p1, p2), self.border_frame_outline_color))

        #rendering the Name Label
        self.menu_label_height = int(self.inner_area.height * self.menu_label_vmargin)
        self.menu_label_surface = pygame.Surface((self.inner_area.width, self.menu_label_height), pygame.SRCALPHA)
        self.menu_label_surface_pos = (self.inner_area.x, self.inner_area.y)
        #calculating menu label dimensions
        self.menu_label_frame = self.inner_area.copy()
        self.menu_label_frame.height = self.menu_label_height
        #inner menu label is the label after applying the margins
        self.inner_menu_label_frame = self.menu_label_frame.copy()
        self.inner_menu_label_frame = graphics.apply_margins(self.inner_menu_label_frame, self.menu_label_inner_hmargin, self.menu_label_inner_vmargin)


        """
        -----------------------------------------
        MENU LABEL WIDGETS
        -----------------------------------------
        """

        #now calculating the menu options
        self.menu_button_frame, self.deckname_frame, self.decksize_frame = graphics.split_rect_horizontally(pygame.Rect(0, 0, self.inner_menu_label_frame.width, self.inner_menu_label_frame.height),
                                                                                                        [self.menu_label_menu_button_hmargin,
                                                                                                        1.0-(self.menu_label_menu_button_hmargin + self.menu_label_decksize_text_hmargin),
                                                                                                        self.menu_label_decksize_text_hmargin
                                                                                                        ]
                                                                                                        )
        self.menu_button_frame = graphics.apply_margins(self.menu_button_frame, self.menu_label_inner_hmargin, self.menu_label_inner_vmargin)
        self.deckname_frame = graphics.apply_margins(self.deckname_frame, self.menu_label_inner_hmargin, self.menu_label_inner_vmargin)
        self.decksize_frame = graphics.apply_margins(self.decksize_frame, self.menu_label_inner_hmargin, self.menu_label_inner_vmargin)
        #now rendering the menu items
        #rendering the menu button
        self.menu_button_unfocused_image_rendered,\
        self.menu_button_unfocused_image_rendered_pos = graphics.img_load_and_position(self.menu_button_unfocused_image, self.menu_button_frame)
        self.menu_button_focused_image_rendered,\
        self.menu_button_focused_image_rendered_pos = graphics.img_load_and_position(self.menu_button_focused_image, self.menu_button_frame)
        #rendering the name
        self.deckname_rendered_and_positions = graphics.render_page_from_chars_color(
                                                                                        font=self.font,
                                                                                        page=[[(self.shown_group, self.menu_label_text_color)]],
                                                                                        frame=self.deckname_frame,
                                                                                        text_color=self.menu_label_text_color,
                                                                                        centered=True,
                                                                                        vertical_centered=True
                                                                                    )
        #rendering the decksize
        self.decksize_rendered_and_positions = graphics.render_page_from_chars_color(
                                                                                        font=self.font,
                                                                                        page=[
                                                                                            [("Decksize:", self.menu_label_text_color)],
                                                                                            [(str(self.get_shown_group_decksize()), self.menu_label_text_color)]
                                                                                        ],
                                                                                        frame=self.decksize_frame,
                                                                                        text_color=self.menu_label_text_color,
                                                                                        centered=True,
                                                                                        vertical_centered=True
                                                                                    )

        """
        -----------------------------------------
        CARD POSITION CALCULATIONS
        -----------------------------------------
        """

        #getting the inner area for the cardlist
        self.main_list_frame = self.inner_area.copy()

        self.main_list_frame.y += self.menu_label_frame.height
        self.main_list_frame.height -= self.menu_label_frame.height

        #getting the inner main list
        self.inner_main_list_frame = graphics.apply_margins(self.main_list_frame, self.main_list_hmargin, self.main_list_vmargin)

        #now getting the card positions
        self.recalculate_main_list_positions()
        #prerendering
        self.prerender()

    #gets the size of the currently shown deck
    def get_shown_group_decksize(self):
        return sum(self.groups[self.shown_group][RenderableCardListviewer.CARDLIST_KEY].values())


    def recalculate_main_list_positions(self):

        #clearing caches#
        self.card_render_cache = {}
        self.text_render_cache = {}

        #getting the separator width
        self.main_list_hseparator_width = int(self.inner_main_list_frame.width * self.main_list_separator_h_percentage)
        self.main_list_vseparator_height = int(self.inner_main_list_frame.height * self.main_list_separator_v_percentage)
        #getting the remaining width
        self.main_list_hseparator_size =  (self.main_list_hseparator_width // (self.cards_per_line-1) if self.cards_per_line > 1 else 0)
        self.main_list_vseparator_size = (self.main_list_vseparator_height // (self.cards_per_column-1) if self.cards_per_column > 1 else 0)
        #calculating the shown cardsizes
        self.main_list_cwidth = (self.inner_main_list_frame.width - self.main_list_hseparator_width) // self.cards_per_line
        self.main_list_cheight = (self.inner_main_list_frame.height - self.main_list_vseparator_height) // self.cards_per_column

        gcards = self.groups[self.shown_group][RenderableCardListviewer.CARDLIST_KEY]
        self.main_list_cards = self.sorting_function(gcards)

        #rendering all cards, and adding their position
        self.subtext_width = 0
        self.subtext_height = 0
        self.cardimage_width = 0
        self.cardimage_height = 0
        self.main_list_card_height = 0

        if self.main_list_view_state == RenderableCardListviewer.SHOW_WITH_AMOUNT:
            self.subtext_width = self.main_list_cwidth
            self.subtext_height = int(self.main_list_cheight * self.subtext_margin)
            self.cardimage_width = self.main_list_cwidth
            self.cardimage_height = self.main_list_cheight - self.subtext_height
        else:
            self.subtext_width = 0
            self.subtext_height = 0
            self.cardimage_width = self.main_list_cwidth
            self.cardimage_height = self.main_list_cheight


        cx = self.inner_main_list_frame.x + (self.inner_main_list_frame.width // 2 - self.main_list_cwidth // 2 if self.cards_per_line == 1 else 0)
        cy = self.inner_main_list_frame.y + (self.inner_main_list_frame.height // 2 - self.main_list_cheight // 2 if self.cards_per_column == 1 else 0)

        self.main_list_yscroll = 0

        main_list_cards_index = 0
        count = 0
        card_id_index = 0

        self.main_list_cards_dict = {}
        self.main_list_cards_rects = {}

        for cardclass, amount in self.main_list_cards:

            if self.main_list_view_state == RenderableCardListviewer.SHOW_WITH_AMOUNT:

                img_rect = pygame.Rect(cx, cy, self.cardimage_width, self.cardimage_height)
                text_rect = pygame.Rect(cx, cy + self.cardimage_height, self.subtext_width, self.subtext_height)

                if cy not in self.main_list_cards_rects:
                    self.main_list_cards_rects[cy] = []

                self.main_list_cards_rects[cy].append((card_id_index, main_list_cards_index, img_rect, text_rect))
                self.main_list_cards_dict[card_id_index] = (main_list_cards_index, img_rect, text_rect)

                main_list_cards_index += 1
                card_id_index += 1

                cx += self.main_list_cwidth + self.main_list_hseparator_size

                if not (card_id_index) % self.cards_per_line:

                    cx = self.inner_main_list_frame.x + (self.inner_main_list_frame.width // 2 - self.main_list_cwidth // 2 if self.cards_per_line == 1 else 0)
                    cy += self.main_list_cheight + self.main_list_vseparator_size

            elif self.main_list_view_state == RenderableCardListviewer.SHOW_EACH_CARD:

                for cardcp in range(amount):

                    img_rect = pygame.Rect(cx, cy, self.cardimage_width, self.cardimage_height)
                    text_rect = pygame.Rect(cx, cy + self.cardimage_height, self.subtext_width, self.subtext_height)

                    if cy not in self.main_list_cards_rects:
                        self.main_list_cards_rects[cy] = []

                    self.main_list_cards_rects[cy].append((card_id_index, main_list_cards_index, img_rect, text_rect))
                    self.main_list_cards_dict[card_id_index] = (main_list_cards_index, img_rect, text_rect)

                    card_id_index += 1

                    cx += self.main_list_cwidth + self.main_list_hseparator_size

                    if not (card_id_index) % self.cards_per_line:

                        cx = self.inner_main_list_frame.x + (self.inner_main_list_frame.width // 2 - self.main_list_cwidth // 2 if self.cards_per_line == 1 else 0)
                        cy += self.main_list_cheight + self.main_list_vseparator_size

                main_list_cards_index += 1

        self.n_cards_shown = card_id_index

    """
    Renders the cardlist
    """

    def render_list_with_yscroll(self):

        self.rendered_rows = []

        for cy in self.main_list_cards_rects:

            if cy + self.main_list_cheight + self.main_list_yscroll < self.inner_main_list_frame.y or\
                cy + self.main_list_yscroll > self.inner_main_list_frame.y + self.inner_main_list_frame.height:
                continue


            for id_index, main_list_cards_idx, img_rect, text_rect in self.main_list_cards_rects[cy]:


                self.rendered_rows.append((cy, id_index, main_list_cards_idx, img_rect, text_rect))
                cinfo = self.main_list_cards[main_list_cards_idx][0].info()

                img, img_pos = None, None
                if cinfo.card_image_path in self.card_render_cache:
                    img, img_pos = self.card_render_cache[cinfo.card_image_path]
                else:

                    img, img_pos = graphics.img_load_and_position(cinfo.card_image_path, pygame.Rect(0, 0, img_rect.width, img_rect.height))
                    self.card_render_cache[cinfo.card_image_path] = (img, img_pos)

                img_render_pos = (img_rect.x + img_pos[0], img_rect.y + img_pos[1] + self.main_list_yscroll)

                shadow_rect = None


                if self.selected_card_index == id_index and self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:

                    #scaling up selected card
                    img_x_inc, img_y_inc = img.get_width() * 0.1, img.get_height() * 0.1
                    img = pygame.transform.smoothscale(img, (img.get_width() + img_x_inc, img.get_height() + img_y_inc))
                    img_render_pos = (img_render_pos[0]  - img_x_inc // 2, img_render_pos[1] - img_y_inc // 2)

                shadow_rect = pygame.Rect(img_render_pos[0], img_render_pos[1], img.get_width(), img.get_height())
                shadow_rect.x += int(self.cardshadow_hoffset_p * shadow_rect.width)
                shadow_rect.y += int(self.cardshadow_voffset_p * shadow_rect.height)

                shadow_color = ((*Colors.BLACK, self.cardshadow_alpha) if (id_index != self.selected_card_index or self.state != RenderableCardListviewer.MAIN_LIST_FOCUSED)\
                                else (*Colors.YELLOW, self.selected_cardshadow_alpha))

                shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                shadow_surf.fill(shadow_color)

                self.surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
                self.surface.blit(img, img_render_pos)

                amount = self.main_list_cards[main_list_cards_idx][1]

                if self.main_list_view_state == RenderableCardListviewer.SHOW_WITH_AMOUNT:

                    trend = None

                    if amount in self.text_render_cache:
                        trend = self.text_render_cache[amount]
                    else:
                        trend = graphics.render_page_from_chars(self.font, [f"x{amount}"], pygame.Rect(0, 0, text_rect.width, text_rect.height),
                                                                self.card_text_description_color, centered=True, vertical_centered=True
                                                                )
                        self.text_render_cache[amount] = trend

                    for surf, pos in trend:
                        self.surface.blit(surf, (pos[0] + text_rect.x, pos[1] + text_rect.y + self.main_list_yscroll))

        #finally sort the l
        self.rendered_rows.sort(key=lambda cy: cy[0])

    def prerender(self):
        #prerendering

        self.surface.fill(self.main_list_color)
        self.menu_label_surface.fill(self.menu_label_color)
        #rendering visible cards
        self.render_list_with_yscroll()

        for rect, color in self.border_lines:
            pygame.draw.rect(self.surface, color, rect)

        #widgets
        #button
        button_img = (self.menu_button_focused_image_rendered if self.state == RenderableCardListviewer.MENU_BUTTON_FOCUSED else self.menu_button_unfocused_image_rendered)
        button_pos = (self.menu_button_focused_image_rendered_pos if self.state == RenderableCardListviewer.MENU_BUTTON_FOCUSED else self.menu_button_unfocused_image_rendered_pos)
        self.menu_label_surface.blit(button_img, self.menu_button_frame)
        #deckname
        for surf, pos in self.deckname_rendered_and_positions:
            self.menu_label_surface.blit(surf, pos)
        for surf, pos in self.decksize_rendered_and_positions:
            self.menu_label_surface.blit(surf, pos)

        #bliting the widgets onto the label
        self.surface.blit(self.menu_label_surface, self.menu_label_surface_pos)


        if self.state == RenderableCardListviewer.FULL_IMAGE_SHOWN:
            self.surface.blit(self.full_image_surface, (0, 0))

    def render(self, screen):
        self.prerender()
        screen.blit(self.surface, (self.x, self.y))

    def render_full_image(self, cinfo):

        cw, ch = self.width // 2, int(self.height * 0.9)
        center_frame = pygame.Rect(cw // 2, (self.height - ch) // 2, cw, ch)
        cimage = cinfo.get_card_image_rendered(center_frame)
        cpos = graphics.get_center_with_surface(cimage, center_frame)

        self.full_image_surface.fill((*Colors.BLACK, 200))
        self.full_image_surface.blit(cimage, cpos)


    def tick(self):
        self.manage_pygame_events()

        #non input accepting states
        if self.state == RenderableCardListviewer.MOVING_ONE_ROW_UP:
            self.move_one_row_up()
        elif self.state == RenderableCardListviewer.MOVING_ONE_ROW_DOWN:
            self.move_one_row_down()
        elif self.state == RenderableCardListviewer.MOVING_ALL_ROWS_UP:
            self.move_all_rows_up()
        else:
            #accept inputs

            if self.key_clock.elapsed() > self.key_delay:

                if self.key_pressed(pygame.K_LEFT) or self.key_pressed(KeyAlternatives.LEFT_ALTERNATIVE):
                    self.left_pressed()
                    self.key_clock.start()

                if self.key_pressed(pygame.K_RIGHT) or self.key_pressed(KeyAlternatives.RIGHT_ALTERNATIVE):
                    self.right_pressed()
                    self.key_clock.start()

                if self.key_pressed(pygame.K_UP) or self.key_pressed(KeyAlternatives.UP_ALTERNATIVE):
                    self.up_pressed()
                    self.key_clock.start()

                if self.key_pressed(pygame.K_DOWN) or self.key_pressed(KeyAlternatives.DOWN_ALTERNATIVE):
                    self.down_pressed()
                    self.key_clock.start()
    """
    INTERACTION FUNCTIONS
    """

    def left_pressed(self):

        if self.state == RenderableCardListviewer.NOTHING_FOCUSED:
            self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED
            self.selected_card_index = 0
        elif self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:
            #if we're at the leftmost state, leave the main list focus
            if (self.selected_card_index % self.cards_per_line) == 0:
                self.state = RenderableCardListviewer.NOTHING_FOCUSED
            else:
                self.selected_card_index -= 1

    def right_pressed(self):

        if self.state == RenderableCardListviewer.NOTHING_FOCUSED:
            self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED
            self.selected_card_index = 0
        elif self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:
            #if we're at the rightmost state, leave the main list focus
            if ((self.selected_card_index + 1) % self.cards_per_line) == 0:
                self.state = RenderableCardListviewer.NOTHING_FOCUSED
            else:
                self.selected_card_index += 1

    def up_pressed(self):

        if self.state == RenderableCardListviewer.NOTHING_FOCUSED:
            self.state = RenderableCardListviewer.MENU_BAR_FOCUSED
        elif self.state == RenderableCardListviewer.MENU_BAR_FOCUSED:
            self.state = RenderableCardListviewer.NOTHING_FOCUSED
        elif self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:
            #check for going off, and if the index is in rendered rows
            if self.selected_card_index < self.cards_per_line:
                self.state = RenderableCardListviewer.MENU_BAR_FOCUSED
            elif (self.selected_card_index - self.cards_per_line) not in [x[1] for x in self.rendered_rows]:
                self.state = RenderableCardListviewer.MOVING_ONE_ROW_UP
                self.initialize_move_one_row_up()
            else:
                self.selected_card_index -= self.cards_per_line

    def down_pressed(self):

        if self.state == RenderableCardListviewer.NOTHING_FOCUSED:
            self.state = RenderableCardListviewer.MENU_BAR_FOCUSED
        elif self.state == RenderableCardListviewer.MENU_BAR_FOCUSED:
            self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED
            self.selected_card_index = 0
            self.main_list_yscroll = 0
        elif self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:
            #check for going off, and if the index is in rendered rows
            if self.selected_card_index > (self.n_cards_shown - self.cards_per_line):
                self.selected_card_index += self.cards_per_line
                self.selected_card_index %= (self.n_cards_shown)
                self.selected_card_index -= (self.cards_per_line - self.n_cards_shown % self.cards_per_line)
                if self.selected_card_index < self.cards_per_line:
                    self.state = RenderableCardListviewer.MOVING_ALL_ROWS_UP
                    self.initialize_move_all_rows_up()
            elif len(self.rendered_rows) < (self.cards_per_line * self.cards_per_column):
                self.selected_card_index += self.cards_per_line
                self.selected_card_index %= self.n_cards_shown
            elif (self.selected_card_index + self.cards_per_line) not in [x[1] for x in self.rendered_rows]:

                self.state = RenderableCardListviewer.MOVING_ONE_ROW_DOWN
                self.initialize_move_one_row_down()
            else:
                self.selected_card_index += self.cards_per_line

    #animation functions
    def initialize_move_one_row_up(self):

        #starting up
        self.main_list_yscroll_copy = self.main_list_yscroll
        #starting the clock
        self.rowscrolling_clock.start()

    def move_one_row_up(self):

        #getting the percentage moved
        percentage = self.rowscrolling_clock.elapsed() / self.rowscrolling_duration

        scroll_amount = self.main_list_cheight + self.main_list_vseparator_size

        if percentage >= 1.0:
            self.finalize_move_one_row_up()
        else:

            self.main_list_yscroll = self.main_list_yscroll_copy + int(percentage * scroll_amount)

    def finalize_move_one_row_up(self):

        self.main_list_yscroll = self.main_list_yscroll_copy + self.main_list_cheight  + self.main_list_vseparator_size
        self.main_list_yscroll_copy = 0

        self.selected_card_index -= self.cards_per_line

        self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED


    #move down
    def initialize_move_one_row_down(self):

        #starting up
        self.main_list_yscroll_copy = self.main_list_yscroll
        #starting the clock
        self.rowscrolling_clock.start()

    def move_one_row_down(self):

        #getting the percentage moved
        percentage = self.rowscrolling_clock.elapsed() / self.rowscrolling_duration

        scroll_amount = self.main_list_cheight + self.main_list_vseparator_size

        if percentage >= 1.0:
            self.finalize_move_one_row_down()
        else:

            self.main_list_yscroll = self.main_list_yscroll_copy - int(percentage * scroll_amount)

    def finalize_move_one_row_down(self):

        self.main_list_yscroll = self.main_list_yscroll_copy - self.main_list_cheight - self.main_list_vseparator_size
        self.main_list_yscroll_copy = 0

        self.selected_card_index += self.cards_per_line

        self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED

    #moving all rows up
    def initialize_move_all_rows_up(self):

        #starting up
        self.main_list_yscroll_copy = self.main_list_yscroll
        #starting the clock
        self.rowscrolling_clock.start()

    def move_all_rows_up(self):

        #getting the percentage moved
        percentage = self.rowscrolling_clock.elapsed() / self.rowscrolling_all_duration

        if percentage >= 1.0:
            self.finalize_move_all_rows_up()
        else:

            self.main_list_yscroll = int((1.0 - percentage) * self.main_list_yscroll_copy)

    def finalize_move_all_rows_up(self):

        self.main_list_yscroll = 0
        self.main_list_yscroll_copy = 0

        self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED
