import os
import pygame
import threading
import random

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import (
    fequal,
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

#widgets
from Frames.widgets.text_input import TextInput
from Frames.widgets.dropdown_menu import DropdownMenu
from Frames.widgets.expandable_dropdown_menu import ExpandableDropdownMenu
from Frames.widgets.scrollable_dropdown_menu import ScrollableDropdownMenu


#TODO
#
#1.) Create detection and state for long enter pressed | DONE
#2.) Create Card animation when card clicked | DONE
#--------------------------------------------------------------
#3.) Add Card state to main list (preview, normal)
#4.) Create Info shown frame when card clicked
#5.) Create card amount increase/decrease when card selected via long enter pressed
#6.) Create search menu

class RenderableCardListviewer(Frame):

    IS_COPYLIST_KEY = "is_copylist"
    MUTABLE_KEY = "mutable"
    RENAMABLE_KEY = "renamable" #if the group is renamable or not
    CARDLIST_KEY = "cardlist"

    FULL_CARDLIST_NAME = "Full Cardlist"
    #info text colors
    INFO_TEXT_STANDARD_COLOR = Colors.BLACK
    INFO_TEXT_WARNING_COLOR = Colors.YELLOW
    INFO_TEXT_ERROR_COLOR = Colors.RED
    #Fading durations for the info text
    RENAMING_NOT_POSSIBLE_FADING_DURATION = 5000#ms
    RENAMING_NOT_POSSIBLE_INFO_TEXT = "Renaming for this group is disabled"
    #deckname exists error
    DECKNAME_ALREADY_EXISTS_ERROR_FADING_DURATION = 5000#ms
    DECKNAME_ALREADY_EXISTS_ERROR_INFO_TEXT = "The chosen Deck name already exists"


    NOTHING_FOCUSED = R_ID() #nothing is focused
    MAIN_LIST_FOCUSED = R_ID() #the cards in the list are focused
    MENU_BUTTON_FOCUSED = R_ID() #menu button in the menu label
    MENU_DECKNAME_FOCUSED = R_ID()
    MENU_DECKSIZE_FOCUSED = R_ID()
    DROPDOWN_MENU_FOCUSED = R_ID() #means the dropdown menu is shown
    SEARCHBAR_FOCUSED = R_ID() #the textinput is focused
    GROUP_SELECTION = R_ID() #displays the groups available (Should show if a group is a copy group or not)
    FULL_IMAGE_SHOWN = R_ID() #if the main list is focused, the selected image is shown on fullscreen
    DROPDOWN_MENU_ACTIVE = R_ID()
    #enter states
    ENTER_PRESSED = R_ID()
    CARD_SNAPBACK_ANIMATION = R_ID() #if a card was pressed, it needs to animate back into its original state

    INITIALIZE_DECK_RENAMING_FRAME = R_ID()
    DECK_RENAMING_FRAME_ACTIVE = R_ID()

    INITIALIZE_MENU_FRAME = R_ID()
    MENU_FRAME_ACTIVE = R_ID()

    #Group Creation states
    INITIALIZE_DECK_CREATION_FRAME = R_ID()
    DECK_CREATION_FRAME_ACTIVE = R_ID()

    #animation states
    MOVING_ONE_ROW_UP = R_ID()
    MOVING_ONE_ROW_DOWN = R_ID()
    MOVING_ALL_ROWS_UP = R_ID()

    DECKNAME_SELECTED_ANIMATION = R_ID()
    MENU_BUTTON_SELECTED_ANIMATION = R_ID()

    #view states
    SHOW_WITH_AMOUNT = R_ID()
    SHOW_EACH_CARD = R_ID()

    class MENU_OPTIONS:

        @staticmethod
        def get_option_from_traceback(traceback):
            return traceback[-1]

        SHOWN_AMOUNT = 5

        #sorting
        SORTING_OPTION_KEY = ("Sort Group",)
        #suboptions
        RANDOMIZED_SORTING = ("Randomized",)
        NAME_DESCENDING_SORTING = ("Name Descending",)
        NAME_ASCENDING_SORTING = ("Name Ascending",)
        AMOUNT_DESCENDING_SORTING = ("Amount Descending",)
        AMOUNT_ASCENDING_SORTING = ("Amount Ascending",)
        #shown_amount
        SORTING_OPTIONS_SHOWN_AMOUNT = 5

        #display type
        DISPLAY_TYPE_KEY = ("Display Type",)
        #options for display type
        SHOW_EACH_CARD_DISPLAY_TYPE = ("Show Each Card",)
        SHOW_WITH_AMOUNT_DISPLAY_TYPE = ("Show With Amount",)
        #shown amount
        DISPLAY_OPTIONS_SHOWN_AMOUNT = 5

        #group selection
        SELECT_GROUP_OPTION_KEY = ("Select Deck",)
        SELECT_GROUP_OPTIONS_SHOWN_AMOUNT = 5
        #group creation
        CREATE_GROUP_OPTION_KEY =("Create Deck",)






    class SortingFunctions:

        """
        Functions to sort cardlists.
        Each cardlist is: [(RenderableCard (Class), amount)]
        """

        @staticmethod
        def no_order(cardlist):
            return cardlist

        @staticmethod
        def randomized(cardlist):
            cardlist_copy = cardlist.copy()
            random.shuffle(cardlist_copy)
            return cardlist_copy

        @staticmethod
        def name_descending(cardlist):

            clist = cardlist.copy()
            clist.sort(key=lambda x: x[0].info().name)
            return clist

        @staticmethod
        def name_ascending(cardlist):

            clist = cardlist.copy()
            clist.sort(key=lambda x: x[0].info().name)
            clist.reverse()
            return clist

        @staticmethod
        def amount_descending(cardlist):

            clist = cardlist.copy()
            clist.sort(key=lambda x: x[1])
            return clist

        @staticmethod
        def amount_ascending(cardlist):

            clist = cardlist.copy()
            clist.sort(key=lambda x: x[1])
            clist.reverse()
            return clist



    #subframes
    class FocusedTextInputFrame(Frame):

        TEXT_ENTERED = R_ID()
        ESCAPE = R_ID()

        def __init__(
                    self,
                    frame_dim,
                    focus_group=""
                    ):

            #initializing
            Frame.__init__(self, FrameEnums.UNDEFINED, None, frame_dim, focus_group=focus_group)

            self.surface = None
            self.text_input = None
            self.text_input_frame = None

            self.background_color = Colors.BLACK
            self.background_alpha = 127

            self.escape_released = False

            #how the frame was exited
            self._exit_type = None

            self.rerender()

        def rerender(self):

            self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            self.text_input_frame = pygame.Rect(0, 0, self.width//2, self.height//20)
            xc, yc = graphics.get_center_with_rect(self.frame_dim, self.text_input_frame)
            self.text_input_frame.x = xc
            self.text_input_frame.y = yc

            self.text_input = TextInput(
                                        self.text_input_frame,
                                        focus_group=self.focus_group
                                        )
            self.text_input.focus()


        def set_input_text(self, text=""):
            self.text_input.set_text(text)

        def get_input_text(self):
            return self.text_input.get_text()

        def bind_events(self):
            self.clear_event_callbacks()

        def reset_exit_type(self):
            self._exit_type = None

        def exit_with_enter(self):
            return (self._exit_type == RenderableCardListviewer.FocusedTextInputFrame.TEXT_ENTERED)

        def exit_with_escape(self):
            return (self._exit_type == RenderableCardListviewer.FocusedTextInputFrame.ESCAPE)

        def tick(self):
            self.manage_pygame_events()
            self.text_input.tick()

            #polling textinput events
            for event in self.text_input.poll_events():
                if event.type == TextInput.EventTypes.ENTER_PRESSED:
                    self._exit_type = RenderableCardListviewer.FocusedTextInputFrame.TEXT_ENTERED
                    self.raise_exit_flag()

            if self.exit_flag_raised():
                return None

            if self.has_focus:
                #checking for any movement key
                if self.key_pressed(pygame.K_LEFT) or self.key_pressed(KeyAlternatives.LEFT_ALTERNATIVE)\
                    or self.key_pressed(pygame.K_RIGHT) or self.key_pressed(KeyAlternatives.RIGHT_ALTERNATIVE)\
                    or self.key_pressed(pygame.K_UP) or self.key_pressed(KeyAlternatives.UP_ALTERNATIVE)\
                    or self.key_pressed(pygame.K_DOWN) or self.key_pressed(KeyAlternatives.DOWN_ALTERNATIVE):

                    self.text_input.focus()

                if (self.key_pressed(KeyAlternatives.BACK_KEY) or self.key_pressed(pygame.K_ESCAPE)) and self.escape_released:
                    self._exit_type = RenderableCardListviewer.FocusedTextInputFrame.ESCAPE
                    self.raise_exit_flag()

                if not (self.key_pressed(KeyAlternatives.BACK_KEY) and self.key_pressed(pygame.K_ESCAPE)) and not self.escape_released:
                    self.escape_released = True

            if not self.text_input.has_focus and not self.has_focus:
                self.focus()
                self.escape_released = False

            return self

        def render(self, screen):

            self.surface.fill((*self.background_color, self.background_alpha))
            self.text_input.render(self.surface)

            screen.blit(self.surface, (self.x, self.y))

    class MenuFrame(Frame):

        def __init__(
                        self,
                        frame_dim,
                        focus_group="",
                        menu_options=None
                    ):

            #initializing
            Frame.__init__(self, FrameEnums.UNDEFINED, None, frame_dim, focus_group=focus_group)

            self.menu_options = (menu_options if menu_options is not None else {})

            self.surface = None
            self.menu_dropdown = None

            self.rerender()

        def rerender(self):
            pass

        def bind_events(self):
            self.clear_event_callbacks()

        def tick(self):

            self.manage_pygame_events()

            if self.exit_flag_raised():
                return None

        def render(self, screen):
            pass

    def __init__(self,
                frame_dim,  #frame dimension, into which it is rendered into
                full_cardlist, #a dictionary of {RenderableCard(Class): amount}
                groups,  #must include at least one group. is {name: {"cardlist": {renderable_card: amount}, "mutable": (False/True), "is_copylist": (False/True)}}
                special_info_frames=None,   #a dictionary like: {cardclass: (list_of_groups_this_info_frame_will_be_used, instantiated frame)}
                                            #for the card as key, when it is clicked the frame given as value[1] will be used in all groups in value[0] instead of the normal infopage

                #focus group
                focus_group="",
                parent_frame=None,

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
                menu_label_highlighted_color=Colors.YELLOW,
                menu_label_highlighted_alpha=64,
                #full image data
                full_image_background_color=Colors.BLACK,
                full_image_background_alpha=180,
                cardtext_hmargin=0.2,
                cardtext_vmargin=0.2,
                #distances inside the label, so the text wont be right at the border
                menu_label_inner_hmargin=0.1,
                menu_label_inner_vmargin=0.1,
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
                #info text specifications
                info_text_hlen_p = 0.3,#horizontal length percentage
                info_text_vlen_p = 0.15,#vertical length percentage
                info_text_surface_alpha=192,
                info_text_color = None,
                info_text_warning_color=None,
                info_text_error_color=None,
                #dropdown menu
                dropdown_menu_hlen_p=0.5,
                dropdown_menu_vlen_p=0.4,
                #group menu stuff
                group_selection_enabled=True,
                group_creation_enabled=True,
                #enter states
                time_until_long_enter_pressed=500,#ms, how long until the long enter state is reached
                #percentage when card is selected
                card_pressed_size_change_percentage=0.25,
                #delay between inputs
                key_delay=200,#ms
                rowscrolling_duration=300,#ms when scrolling one row upor down, this is the duration it takes
                rowscrolling_all_duration=500,#ms #rowscrolling all rows up
                fastscroll_duration=50,#ms for fast scrolling
                deckname_selected_animation_duration=400,#ms
                menu_button_selected_animation_duration=400,#ms
                card_snapback_duration=200#ms, time it takes for a card to snap back and do the card pressed animation in reverse
                ):

        if len(groups) == 0:
            raise RuntimeError("You need at least one group")
        if len(groups) > max_group_number:
            raise RuntimeError("Too many groups. Adjust your max_group_size")
        if cards_per_line <= 0 or cards_per_column <= 0:
            raise RuntimeError("cards_per_line and cards_per_column have to be greater than 0")

        super().__init__(FrameEnums.RENDERABLE_CARDLIST_VIEWER_WIDGET, None, frame_dim, focus_group=focus_group, parent_frame=parent_frame)

        #deepcopying, to avoid altering the references
        self.full_cardlist = full_cardlist.copy()
        self.groups = deepcopy(groups)
        self.special_info_frames = (special_info_frames if special_info_frames is not None else {})
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

        self.full_image_background_color = full_image_background_color
        self.full_image_background_alpha = full_image_background_alpha

        #margin for the textbox
        self.cardtext_hmargin = cardtext_hmargin
        self.cardtext_vmargin = cardtext_vmargin

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
        self._state = RenderableCardListviewer.NOTHING_FOCUSED
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
        #highlighted surface
        self.menu_label_highlighted_surface = None
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
        #highlighted menu
        self.menu_label_highlighted_color = menu_label_highlighted_color
        self.menu_label_highlighted_alpha = menu_label_highlighted_alpha
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
                                                                    RenderableCardListviewer.IS_COPYLIST_KEY: True,
                                                                    RenderableCardListviewer.RENAMABLE_KEY: False #not renamable
                                                                    }
        self.shown_group = (shown_group if shown_group is not None else list(self.groups.keys())[0])

        #deckname subframe
        self.focused_text_input_subframe = None

        #key clock for all key triggers
        self.key_clock = Clock()
        self.key_delay = key_delay

        #rowscrolling clock
        self.rowscrolling_clock = Clock()
        self.rowscrolling_duration = rowscrolling_duration
        self.rowscrolling_all_duration = rowscrolling_all_duration
        self.fastscroll_enabled = False
        self.fastscroll_duration = fastscroll_duration
        self.rowscroll_copy = None

        self.deckname_selected_animation_clock = Clock()
        self.deckname_selected_animation_duration = deckname_selected_animation_duration
        self.deckname_rendered_and_positions_copy = None

        self.menu_button_selected_animation_clock = Clock()
        self.menu_button_focused_image_rendered_copy = None
        self.menu_button_focused_image_rendered_pos_copy = None
        self.menu_button_frame_copy = None
        self.menu_button_selected_animation_duration = menu_button_selected_animation_duration

        #info text, for displaying information
        self.info_text_frame = None
        self.info_text_surface = None
        self.info_text_rendered = None #actual rendered text
        self.info_text_surface_alpha = info_text_surface_alpha
        self.info_text_hlen_p = info_text_hlen_p
        self.info_text_vlen_p = info_text_vlen_p
        #info text colors
        self.info_text_color = info_text_color
        self.info_text_warning_color = info_text_warning_color
        self.info_text_error_color = info_text_error_color
        #fadeout time saved
        self.current_info_text_fadeout_duration = 0
        self.info_text_fading_clock = Clock()
        #dropdown menu
        self.dropdown_menu = None
        self.dropdown_menu_frame = None
        self.dropdown_menu_hlen_p = dropdown_menu_hlen_p
        self.dropdown_menu_vlen_p = dropdown_menu_vlen_p
        self.dropdown_menu_options_dict = None

        self.group_creation_enabled = group_creation_enabled
        self.group_selection_enabled = group_selection_enabled

        #long enter
        self.time_until_long_enter_pressed = time_until_long_enter_pressed
        self.enter_clock = Clock()

        self.card_snapback_duration = card_snapback_duration
        self.card_snapback_clock = Clock()
        self.enter_pressed_on_card_percentage = 0
        self.card_pressed_size_change_percentage = card_pressed_size_change_percentage

        self.cards_dict_before_enter = None
        self.cards_rects_before_enter = None
        self.cards_rects_before_enter_index = -1

        self.prev_state = None

        self.key_clock.start()
        self.rerender()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self.prev_state = self._state
        self._state = new_state


    def rerender(self):
        #info text calc
        iheight = int(self.height * self.info_text_vlen_p)
        self.info_text_frame = pygame.Rect( 0,
                                            self.height - iheight,
                                            int(self.width * self.info_text_hlen_p),
                                            iheight
                                            )
        self.info_text_surface = pygame.Surface((self.info_text_frame.width, self.info_text_frame.height), pygame.SRCALPHA)
        self.info_text_rendered = None
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
        self.menu_label_highlighted_surface = self.menu_label_surface.copy()
        self.menu_label_highlighted_surface.fill((*self.menu_label_highlighted_color, self.menu_label_highlighted_alpha))
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
        self.menu_button_frame, self.deckname_frame, self.decksize_frame = graphics.split_rect_horizontally(
                                                                                                        pygame.Rect(
                                                                                                        self.inner_menu_label_frame.x - self.menu_label_frame.x,
                                                                                                        self.inner_menu_label_frame.y - self.menu_label_frame.y,
                                                                                                        self.inner_menu_label_frame.width, self.inner_menu_label_frame.height),
                                                                                                        [self.menu_label_menu_button_hmargin,
                                                                                                        1.0-(self.menu_label_menu_button_hmargin + self.menu_label_decksize_text_hmargin),
                                                                                                        self.menu_label_decksize_text_hmargin
                                                                                                        ]
                                                                                                        )
        #now rendering the menu items
        #rendering the menu button
        self.menu_button_unfocused_image_rendered,\
        self.menu_button_unfocused_image_rendered_pos = graphics.img_load_and_position(self.menu_button_unfocused_image, self.menu_button_frame)
        self.menu_button_focused_image_rendered,\
        self.menu_button_focused_image_rendered_pos = graphics.img_load_and_position(self.menu_button_focused_image, self.menu_button_frame)

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

        #rendering the name
        self.render_deckname_text()
        #rendering the decksize
        self.render_decksize_text()
        #creating the cardmenu
        self.create_dropdown_menu()
        #now getting the card positions
        self.recalculate_main_list_positions()
        #prerendering
        self.prerender()

    def render_deckname_text(self):

        self.deckname_rendered_and_positions = graphics.render_page_from_chars_color(
                                                                                        font=self.font,
                                                                                        page=[[(self.shown_group, self.menu_label_text_color)]],
                                                                                        frame=self.deckname_frame,
                                                                                        text_color=self.menu_label_text_color,
                                                                                        centered=True,
                                                                                        vertical_centered=True
                                                                                    )
    def render_decksize_text(self):

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
    def reload_current_group(self):

        self.render_deckname_text()
        self.render_decksize_text()
        self.create_dropdown_menu()
        self.recalculate_main_list_positions()

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
        gcards = [(key, value) for key, value in gcards.items()]
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

            if amount == 0:
                main_list_cards_index += 1
                continue

            if self.main_list_view_state == RenderableCardListviewer.SHOW_WITH_AMOUNT:

                img_rect = pygame.Rect(cx, cy, self.cardimage_width, self.cardimage_height)
                text_rect = pygame.Rect(cx, cy + self.cardimage_height, self.subtext_width, self.subtext_height)
                #applying the margins
                text_rect = graphics.apply_margins(text_rect, self.cardtext_hmargin, self.cardtext_vmargin)

                if cy not in self.main_list_cards_rects:
                    self.main_list_cards_rects[cy] = []

                self.main_list_cards_rects[cy].append((card_id_index, main_list_cards_index, img_rect, text_rect))
                self.main_list_cards_dict[card_id_index] = (main_list_cards_index, img_rect, text_rect, cy)

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
                    self.main_list_cards_dict[card_id_index] = (main_list_cards_index, img_rect, text_rect, cy)

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

                img_rerender_needed = True
                img, img_pos = None, None
                if cinfo.card_image_path in self.card_render_cache:
                    img, img_pos, cached_img_rect = self.card_render_cache[cinfo.card_image_path]
                    if cached_img_rect == img_rect:
                        img_rerender_needed = False

                if img_rerender_needed:
                    img, img_pos = graphics.img_load_and_position(cinfo.card_image_path, pygame.Rect(0, 0, img_rect.width, img_rect.height))
                    self.card_render_cache[cinfo.card_image_path] = (img, img_pos, img_rect.copy())

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

                    txt_rerender_needed = True
                    if amount in self.text_render_cache:
                        trend, cached_txt_rect = self.text_render_cache[amount]
                        if cached_txt_rect == text_rect:
                            txt_rerender_needed = False
                    if txt_rerender_needed:
                        trend = graphics.render_page_from_chars(self.font, [f"x{amount}"], pygame.Rect(0, 0, text_rect.width, text_rect.height),
                                                                self.card_text_description_color, centered=True, vertical_centered=True
                                                                )
                        self.text_render_cache[amount] = (trend, text_rect.copy())

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

        if self.state == RenderableCardListviewer.MENU_BUTTON_FOCUSED:
            self.menu_label_highlighted_surface = pygame.Surface((self.menu_button_frame.width, self.menu_button_frame.height), pygame.SRCALPHA)
            self.menu_label_highlighted_surface.fill((*self.menu_label_highlighted_color, self.menu_label_highlighted_alpha))
            self.menu_label_surface.blit(self.menu_label_highlighted_surface, (self.menu_button_frame.x, self.menu_button_frame.y))
        elif self.state == RenderableCardListviewer.MENU_DECKNAME_FOCUSED:
            self.menu_label_highlighted_surface = pygame.Surface((self.deckname_frame.width, self.deckname_frame.height), pygame.SRCALPHA)
            self.menu_label_highlighted_surface.fill((*self.menu_label_highlighted_color, self.menu_label_highlighted_alpha))
            self.menu_label_surface.blit(self.menu_label_highlighted_surface, (self.deckname_frame.x, self.deckname_frame.y))
        elif self.state == RenderableCardListviewer.MENU_DECKSIZE_FOCUSED:
            self.menu_label_highlighted_surface = pygame.Surface((self.decksize_frame.width, self.decksize_frame.height), pygame.SRCALPHA)
            self.menu_label_highlighted_surface.fill((*self.menu_label_highlighted_color, self.menu_label_highlighted_alpha))
            self.menu_label_surface.blit(self.menu_label_highlighted_surface, (self.decksize_frame.x, self.decksize_frame.y))
        #widgets
        #button
        button_img = (self.menu_button_focused_image_rendered if self.state in\

                        [RenderableCardListviewer.MENU_BUTTON_FOCUSED,
                        RenderableCardListviewer.MENU_BUTTON_SELECTED_ANIMATION]\

                        else self.menu_button_unfocused_image_rendered)

        button_pos = (self.menu_button_focused_image_rendered_pos if self.state in\

                        [RenderableCardListviewer.MENU_BUTTON_FOCUSED,
                        RenderableCardListviewer.MENU_BUTTON_SELECTED_ANIMATION]\

                        else self.menu_button_unfocused_image_rendered_pos)

        self.menu_label_surface.blit(button_img, button_pos)
        #deckname
        for surf, pos in self.deckname_rendered_and_positions:
            self.menu_label_surface.blit(surf, pos)
        for surf, pos in self.decksize_rendered_and_positions:
            self.menu_label_surface.blit(surf, pos)

        #bliting the widgets onto the label
        self.surface.blit(self.menu_label_surface, self.menu_label_surface_pos)

        if self.info_text_active():
            self.info_text_surface.fill((*Colors.BLACK, self.info_text_surface_alpha))
            for surf, pos in self.info_text_rendered:
                self.info_text_surface.blit(surf, pos)
            self.surface.blit(self.info_text_surface, (self.info_text_frame.x, self.info_text_frame.y))

        if self.state == RenderableCardListviewer.DROPDOWN_MENU_ACTIVE:
            self.dropdown_menu.render(self.surface)

        if self.state == RenderableCardListviewer.FULL_IMAGE_SHOWN:
            self.surface.blit(self.full_image_surface, (0, 0))
        elif self.focused_text_input_subframe is not None:
            self.focused_text_input_subframe.render(self.surface)

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

    #gets the size of the currently shown deck
    def get_shown_group_decksize(self):
        return sum(self.groups[self.shown_group][RenderableCardListviewer.CARDLIST_KEY].values())

    #adding a group
    def add_group(self, groupname, cardlist=None, mutable=True, is_copylist=False, renamable=True):
        #returns true if successful
        if not groupname or groupname in list(self.groups.keys()):
            return False

        if cardlist is None:
            cardlist = {}

        self.groups[groupname] = {
                                    RenderableCardListviewer.CARDLIST_KEY: cardlist,
                                    RenderableCardListviewer.MUTABLE_KEY: mutable,
                                    RenderableCardListviewer.IS_COPYLIST_KEY: is_copylist,
                                    RenderableCardListviewer.RENAMABLE_KEY: renamable
                                    }

        return True

    """
    ------------------------------------------------
                        INFO TEXT
    ------------------------------------------------
    """

    #for getting the info text flag
    def info_text_active(self):
        return (self.info_text_rendered is not None)

    def print_info_text(self, text_page, text_color, fade_duration):
        #text needs to be a colored page
        self.info_text_rendered = graphics.render_page_from_chars_color(
                                                                        self.font,
                                                                        text_page,
                                                                        pygame.Rect(0, 0, self.info_text_frame.width, self.info_text_frame.height),
                                                                        text_color=text_color,
                                                                        centered=True,
                                                                        vertical_centered=True
                                                                        )

        self.current_info_text_fadeout_duration = fade_duration
        self.info_text_fading_clock.start()

    def info_text_tick(self):

        percentage = self.info_text_fading_clock.elapsed() / self.current_info_text_fadeout_duration

        if percentage >= 1.0:
            self.info_text_rendered = None
        else:
            fade = int((1.0 - percentage) * 255)
            self.info_text_surface.set_alpha(fade)

    """
    --------------------------------------
            DROPDOWN_MENU_CREATION
    --------------------------------------
    """
    def create_dropdown_menu_dict(self):

        mdict = {
                    ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY: RenderableCardListviewer.MENU_OPTIONS.SHOWN_AMOUNT
                }

        if self.group_selection_enabled:

            selection_groups_dict = {(G,): None for G in self.groups.keys() if G != ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY}
            selection_groups_dict[ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY] = RenderableCardListviewer.MENU_OPTIONS.SELECT_GROUP_OPTIONS_SHOWN_AMOUNT

            mdict[RenderableCardListviewer.MENU_OPTIONS.SELECT_GROUP_OPTION_KEY] = selection_groups_dict

        if self.group_creation_enabled:

            mdict[RenderableCardListviewer.MENU_OPTIONS.CREATE_GROUP_OPTION_KEY] = None

        #sorting types
        sorting_options_dict = {
                                    RenderableCardListviewer.MENU_OPTIONS.RANDOMIZED_SORTING: None,
                                    RenderableCardListviewer.MENU_OPTIONS.NAME_DESCENDING_SORTING: None,
                                    RenderableCardListviewer.MENU_OPTIONS.NAME_ASCENDING_SORTING: None,
                                    ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY: RenderableCardListviewer.MENU_OPTIONS.SORTING_OPTIONS_SHOWN_AMOUNT
                                }

        if self.main_list_view_state == RenderableCardListviewer.SHOW_WITH_AMOUNT:

            sorting_options_dict[RenderableCardListviewer.MENU_OPTIONS.AMOUNT_DESCENDING_SORTING] = None
            sorting_options_dict[RenderableCardListviewer.MENU_OPTIONS.AMOUNT_ASCENDING_SORTING] = None

        mdict[RenderableCardListviewer.MENU_OPTIONS.SORTING_OPTION_KEY] = sorting_options_dict

        #display types
        display_options_dict = {
                                    RenderableCardListviewer.MENU_OPTIONS.SHOW_EACH_CARD_DISPLAY_TYPE: None,
                                    RenderableCardListviewer.MENU_OPTIONS.SHOW_WITH_AMOUNT_DISPLAY_TYPE: None,
                                    ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY: RenderableCardListviewer.MENU_OPTIONS.DISPLAY_OPTIONS_SHOWN_AMOUNT
                                }

        mdict[RenderableCardListviewer.MENU_OPTIONS.DISPLAY_TYPE_KEY] = display_options_dict

        return mdict


    def handle_dropdown_menu_selection(self, event):

        if event.type == ScrollableDropdownMenu.EventTypes.SELECTION_FINISHED_EVENT:
            #selection was done
            if self.state == RenderableCardListviewer.DROPDOWN_MENU_ACTIVE:
                #getting the selected instance
                full_trace = event.data
                selection = RenderableCardListviewer.MENU_OPTIONS.get_option_from_traceback(event.data)

                if selection == RenderableCardListviewer.MENU_OPTIONS.RANDOMIZED_SORTING:
                    self.sorting_function = RenderableCardListviewer.SortingFunctions.randomized
                    self.main_list_cards = self.sorting_function(self.main_list_cards)
                    self.recalculate_main_list_positions()
                elif selection == RenderableCardListviewer.MENU_OPTIONS.NAME_DESCENDING_SORTING:
                    if self.sorting_function is not RenderableCardListviewer.SortingFunctions.name_descending:
                        self.sorting_function = RenderableCardListviewer.SortingFunctions.name_descending
                        self.main_list_cards = self.sorting_function(self.main_list_cards)
                        self.recalculate_main_list_positions()
                elif selection == RenderableCardListviewer.MENU_OPTIONS.NAME_ASCENDING_SORTING:
                    if self.sorting_function is not RenderableCardListviewer.SortingFunctions.name_ascending:
                        self.sorting_function = RenderableCardListviewer.SortingFunctions.name_ascending
                        self.main_list_cards = self.sorting_function(self.main_list_cards)
                        self.recalculate_main_list_positions()
                elif selection == RenderableCardListviewer.MENU_OPTIONS.AMOUNT_DESCENDING_SORTING:
                    if self.sorting_function is not RenderableCardListviewer.SortingFunctions.amount_descending:
                        self.sorting_function = RenderableCardListviewer.SortingFunctions.amount_descending
                        self.main_list_cards = self.sorting_function(self.main_list_cards)
                        self.recalculate_main_list_positions()
                elif selection == RenderableCardListviewer.MENU_OPTIONS.AMOUNT_ASCENDING_SORTING:
                    if self.sorting_function is not RenderableCardListviewer.SortingFunctions.amount_ascending:
                        self.sorting_function = RenderableCardListviewer.SortingFunctions.amount_ascending
                        self.main_list_cards = self.sorting_function(self.main_list_cards)
                        self.recalculate_main_list_positions()

                #display types
                elif selection == RenderableCardListviewer.MENU_OPTIONS.SHOW_EACH_CARD_DISPLAY_TYPE:
                    if self.main_list_view_state != RenderableCardListviewer.SHOW_EACH_CARD:
                        self.main_list_view_state = RenderableCardListviewer.SHOW_EACH_CARD
                        self.recalculate_main_list_positions()

                elif selection == RenderableCardListviewer.MENU_OPTIONS.SHOW_WITH_AMOUNT_DISPLAY_TYPE:
                    if self.main_list_view_state != RenderableCardListviewer.SHOW_WITH_AMOUNT:
                        self.main_list_view_state = RenderableCardListviewer.SHOW_WITH_AMOUNT
                        self.recalculate_main_list_positions()

                #group selection
                elif full_trace[:-1] == [RenderableCardListviewer.MENU_OPTIONS.SELECT_GROUP_OPTION_KEY]:

                    self.shown_group = selection[0]
                    self.reload_current_group()

                elif selection == RenderableCardListviewer.MENU_OPTIONS.CREATE_GROUP_OPTION_KEY:
                    self.initialize_deck_creation_frame()

                self.reload_dropdown_menu_with_progress()



    def create_dropdown_menu(self):

        self.dropdown_menu_options_dict = self.create_dropdown_menu_dict()

        #creating the dropdown menu
        self.dropdown_menu_frame = pygame.Rect(
                                                    self.inner_area.x,
                                                    self.inner_area.y + self.menu_label_height,
                                                    int(self.dropdown_menu_hlen_p * self.inner_area.width),
                                                    int(self.dropdown_menu_vlen_p * self.inner_area.height)
                                            )

        self.dropdown_menu = ScrollableDropdownMenu(
                                                        self.dropdown_menu_frame,
                                                        self.dropdown_menu_options_dict,
                                                        parent_frame=self
                                                    )

        self.focus()

    def reload_dropdown_menu_with_progress(self):

        if self.dropdown_menu is not None:

            trace = self.dropdown_menu.get_option_trace()
            self.create_dropdown_menu()
            self.dropdown_menu.select_option_expanded(trace)





    def bind_events(self):
        self.clear_event_callbacks()

    def tick(self):
        self.manage_pygame_events()

        if self.exit_flag_raised():
            return None

        if self.is_focused():
            if self.info_text_active():
                self.info_text_tick()

            #dropdown events
            dropdown_events = self.dropdown_menu.poll_events()

            if self.state == RenderableCardListviewer.DROPDOWN_MENU_ACTIVE:
                self.dropdown_menu.tick()

            for event in dropdown_events:
                self.handle_dropdown_menu_selection(event)

            #non input accepting states
            if self.state == RenderableCardListviewer.MOVING_ONE_ROW_UP:
                self.move_one_row_up()
            elif self.state == RenderableCardListviewer.MOVING_ONE_ROW_DOWN:
                self.move_one_row_down()
            elif self.state == RenderableCardListviewer.MOVING_ALL_ROWS_UP:
                self.move_all_rows_up()
            elif self.state == RenderableCardListviewer.FULL_IMAGE_SHOWN:
                if not self.key_pressed(KeyAlternatives.SHOW_IMAGE_KEY):
                    self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED
            elif self.state == RenderableCardListviewer.DECKNAME_SELECTED_ANIMATION:
                self.deckname_selected_animation()
            elif self.state == RenderableCardListviewer.MENU_BUTTON_SELECTED_ANIMATION:
                self.menu_button_selected_animation()
            elif self.state == RenderableCardListviewer.INITIALIZE_DECK_RENAMING_FRAME:
                self.initialize_deck_renaming_frame()
            elif self.state == RenderableCardListviewer.CARD_SNAPBACK_ANIMATION:
                self.card_snapback_animation()
            elif self.state == RenderableCardListviewer.ENTER_PRESSED:
                if not (self.key_pressed(pygame.K_RETURN) or self.key_pressed(KeyAlternatives.ENTER_ALTERNATIVE)):
                    if self.prev_state == RenderableCardListviewer.MAIN_LIST_FOCUSED and self.n_cards_shown > 0:
                        #if a card was focused, we need to animate putting it back in its original state
                        self.state = RenderableCardListviewer.CARD_SNAPBACK_ANIMATION
                        self.initialize_card_snapback_animation()
                    else:
                        self.state = self.prev_state
                        if self.enter_clock.elapsed() >= self.time_until_long_enter_pressed:
                            self.long_enter_pressed()
                        else:
                            self.enter_pressed()
                        self.key_clock.start()
                else:
                    if self.prev_state == RenderableCardListviewer.MAIN_LIST_FOCUSED and self.n_cards_shown > 0:
                        self.card_pressed_animation()
            elif self.state == RenderableCardListviewer.DECK_RENAMING_FRAME_ACTIVE:
                ret = self.focused_text_input_subframe.tick()

                if ret is None:

                    #setting the groupname
                    if self.focused_text_input_subframe.exit_with_enter():

                        text = self.focused_text_input_subframe.get_input_text()

                        if not text or text in list(self.groups.keys()):
                            tcolor = (RenderableCardListviewer.INFO_TEXT_ERROR_COLOR if self.info_text_error_color is None else self.info_text_error_color)

                            self.print_info_text(
                                                    [[(RenderableCardListviewer.DECKNAME_ALREADY_EXISTS_ERROR_INFO_TEXT, tcolor)]],
                                                    tcolor,
                                                    RenderableCardListviewer.DECKNAME_ALREADY_EXISTS_ERROR_FADING_DURATION
                                                )

                            self.focused_text_input_subframe.reset_exit_flag()
                            self.focused_text_input_subframe.reset_exit_type()

                        else:

                            data_cp = deepcopy(self.groups[self.shown_group])
                            del self.groups[self.shown_group]
                            self.shown_group = self.focused_text_input_subframe.get_input_text()
                            self.groups[self.shown_group] = data_cp
                            self.focused_text_input_subframe = None
                            self.focus()
                            self.state = RenderableCardListviewer.MENU_DECKNAME_FOCUSED
                            self.render_deckname_text()
                            self.create_dropdown_menu()

                    elif self.focused_text_input_subframe.exit_with_escape():
                        self.focused_text_input_subframe = None
                        self.state = RenderableCardListviewer.MENU_DECKNAME_FOCUSED

                    self.key_clock.start()

            elif self.state == RenderableCardListviewer.DECK_CREATION_FRAME_ACTIVE:
                ret = self.focused_text_input_subframe.tick()

                if ret is None:
                    self.finalize_deck_creation_frame()

                self.key_clock.start()

            else:
                #accept inputs

                if self.key_clock.elapsed() > self.key_delay:

                    if self.key_pressed(pygame.K_ESCAPE):
                        self.escape_pressed()
                        self.key_clock.start()

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

                    if self.key_pressed(KeyAlternatives.SHOW_IMAGE_KEY):
                        self.state = RenderableCardListviewer.FULL_IMAGE_SHOWN
                        self.prerender_full_image()
                        self.key_clock.start()

                    if self.key_pressed(pygame.K_RETURN) or self.key_pressed(KeyAlternatives.ENTER_ALTERNATIVE):

                        if self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED and self.n_cards_shown > 0:
                            self.cards_dict_before_enter = self.main_list_cards_dict[self.selected_card_index]
                            self.cards_rects_before_enter = self.main_list_cards_rects[self.cards_dict_before_enter[3]]#the cy
                            self.cards_rects_before_enter_index = [i for i in range(len(self.cards_rects_before_enter)) if self.cards_rects_before_enter[i][0] == self.selected_card_index][0]
                        self.state = RenderableCardListviewer.ENTER_PRESSED
                        self.enter_clock.start()
                        self.key_clock.start()

                    if self.key_pressed(pygame.K_BACKSPACE) or self.key_pressed(KeyAlternatives.BACK_KEY):
                        self.back_pressed()
                        self.key_clock.start()

        return self
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
        elif self.state == RenderableCardListviewer.MENU_BUTTON_FOCUSED:
            self.state = RenderableCardListviewer.MENU_DECKSIZE_FOCUSED
        elif self.state == RenderableCardListviewer.MENU_DECKSIZE_FOCUSED:
            self.state = RenderableCardListviewer.MENU_DECKNAME_FOCUSED
        elif self.state == RenderableCardListviewer.MENU_DECKNAME_FOCUSED:
            self.state = RenderableCardListviewer.MENU_BUTTON_FOCUSED
        elif self.state == RenderableCardListviewer.DROPDOWN_MENU_ACTIVE:
            self.dropdown_menu.move_left()

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

        elif self.state == RenderableCardListviewer.MENU_BUTTON_FOCUSED:
            self.state = RenderableCardListviewer.MENU_DECKNAME_FOCUSED
        elif self.state == RenderableCardListviewer.MENU_DECKNAME_FOCUSED:
            self.state = RenderableCardListviewer.MENU_DECKSIZE_FOCUSED
        elif self.state == RenderableCardListviewer.MENU_DECKSIZE_FOCUSED:
            self.state = RenderableCardListviewer.MENU_BUTTON_FOCUSED
        elif self.state == RenderableCardListviewer.DROPDOWN_MENU_ACTIVE:
            self.dropdown_menu.move_right()

    def up_pressed(self):

        if self.state == RenderableCardListviewer.NOTHING_FOCUSED:
            self.state = RenderableCardListviewer.MENU_BUTTON_FOCUSED

        elif self.state == RenderableCardListviewer.MENU_BUTTON_FOCUSED\
            or self.state == RenderableCardListviewer.MENU_DECKNAME_FOCUSED\
            or self.state == RenderableCardListviewer.MENU_DECKSIZE_FOCUSED:

            self.state = RenderableCardListviewer.NOTHING_FOCUSED

        elif self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:

            if self.n_cards_shown == 0:
                self.state = RenderableCardListviewer.MENU_BUTTON_FOCUSED
                return

            if self.key_pressed(pygame.K_LSHIFT):
                if not self.fastscroll_enabled:
                    self.fastscroll_enabled = True
                    self.rowscroll_copy = self.rowscrolling_duration
                    self.rowscrolling_duration = self.fastscroll_duration
            elif self.fastscroll_enabled:
                self.fastscroll_enabled = False
                self.rowscrolling_duration = self.rowscroll_copy
            #check for going off, and if the index is in rendered rows
            if self.selected_card_index < self.cards_per_line:
                self.state = RenderableCardListviewer.MENU_BUTTON_FOCUSED
            elif (self.selected_card_index - self.cards_per_line) not in [x[1] for x in self.rendered_rows]:
                self.state = RenderableCardListviewer.MOVING_ONE_ROW_UP
                self.initialize_move_one_row_up()
            else:
                self.selected_card_index -= self.cards_per_line

        elif self.state == RenderableCardListviewer.DROPDOWN_MENU_ACTIVE:
            self.dropdown_menu.move_up()

    def down_pressed(self):

        if self.state == RenderableCardListviewer.NOTHING_FOCUSED:
            self.state = RenderableCardListviewer.MENU_BUTTON_FOCUSED

        elif self.state == RenderableCardListviewer.MENU_BUTTON_FOCUSED\
            or self.state == RenderableCardListviewer.MENU_DECKNAME_FOCUSED\
            or self.state == RenderableCardListviewer.MENU_DECKSIZE_FOCUSED:

            self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED
            self.selected_card_index = 0
            self.main_list_yscroll = 0

        elif self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:

            if self.n_cards_shown == 0:
                self.state = RenderableCardListviewer.NOTHING_FOCUSED
                return
            #check for going off, and if the index is in rendered rows
            if self.key_pressed(pygame.K_LSHIFT):
                if not self.fastscroll_enabled:
                    self.fastscroll_enabled = True
                    self.rowscroll_copy = self.rowscrolling_duration
                    self.rowscrolling_duration = self.fastscroll_duration
            elif self.fastscroll_enabled:
                self.fastscroll_enabled = False
                self.rowscrolling_duration = self.rowscroll_copy

            if self.selected_card_index >= (self.n_cards_shown - self.cards_per_line):
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

        elif self.state == RenderableCardListviewer.DROPDOWN_MENU_ACTIVE:
            self.dropdown_menu.move_down()


    def enter_pressed(self):

        #checking for deck renaming
        if self.state == RenderableCardListviewer.MENU_DECKNAME_FOCUSED:
            if self.groups[self.shown_group][RenderableCardListviewer.RENAMABLE_KEY]:
                self.state = RenderableCardListviewer.DECKNAME_SELECTED_ANIMATION
                self.initialize_deckname_selected_animation()
            else:
                tcolor = (RenderableCardListviewer.INFO_TEXT_WARNING_COLOR if self.info_text_warning_color is None else self.info_text_warning_color)


                self.print_info_text(
                                        [[(RenderableCardListviewer.RENAMING_NOT_POSSIBLE_INFO_TEXT, tcolor)]],
                                        tcolor,
                                        RenderableCardListviewer.RENAMING_NOT_POSSIBLE_FADING_DURATION
                                    )

        elif self.state == RenderableCardListviewer.MENU_BUTTON_FOCUSED:
            self.state = RenderableCardListviewer.MENU_BUTTON_SELECTED_ANIMATION
            self.initialize_menu_button_selected_animation()
        elif self.state == RenderableCardListviewer.DROPDOWN_MENU_ACTIVE:
            self.dropdown_menu.select()

    def long_enter_pressed(self):
        pass

    def back_pressed(self):

        if self.state == RenderableCardListviewer.DROPDOWN_MENU_ACTIVE:
            self.state = RenderableCardListviewer.NOTHING_FOCUSED

    def escape_pressed(self):
        if self.state == RenderableCardListviewer.NOTHING_FOCUSED:
            self.raise_exit_flag()
        else:
            self.state = RenderableCardListviewer.NOTHING_FOCUSED


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



    def initialize_deckname_selected_animation(self):

        self.deckname_rendered_and_positions_copy = self.deckname_rendered_and_positions
        self.deckname_selected_animation_clock.start()

    def deckname_selected_animation(self):

        percentage = self.deckname_selected_animation_clock.elapsed() / self.deckname_selected_animation_duration

        deckname_animation_frame = None

        if percentage >= 1.0:
            self.finalize_deckname_selected_animation()
            return

        elif percentage <= 0.5:

            rp = percentage * 2
            deckname_animation_frame = graphics.apply_margins(self.deckname_frame, 0.5 * rp, 0.5 * rp)

        else:

            rp = (percentage - 0.5) * 2
            deckname_animation_frame = graphics.apply_margins(self.deckname_frame, 0.5 * (1.0 - rp), 0.5 * (1.0 - rp))




        self.deckname_rendered_and_positions = graphics.render_page_from_chars_color(
                                                                                        font=self.font,
                                                                                        page=[[(self.shown_group, self.menu_label_text_color)]],
                                                                                        frame=deckname_animation_frame,
                                                                                        text_color=self.menu_label_text_color,
                                                                                        centered=True,
                                                                                        vertical_centered=True
                                                                                    )

    def finalize_deckname_selected_animation(self):

        self.deckname_rendered_and_positions = self.deckname_rendered_and_positions_copy
        self.state = RenderableCardListviewer.INITIALIZE_DECK_RENAMING_FRAME


    def initialize_menu_button_selected_animation(self):

        self.menu_button_focused_image_rendered_copy = self.menu_button_focused_image_rendered.copy()
        self.menu_button_focused_image_rendered_pos_copy = self.menu_button_focused_image_rendered_pos
        self.menu_button_frame_copy = self.menu_button_frame.copy()
        self.menu_button_selected_animation_clock.start()

    def menu_button_selected_animation(self):

        percentage = self.menu_button_selected_animation_clock.elapsed() / self.menu_button_selected_animation_duration

        menu_button_animation_frame = None

        if percentage >= 1.0:
            self.finalize_menu_button_selected_animation()
            return

        elif percentage <= 0.5:

            rp = percentage * 2
            menu_button_animation_frame = graphics.apply_margins(self.menu_button_frame_copy, 0.5 * rp, 0.5 * rp)

        else:

            rp = (percentage - 0.5) * 2
            menu_button_animation_frame = graphics.apply_margins(self.menu_button_frame_copy, 0.5 * (1.0 - rp), 0.5 * (1.0 - rp))



        self.menu_button_frame = menu_button_animation_frame
        self.menu_button_focused_image_rendered, self.menu_button_focused_image_rendered_pos = graphics.img_load_and_position(self.menu_button_focused_image, self.menu_button_frame)

    def finalize_menu_button_selected_animation(self):

        self.menu_button_focused_image_rendered = self.menu_button_focused_image_rendered_copy
        self.menu_button_focused_image_rendered_pos = self.menu_button_focused_image_rendered_pos_copy
        self.menu_button_frame = self.menu_button_frame_copy
        self.state = RenderableCardListviewer.DROPDOWN_MENU_ACTIVE
        self.dropdown_menu.unselect()

    def prerender_full_image(self):

        self.full_image_surface.fill((*self.full_image_background_color, self.full_image_background_alpha))
        #rendering the image
        main_list_card_idx = self.main_list_cards_dict[self.selected_card_index][0]
        cinfo = self.main_list_cards[main_list_card_idx][0].info()

        img_path = cinfo.card_image_path

        isurf, ipos = graphics.img_load_and_position(img_path, self.frame_dim)
        self.full_image_surface.blit(isurf, ipos)

    def initialize_deck_renaming_frame(self):

        self.focused_text_input_subframe = RenderableCardListviewer.FocusedTextInputFrame(self.frame_dim, self.focus_group)
        self.focused_text_input_subframe.set_input_text(self.shown_group)
        self.state = RenderableCardListviewer.DECK_RENAMING_FRAME_ACTIVE

    def initialize_deck_creation_frame(self):

        self.focused_text_input_subframe = RenderableCardListviewer.FocusedTextInputFrame(self.frame_dim, self.focus_group)
        self.focused_text_input_subframe.set_input_text("")
        self.state = RenderableCardListviewer.DECK_CREATION_FRAME_ACTIVE

    def finalize_deck_creation_frame(self):

        if self.focused_text_input_subframe.exit_with_escape():
            self.focused_text_input_subframe = None
            self.state = RenderableCardListviewer.NOTHING_FOCUSED

        elif self.focused_text_input_subframe.exit_with_enter():

            text = self.focused_text_input_subframe.get_input_text()

            if not text\
                or text in list(self.groups.keys()):

                tcolor = (RenderableCardListviewer.INFO_TEXT_ERROR_COLOR if self.info_text_error_color is None else self.info_text_error_color)

                self.print_info_text(
                                        [[(RenderableCardListviewer.DECKNAME_ALREADY_EXISTS_ERROR_INFO_TEXT, tcolor)]],
                                        tcolor,
                                        RenderableCardListviewer.DECKNAME_ALREADY_EXISTS_ERROR_FADING_DURATION
                                    )

                self.focused_text_input_subframe.reset_exit_flag()
                self.focused_text_input_subframe.reset_exit_type()

            else:

                self.focused_text_input_subframe = None

                self.add_group(
                                    text,
                                    cardlist={},
                                    mutable=True,
                                    is_copylist=False,
                                    renamable=True
                                )

                self.shown_group = text
                self.reload_current_group()

                self.state = RenderableCardListviewer.NOTHING_FOCUSED

    def card_pressed_animation(self):

        percentage = self.enter_clock.elapsed() / self.time_until_long_enter_pressed
        percentage = min(percentage, 1.0)

        self.enter_pressed_on_card_percentage = percentage
        #changing the frame dimensions

        main_list_index, img_rect, txt_rect, cy = self.cards_dict_before_enter
        card_id_index, main_list_cards_index, _1, _2 = self.cards_rects_before_enter[self.cards_rects_before_enter_index]

        size_margin = self.card_pressed_size_change_percentage * percentage
        img_rect = graphics.apply_margins(img_rect, size_margin, size_margin)
        txt_rect = graphics.apply_margins(txt_rect, size_margin, size_margin)

        self.main_list_cards_dict[card_id_index] = (main_list_index, img_rect, txt_rect, cy)
        self.main_list_cards_rects[cy][self.cards_rects_before_enter_index] = (card_id_index, main_list_cards_index, img_rect, txt_rect)


    def initialize_card_snapback_animation(self):
        self.card_snapback_clock.start()

    def card_snapback_animation(self):

        percentage = self.card_snapback_clock.elapsed() / self.card_snapback_duration

        if percentage >= 1.0:
            self.finalize_card_snapback_animation()
        else:

            main_list_index, img_rect, txt_rect, cy = self.cards_dict_before_enter
            card_id_index, main_list_cards_index, _1, _2 = self.cards_rects_before_enter[self.cards_rects_before_enter_index]

            size_margin = (self.enter_pressed_on_card_percentage * self.card_pressed_size_change_percentage) * (1.0 - percentage)
            img_rect = graphics.apply_margins(img_rect, size_margin, size_margin)
            txt_rect = graphics.apply_margins(txt_rect, size_margin, size_margin)

            self.main_list_cards_dict[card_id_index] = (main_list_index, img_rect, txt_rect, cy)
            self.main_list_cards_rects[cy][self.cards_rects_before_enter_index] = (card_id_index, main_list_cards_index, img_rect, txt_rect)


    def finalize_card_snapback_animation(self):

        main_list_index, img_rect, txt_rect, cy = self.cards_dict_before_enter
        card_id_index, main_list_cards_index, _1, _2 = self.cards_rects_before_enter[self.cards_rects_before_enter_index]

        self.main_list_cards_dict[card_id_index] = self.cards_dict_before_enter
        self.main_list_cards_rects[cy][self.cards_rects_before_enter_index] = (card_id_index, main_list_cards_index, img_rect, txt_rect)

        self.state = RenderableCardListviewer.MAIN_LIST_FOCUSED

        if fequal(self.enter_pressed_on_card_percentage, 1.0):
            self.long_enter_pressed()
        else:
            self.enter_pressed()
