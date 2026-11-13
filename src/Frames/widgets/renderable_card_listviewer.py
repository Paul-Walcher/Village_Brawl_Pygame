from __future__ import annotations
from typing import Type, Any, Callable, override

import pygame

import random
from constants import (
    fequal,
    PLAYSETS_FOLDER,
    Colors,
    Fonts,
    Fontsizes,
    KeyAlternatives,
    R_ID,
    color_t,
    point_t,
    id_t,
    MENU_BUTTON_UNFOCUSED_IMAGE,
    MENU_BUTTON_FOCUSED_IMAGE
)

from pprint import pprint

import constants
import graphics
from graphics import page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t
from clock import Clock
from modules import Modules
from event_queue_manager import Event
from copy import deepcopy
from templates.renderable_cardinfo import Renderable_CardInfo

#widgets
from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.text_input import TextInput
from Frames.widgets.dropdown_menu import DropdownMenu
from Frames.widgets.expandable_dropdown_menu import ExpandableDropdownMenu, option_trace_t, expandable_dropdown_options_t
from Frames.widgets.scrollable_dropdown_menu import (
                                                        ScrollableDropdownMenu,
                                                        scrollable_tuple_options_t,
                                                        scrollable_dropdown_options_t,
                                                        scrollable_option_trace_t,
                                                        scrollable_option_trace_element_t
                                                    )


#TODO
#
#1.) Create detection and state for long enter pressed | DONE
#2.) Create Card animation when card clicked | DONE
#--------------------------------------------------------------
#3.) Create Info shown frame when card clicked
#4.) Add Card state to main list (preview, normal)
#5.) Create card amount increase/decrease when card selected via long enter pressed
#6.) Create search menu


#types
type cardlist_element_t = tuple[ Type[Renderable_CardInfo], int ] # (class reference, amount)
type cardlist_t = list[cardlist_element_t]
type dict_cardlist_t = dict[ Type[Renderable_CardInfo], int ] # (class reference: amount)

type cardlist_sorting_function_t = Callable[ [cardlist_t], cardlist_t ]

#group types
type group_t = dict[str, Any] #group type
type group_dict_t = dict[str, group_t] #name: group

class RenderableCardListviewer(Frame):

    #==================================
    # GROUP KEYS
    #==================================

    IS_COPYLIST_KEY: str = "is_copylist"
    MUTABLE_KEY: str = "mutable"
    RENAMABLE_KEY: str = "renamable" #if the group is renamable or not
    CARDLIST_KEY: str = "cardlist"

    #full cardlist name key
    FULL_CARDLIST_NAME: str = "Full Cardlist"

    #==================================
    # INFO TEXT VARIABLES
    #==================================

    #info text colors
    INFO_TEXT_STANDARD_COLOR: color_t = Colors.BLACK
    INFO_TEXT_WARNING_COLOR: color_t = Colors.YELLOW
    INFO_TEXT_ERROR_COLOR: color_t = Colors.RED

    #Fading durations for the info text
    RENAMING_NOT_POSSIBLE_FADING_DURATION: float = 5000#ms
    RENAMING_NOT_POSSIBLE_INFO_TEXT: str = "Renaming for this group is disabled"

    #deckname exists error
    DECKNAME_ALREADY_EXISTS_ERROR_FADING_DURATION: float = 5000#ms
    DECKNAME_ALREADY_EXISTS_ERROR_INFO_TEXT: str = "The chosen Deck name already exists"

    #==================================
    # STATES
    #==================================

    NOTHING_FOCUSED: id_t = R_ID() #nothing is focused
    MAIN_LIST_FOCUSED: id_t = R_ID() #the cards in the list are focused
    MENU_BUTTON_FOCUSED: id_t = R_ID() #menu button in the menu label
    MENU_DECKNAME_FOCUSED: id_t = R_ID()
    MENU_DECKSIZE_FOCUSED: id_t = R_ID()
    DROPDOWN_MENU_FOCUSED: id_t = R_ID() #means the dropdown menu is shown
    SEARCHBAR_FOCUSED: id_t = R_ID() #the textinput is focused
    GROUP_SELECTION: id_t = R_ID() #displays the groups available (Should show if a group is a copy group or not)
    FULL_IMAGE_SHOWN: id_t = R_ID() #if the main list is focused, the selected image is shown on fullscreen
    DROPDOWN_MENU_ACTIVE: id_t = R_ID()
    #enter states
    ENTER_PRESSED: id_t = R_ID()
    CARD_SNAPBACK_ANIMATION: id_t = R_ID() #if a card was pressed, it needs to animate back into its original state

    INITIALIZE_DECK_RENAMING_FRAME: id_t = R_ID()
    DECK_RENAMING_FRAME_ACTIVE: id_t = R_ID()

    INITIALIZE_MENU_FRAME: id_t = R_ID()
    MENU_FRAME_ACTIVE: id_t = R_ID()

    #Group Creation states
    INITIALIZE_DECK_CREATION_FRAME: id_t = R_ID()
    DECK_CREATION_FRAME_ACTIVE: id_t = R_ID()

    #animation states
    MOVING_ONE_ROW_UP: id_t = R_ID()
    MOVING_ONE_ROW_DOWN: id_t = R_ID()
    MOVING_ALL_ROWS_UP: id_t = R_ID()

    DECKNAME_SELECTED_ANIMATION: id_t = R_ID()
    MENU_BUTTON_SELECTED_ANIMATION: id_t = R_ID()

    #==================================
    # VIEW STATES
    #==================================

    SHOW_WITH_AMOUNT: id_t = R_ID()
    SHOW_EACH_CARD: id_t = R_ID()

    #==================================
    # MENU OPTIONS
    #==================================

    class MENU_OPTIONS:
        """
        This class provides the option keys
        for the (dropdown) menu.
        """

        @staticmethod
        def get_option_from_traceback(traceback: scrollable_option_trace_t) -> scrollable_option_trace_element_t:
            """
            Returns the last element of the scrollable option trace.
            """
            return traceback[-1]

        SHOWN_AMOUNT: int = 5 #shown amount of options

        #sorting
        SORTING_OPTION_KEY: tuple[str] = ("Sort Group",)
        #suboptions
        RANDOMIZED_SORTING: tuple[str] = ("Randomized",)
        NAME_DESCENDING_SORTING: tuple[str] = ("Name Descending",)
        NAME_ASCENDING_SORTING: tuple[str] = ("Name Ascending",)
        AMOUNT_DESCENDING_SORTING: tuple[str] = ("Amount Descending",)
        AMOUNT_ASCENDING_SORTING: tuple[str] = ("Amount Ascending",)
        #shown_amount
        SORTING_OPTIONS_SHOWN_AMOUNT: int = 5

        #display type
        DISPLAY_TYPE_KEY: tuple[str] = ("Display Type",)
        #options for display type
        SHOW_EACH_CARD_DISPLAY_TYPE: tuple[str] = ("Show Each Card",)
        SHOW_WITH_AMOUNT_DISPLAY_TYPE: tuple[str] = ("Show With Amount",)
        #shown amount
        DISPLAY_OPTIONS_SHOWN_AMOUNT: int = 5

        #group selection
        SELECT_GROUP_OPTION_KEY: tuple[str] = ("Select Deck",)
        SELECT_GROUP_OPTIONS_SHOWN_AMOUNT: int = 5
        #group creation
        CREATE_GROUP_OPTION_KEY: tuple[str] =("Create Deck",)

    #==================================
    # SORTING FUNCTIONS
    #==================================

    class SortingFunctions:
        """
        Functions to sort cardlists.
        Each cardlist is: [(RenderableCard (Class), amount)]
        """

        @staticmethod
        def no_order(cardlist: cardlist_t) -> cardlist_t:
            """
            Returns the cardlist in the same order as
            it was before.
            """
            return cardlist

        @staticmethod
        def randomized(cardlist: cardlist_t) -> cardlist_t:
            """
            Returns the cardlist after a random shuffle.
            """
            cardlist_copy = cardlist.copy()
            random.shuffle(cardlist_copy)
            return cardlist_copy

        @staticmethod
        def name_descending(cardlist: cardlist_t) -> cardlist_t:
            """
            Sorts by name descending.
            """
            clist = cardlist.copy()
            clist.sort(key=lambda x: x[0].info().name)
            return clist

        @staticmethod
        def name_ascending(cardlist: cardlist_t) -> cardlist_t:
            """
            Sorts by name ascending.
            """
            clist = cardlist.copy()
            clist.sort(key=lambda x: x[0].info().name)
            clist.reverse()
            return clist

        @staticmethod
        def amount_descending(cardlist: cardlist_t) -> cardlist_t:
            """
            Sorts by amount descending.
            """
            clist = cardlist.copy()
            clist.sort(key=lambda x: x[1])
            return clist

        @staticmethod
        def amount_ascending(cardlist: cardlist_t) -> cardlist_t:
            """
            Sorts by amount ascending.
            """
            clist = cardlist.copy()
            clist.sort(key=lambda x: x[1])
            clist.reverse()
            return clist

    #==================================
    # SUBFRAMES
    #==================================

    #subframes
    class FocusedTextInputFrame(Frame):
        """
        Provides a text input frame.
        """

        TEXT_ENTERED: id_t = R_ID()
        ESCAPE: id_t = R_ID()

        def __init__(
                    self,
                    frame_dim: pygame.Rect,
                    focus_group: str = "",
                    has_focus: bool = True
                    ):

            #initializing
            Frame.__init__(
                            self,
                            frame_enum=FrameEnums.UNDEFINED,
                            data=None,
                            frame_dim=frame_dim,
                            focus_group=focus_group,
                            has_focus=has_focus
                            )

            self.text_input: TextInput = None
            """
            Text input reference.
            """
            self.text_input_frame: pygame.Rect = None
            """
            Frame_dim for self.text_input.
            """
            self.background_color: color_t = Colors.BLACK
            """
            Background color.
            """
            self.background_alpha: int = 127
            """
            Alpha value for the background.
            """
            self.escape_released: bool = False
            """
            For checking if escaping the frame is possible.
            """
            self._exit_type: id_t = None
            """
            The state describing how the frame was exited.
            """
            self.intro_delay: float = 100#ms
            """
            The intro delay.
            """
            self.intro_delay_clock: Clock = Clock()
            """
            Intro delay clock.
            """

            self.rerender()

        @override
        def rerender(self) -> None:
            """
            Rerendering.
            """
            self.text_input_frame = pygame.Rect(0, 0, self.width//2, self.height//20)
            xc, yc = graphics.get_center_with_rect(self.frame_dim, self.text_input_frame)
            #setting the centered position
            self.text_input_frame.x = xc
            self.text_input_frame.y = yc
            #creating the text input
            self.text_input = TextInput(
                                        self.text_input_frame,
                                        focus_group=self.focus_group,
                                        has_focus=True #starts out with focus
                                        )

            self.raise_prerender_flag()
            self.intro_delay_clock.start()

        @override
        def prerender(self) -> None:
            """
            Prerendering.
            """
            self.surface.fill((*self.background_color, self.background_alpha))
            self.text_input.render(self.surface)

        def set_input_text(self, text: str = "") -> None:
            """
            Sets the text for self.input_text_frame.
            """
            self.text_input.set_text(text)

        def get_input_text(self) -> str:
            """
            Returns the text of self.text_input.
            """
            return self.text_input.get_text()

        def reset_exit_type(self) -> None:
            """
            Resets the exit type.
            """
            self._exit_type = None

        def exit_with_enter(self) -> bool:
            """
            Is true if this frame exited with an enter pressed.
            """
            return (self._exit_type == RenderableCardListviewer.FocusedTextInputFrame.TEXT_ENTERED)

        def exit_with_escape(self) -> bool:
            """
            Is true if this frame was aborted.
            """
            return (self._exit_type == RenderableCardListviewer.FocusedTextInputFrame.ESCAPE)

        @override
        def tick(self) -> None:
            """
            Tick function.
            """

            if self.intro_delay_clock.elapsed() > self.intro_delay:
                self.manage_pygame_events()

            self.text_input.tick()

            #polling textinput events
            for event in self.text_input.poll_events():
                if event.type == TextInput.EventTypes.TEXT_ENTERED:
                    self._exit_type = RenderableCardListviewer.FocusedTextInputFrame.TEXT_ENTERED
                    self.raise_exit_flag()

            if self.exit_flag_raised():
                return None

            if is_focused():
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

            if not self.text_input.is_focused() and not self.is_focused():
                self.focus()
                self.escape_released = False

            if self.text_input.is_focused():
                self.raise_prerender_flag()

            if self.prerender_flag_raised():
                self.prerender()
                self.reset_prerender_flag()

            return self

    #==================================
    # INIT
    #==================================

    def __init__(
                    self,
                    frame_dim: pygame.Rect,  #frame dimension, into which it is rendered into
                    full_cardlist: dict_cardlist_t, #a dictionary of {RenderableCard(Class): amount}
                    groups: group_dict_t,  #must include at least one group. is {name: {"cardlist": {renderable_card: amount}, "mutable": (False/True), "is_copylist": (False/True)}}
                    special_info_frames: dict[ Type[Renderable_CardInfo], dict[ tuple[str], Type[Frame] ] ] = None,
                    #a dictionary like: {cardclass: (list_of_groups_this_info_frame_will_be_used, instantiated frame)}
                    #for the card as key, when it is clicked the frame given as value[1] will be used in all groups in value[0] instead of the normal infopage
                    focus_group: str = "",
                    has_focus: bool = True,
                    parent_frame: Frame = None,

                    shown_group: str = None, #the name of the first shown group, must be the name of a group or None

                    font: pygame.font.Font = Fonts.STANDARD_FONT,
                    max_group_number: int = 25,
                    #maximum number of groups allowed, gets enforced on loading in and when trying to create a neww group

                    #card dimensions
                    cards_per_line: int = 8,
                    cards_per_column: int = 4,

                    #the sorting function that is employed for all groups, when the groups are shown
                    sorting_function: cardlist_sorting_function_t = None,
                    #determines if while typing the searched up cards should be shown
                    search_while_typing: bool = True,

                    #what percentage of the height is used of the menu_label, and what percentage of width is used
                    menu_label_menu_button_hmargin: float = 0.2,
                    menu_label_decksize_text_hmargin: float = 0.2,
                    menu_label_vmargin: float = 0.1,
                    menu_label_highlighted_color: color_t = Colors.YELLOW,
                    menu_label_highlighted_alpha: int = 64,
                    #full image data
                    full_image_background_color: color_t = Colors.BLACK,
                    full_image_background_alpha: int = 180,
                    cardtext_hmargin: float = 0.2,
                    cardtext_vmargin: float = 0.2,
                    #distances inside the label, so the text wont be right at the border
                    menu_label_inner_hmargin: float = 0.1,
                    menu_label_inner_vmargin: float = 0.1,
                    menu_label_color: color_t = Colors.BLACK,
                    menu_label_text_color: color_t = Colors.WHITE,
                    #alpha of the menu label
                    menu_label_alpha: int = 200,
                    #margins for the main list
                    main_list_hmargin: float = 0.1,
                    main_list_vmargin: float = 0.1,
                    #how much the cards should be separated, based on the cardlist width and height
                    main_list_separator_h_percentage: float = 0.1,
                    main_list_separator_v_percentage: float = 0.1,
                    #menu label assets
                    menu_button_unfocused_image: str = MENU_BUTTON_UNFOCUSED_IMAGE,
                    menu_button_focused_image: str = MENU_BUTTON_FOCUSED_IMAGE,
                    #in which color the group name will be shown
                    group_name_color: color_t = Colors.WHITE,
                    #what percentage of width and height is used for the border
                    border_frame_margin: float = 0.02,
                    #fill color of the border
                    border_frame_color: color_t = Colors.DARK_CYAN,
                    #the frame outline is drawn once on the outer edge and once in the inner edge
                    border_frame_outline_margin: float = 0.2,
                    border_frame_outline_color: color_t = Colors.BLACK,
                    #background color of the list
                    main_list_color: color_t = Colors.CYAN,
                    #margins for the cards inside the main list
                    inner_frame_hmargin: float = 0.1,
                    inner_frame_vmargin: float = 0.05,
                    #description text shown under a card
                    card_text_description_color: color_t = Colors.BLACK,
                    #either showing with amount or not
                    main_list_view_state: id_t = None,
                    #shadow offsets for the cards
                    cardshadow_hoffset_p: float = 0.075,
                    cardshadow_voffset_p: float = 0.075,
                    cardshadow_alpha: int = 120,
                    selected_card_size_increase_percentage: float = 0.05,
                    selected_cardshadow_color: color_t = Colors.YELLOW,
                    selected_cardshadow_alpha: int = 120,
                    #margin between timage and any text rendered below
                    subtext_margin: float = 0.2,
                    #dropdown menu
                    dropdown_menu_hlen_p: float = 0.5,
                    dropdown_menu_vlen_p: float = 0.4,


                    #info text specifications
                    info_text_hlen_p: float = 0.3,#horizontal length percentage
                    info_text_vlen_p: float = 0.15,#vertical length percentage
                    info_text_surface_alpha: int = 180,
                    info_text_color: color_t = None,
                    info_text_warning_color: color_t = None,
                    info_text_error_color: color_t = None,

                    #group menu stuff
                    group_selection_enabled: bool = True,
                    group_creation_enabled: bool = True,

                    #enter states
                    time_until_long_enter_pressed: float = 500,#ms, how long until the long enter state is reached
                    #percentage when card is selected
                    card_pressed_size_change_percentage: float = 0.25,
                    #delay between inputs
                    key_delay: float = 200,#ms
                    rowscrolling_duration: float = 300,#ms when scrolling one row upor down, this is the duration it takes
                    rowscrolling_all_duration: float = 500,#ms #rowscrolling all rows up
                    fastscroll_duration: float = 50,#ms for fast scrolling
                    deckname_selected_animation_duration: float = 400,#ms
                    menu_button_selected_animation_duration: float = 400,#ms
                    card_snapback_duration: float = 200#ms, time it takes for a card to snap back and do the card pressed animation in reverse
                    ):

        Frame.__init__(
                            self,
                            frame_enum=FrameEnums.RENDERABLE_CARDLIST_VIEWER_WIDGET,
                            data=None,
                            frame_dim=frame_dim,
                            parent_frame=parent_frame,
                            focus_group=focus_group,
                            has_focus=has_focus
                            )
        #==================================
        # INIT DATA
        #==================================

        #deepcopying, to avoid altering the references
        self.full_cardlist: dict_cardlist_t = full_cardlist.copy()
        """
        The full cardlist. In the form of: Class Type Reference: amount.
        Should contain all cards available.
        """
        self.groups: group_dict_t = deepcopy(groups)
        """
        A deepcopy of the given groups.
        """
        self.special_info_frames: dict[ Type[Renderable_CardInfo], dict[ tuple[str], Type[Frame] ] ] = (special_info_frames if special_info_frames is not None else {})
        """
        Special info frames are info frames that will be used instead of standard CardinfoFrame.

        The structure is:

        Cardclass (that gets another frame): { (tuple of groups this frame will be used for):  Frame class reference}
        """
        self.shown_group: str = shown_group
        """
        The initially shown group. Gets set later on if it is None.
        """
        self.group_name_color: color_t = group_name_color
        """
        Color the name of the group will be shown in.
        """
        self.max_group_number: int = max_group_number
        """
        The maximum number of groups allowed.
        """
        self.sorting_function: cardlist_sorting_function_t = (sorting_function if sorting_function is not None else RenderableCardListviewer.SortingFunctions.name_descending)
        """
        The sorting function used for sorting self.cardlist.
        Sorts by name descending on default.
        """
        self.cards_per_line: int = cards_per_line
        """
        Number of cards per line shown in the editor.
        """
        self.cards_per_column: int = cards_per_column
        """
        Number of cards per column shown in the editor.
        """
        self.font: pygame.font.Font = font
        """
        The font used for all text.
        """
        self.card_text_description_color: color_t = card_text_description_color
        """
        The color used for any description text under the card images shown.
        """
        self.search_while_typing: bool = search_while_typing
        """
        Clarifies whether a preview of the cards matching the current search string
        should be used after every key input. Might be slowing down the program if True.
        """
        self.inner_area: pygame.Rect = None
        """
        The inner area is the frame inside the without the border.
        """

        #==================================
        # MENU LABEL
        #==================================

        self.menu_label_surface: pygame.Surface = None
        """
        The surface onto which the menu background will be rendered.
        """
        self.menu_label_highlighted_surface: pygame.Surface = None
        """
        The surface for the menu label onto which all
        menu elements will be rendered.
        """
        self.menu_label_frame: pygame.Rect = None
        """
        The frame used for rendering the menu.
        """
        self.menu_button_frame: pygame.Rect = None
        """
        Frame for rendering the menu button.
        Relative to self.inner_menu_label_frame.
        """
        self.deckname_frame: pygame.Rect = None
        """
        Frame for rendering the deckname.
        Relative to self.inner_menu_label_frame.
        """
        self.decksize_frame: pygame.Rect = None
        """
        Frame for rendering the decksize text.
        Relative to self.inner_menu_label_frame.
        """
        self.inner_menu_label_frame: pygame.Rect = None
        """
        The menu frame after applying self.menu_label_inner_hmargin and self.menu_label_inner_vmargin-
        """
        self.menu_label_height: int = -1
        """
        Actual height of the menu label.
        """
        self.menu_label_vmargin: float = menu_label_vmargin
        """
        The percentage of height used for the menu bar relative to self.inner_area.height.
        """
        self.menu_label_inner_hmargin: float = menu_label_inner_hmargin
        """
        The horizontal margin applied to self.menu_label_frame to create self.inner_menu_label_frame.
        """
        self.menu_label_inner_vmargin: float = menu_label_vmargin
        """
        The vertical margin applied to self.menu_label_frame to create self.inner_menu_label_frame.
        """
        self.menu_label_menu_button_hmargin: float = menu_label_menu_button_hmargin
        """
        The percentage of width occupied by the menu button relative to self.inner_menu_label_frame.width.
        """
        self.menu_label_decksize_text_hmargin: float = menu_label_decksize_text_hmargin
        """
        The percentage of width occupied by the decksize text relative to self.inner_menu_label_frame.width.
        """
        self.menu_label_color: color_t = menu_label_color
        """
        Color of the menu label.
        """
        self.menu_label_text_color: color_t = menu_label_text_color
        """
        Color of the text rendered onto the menu.
        """
        self.menu_label_alpha: int = menu_label_alpha
        """
        Alpha value of the menu label.
        """
        self.menu_label_highlighted_color: color_t = menu_label_highlighted_color
        """
        Color for the highlighted menu label, layed on top
        of the background.
        """
        self.menu_label_highlighted_alpha: int = menu_label_highlighted_alpha
        """
        Alpha value for the highlighted menu label, to blend
        into the menu label background.
        """

        #==================================
        # MENU BUTTON
        #==================================

        self.menu_button_unfocused_image: str = menu_button_unfocused_image
        """
        Path to the image used as the unfocused menu button image.
        """
        self.menu_button_focused_image: str = menu_button_focused_image
        """
        Path to the image used as the focused menu button image.
        """
        self.menu_button_unfocused_image_rendered: pygame.Surface = None
        """
        The rendered image of the unfocused menu button.
        """
        self.menu_button_unfocused_image_rendered_pos: point_t = None
        """
        Position if the unfocused menu button image,
        relative to self.inner_menu_label_frame
        """
        self.menu_button_focused_image_rendered: pygame.Surface = None
        """
        The rendered image of the focused menu button.
        """
        self.menu_button_focused_image_rendered_pos: point_t = None
        """
        Position if the focused menu button image,
        relative to self.inner_menu_label_frame
        """
        self.menu_button_focused_image_rendered_copy: pygame.Surface = None
        """
        Copy of the original unselected menu button surface for animation purposes.
        """
        self.menu_button_focused_image_rendered_pos_copy: point_t = None
        """
        Copy of the original unselected menu button position for animation purposes.
        """
        self.menu_button_frame_copy: pygame.Surface = None
        """
        Copy of the original selected menu button surface for animation purposes.
        """
        self.menu_button_selected_animation_duration: point_t = menu_button_selected_animation_duration
        """
        Copy of the original selected menu button position for animation purposes.
        """

        #==================================
        # DECKNAME
        #==================================

        self.deckname_rendered_and_positions: surface_with_position_t = None
        """
        The deckname surface and position relative to self.inner_menu_label_frame.
        """
        self.deckname_rendered_and_positions_copy: rendered_surface_position_tuples_t = None
        """
        Copy of the rendered deckname and its position,
        since the original is being swapped out during the animation.
        """

        #==================================
        # DECKSIZE
        #==================================

        self.decksize_rendered_and_positions: surface_with_position_t = None
        """
        The decksize surface and position relative to self.inner_menu_label_frame.
        """

        #==================================
        # DROPOWN MENU
        #==================================

        self.dropdown_menu: ScrollableDropdownMenu = None
        """
        The dropdown menu for the menu bar.
        """
        self.dropdown_menu_frame: pygame.Rect = None
        """
        The frame for the dropdown menu, relative to self.frame.
        """
        self.dropdown_menu_hlen_p: float = dropdown_menu_hlen_p
        """
        The horizontal percentage of self.inner_area,
        being the width of self.dropdown_menu_frame.
        """
        self.dropdown_menu_vlen_p: float = dropdown_menu_vlen_p
        """
        The vertical percentage of self.inner_area,
        being the height of self.dropdown_menu_frame.
        """
        self.dropdown_menu_tuple_options_dict: scrollable_tuple_options_t = None
        """
        The dropdown menu options as the tuple dictionary.
        """
        self.dropdown_menu_options_dict: scrollable_dropdown_options_t = None
        """
        The real dropdown menu created from self.dropdown_menu_tuple_options_dict.
        """

        #==================================
        # MAIN LIST
        #==================================

        self.main_list_frame: pygame.Rect = None
        """
        The frame where the cards will be displayed.
        Not directly, but after applying margins.
        """
        self.inner_main_list_frame: pygame.Rect = None
        """
        The actual frame where the cards will be displayed.
        Gets created after applying self.main_list_hmargin and
        self.main_list_vmargin to self.main_list_frame.
        """
        self.cardlist_frame: pygame.Rect = None
        """
        The frame of the main list, where the card previews are shown.
        """
        self.main_list_hmargin: float = main_list_hmargin
        """
        Horizontal margin for creating self.inner_main_list_frame.
        """
        self.main_list_vmargin: float = main_list_vmargin
        """
        Vertical margin for creating self.inner_main_list_frame.
        """
        self.main_list_separator_h_percentage: float = main_list_separator_h_percentage
        """
        Percentage of the width used for separating the card images as a
        percentage of self.inner_main_list_frame.width.
        """
        self.main_list_hseparator_width: int = -1
        """
        The actual width that will be distributed among the
        separator space. Calculated as main_list_separator_h_percentage * self.inner_main_list_frame.width
        """
        self.main_list_vseparator_height: int = -1
        """
        The actual height that will be distributed among the
        separator space. Calculated as main_list_separator_v_percentage * self.inner_main_list_frame.height
        """
        self.main_list_hseparator_size: int = -1
        """
        Actual width of the separator between 2 individual card previews.
        """
        self.main_list_vseparator_size: int = -1
        """
        Actual height of the separator between 2 individual card previews.
        """
        self.main_list_separator_v_percentage: float = main_list_separator_v_percentage
        """
        Percentage of the height used for separating the card images as a
        percentage of self.inner_main_list_frame.height.
        """
        self.main_list_color: color_t = main_list_color
        """
        Background color of the main list.
        """
        self.main_list_view_state: id_t = (main_list_view_state if main_list_view_state is not None else RenderableCardListviewer.SHOW_EACH_CARD)
        """
        The way the cards are portayed.
        """
        self.main_list_cwdith: int = -1
        """
        Actual width of a card preview in the main list.
        """
        self.main_list_cheight: int = -1
        """
        Actual height of a card preview in the main list.
        """

        #==================================
        # FULL IMAGE
        #==================================

        self.full_image_background_color: color_t = full_image_background_color
        """
        Background color when rendering the full image of a card.
        """
        self.full_image_background_alpha: color_t = full_image_background_alpha
        """
        The alpha value applied to the background when rendering the full image of a card.
        """
        self.full_image_surface: pygame.Surface = None
        """
        The surface, which will be shown when a images full image is required.
        """

        #==================================
        # CARD PREVIEW
        #==================================

        self.cardtext_hmargin: float = cardtext_hmargin
        """
        The cardtext horizontal margin applied to the rectangle
        the cards description text will be rendered into.
        """
        self.cardtext_vmargin: float = cardtext_vmargin
        """
        The cardtext vertical margin applied to the rectangle
        the cards description text will be rendered into.
        """
        self.cardshadow_hoffset_p: float = cardshadow_hoffset_p
        """
        The percentage of the horizontal offset of the cardshadow vs the card.
        """
        self.cardshadow_voffset_p: float = cardshadow_voffset_p
        """
        The percentage of the vertical offset of the cardshadow vs the card.
        """
        self.cardshadow_alpha: int = cardshadow_alpha
        """
        The alpha value of the cardshadow.
        """
        self.subtext_margin: float = subtext_margin
        """
        The percentage of height the description text of a card occupies.
        Relative to self.main_list_cheight.
        """
        self.selected_card_size_increase_percentage: float = selected_card_size_increase_percentage
        """
        The percentage of the size increase when a card is in the selected state.
        """
        self.selected_cardshadow_color: color_t = selected_cardshadow_color
        """
        Color for the selected cardshadow.
        """
        self.selected_cardshadow_alpha: int = selected_cardshadow_alpha
        """
        Alpha value of the selected cardshadow.
        """
        self.subtext_width: int = -1
        """
        Actual width of the portion designated to the subtext
        of a card preview.
        """
        self.subtext_height: int = -1
        """
        Actual height of the portion designated to the subtext
        of a card preview.
        """
        self.cardimage_width: int = -1
        """
        Actual width of the portion designated to the image
        of a card preview.
        """
        self.cardimage_height: int = -1
        """
        Actual height of the portion designated to the image
        of a card preview.
        """

        #==================================
        # BORDER
        #==================================

        self.border_frame_margin: float = border_frame_margin
        """
        For calculating the size of the border, relative to self.width and self.height.
        """
        self.border_width: int = -1
        """
        The actual border width.
        """
        self.border_height: int = -1
        """
        The actual border height.
        """
        self.border_frame_color: color_t = border_frame_color
        """
        Color of the border frame.
        """
        self.border_frame_outline_margin: float = border_frame_outline_margin
        """
        The percentage used to calculate the border outline size.
        Relative to self.border_width, self.border_height.
        """
        self.border_outline_width: int = -1
        """
        Actual width of the border outline.
        """
        self.border_outline_height: int = -1
        """
        Actual height of the border outline.
        """
        self.used_border_outline_size: int = -1
        """
        The actual size of the outline,
        as a minimum margin of self.border_width, self.border_height
        """
        self.border_frame_outline_color: color_t = border_frame_outline_color
        """
        The color of the outline of the border frame.
        """
        self.inner_border_corners: list[point_t] = []
        """
        List of the position of the inner border corners,
        in clockwise direction.
        """
        self.border_lines: list[pygame.Rect] = []
        """
        The rectangles to draw the border.
        """

        #==================================
        # INFO FRAME
        #==================================

        self.info_text_frame: pygame.Rect = None
        """
        Frame where the info text will be rendered.
        """
        self.info_text_surface: pygame.Surface = None
        """
        Surface for the info text.
        """
        self.info_text_rendered: rendered_surface_position_tuples_t = None
        """
        The actual rendered info text.
        """
        self.info_text_surface_alpha: int = info_text_surface_alpha
        """
        Alpha value of the info text surface.
        """
        self.info_text_hlen_p: float = info_text_hlen_p
        """
        Width of the info text as a percentage relative to self.width.
        """
        self.info_text_vlen_p: float = info_text_vlen_p
        """
        Height of the info text as a percentage relative to self.height.
        """
        #info text colors
        self.info_text_color: color_t = info_text_color
        """
        The standard info text color for the text.
        """
        self.info_text_warning_color: color_t = info_text_warning_color
        """
        The color for the info text for when a warning is displayed.
        """
        self.info_text_error_color: color_t = info_text_error_color
        """
        The color for the info text for when an error is displayed.
        """
        #fadeout time saved
        self.current_info_text_fadeout_duration: float = 0
        """
        The currently saved fadeout duration, since different
        Info texts could have different fadeout durations.
        """
        self.info_text_fading_clock: Clock = Clock()
        """
        The clock for calculating the info tetx fadeout.
        """

        #==================================
        # INTERNAL VARIABLES
        #==================================

        self.selected_card_index: int = 0
        """
        The index of the currently selected card.
        """
        self._state: id_t = RenderableCardListviewer.NOTHING_FOCUSED
        """
        The state of this frame.
        Protected variable.
        self.state will be used as the state variable,
        and changing self._state will change self.prev_state
        """
        self.prev_state: id_t = None
        """
        The previous state, saved.
        """
        self.main_list_yscroll: int = 0
        """
        Saves the amount scrolled on the current main list.
        """
        self.main_list_yscroll_copy: int = 0
        """
        Temporary copy of the yscroll, used for animations.
        """
        self.card_render_cache: dict[str, tuple[ pygame.Surface, point_t, pygame.Rect ]]  = {}
        """
        A cache for saving the rendered cards.
        Structured as:
                        image_path: (image_surface, image_pos, image_rect)

        The image_pos is relative to image_rect, and image_rect
        is only (0, 0, card_width, card_height)
        """
        self.text_render_cache: dict[Any, tuple[rendered_surface_position_tuples_t, pygame.Rect]] = {}
        """
        A cache for saving rendered texts.
        The keys might be different, depending
        on the current view state.
        """
        self.main_list_cards_dict: dict[int, tuple[int, pygame.Rect, pygame.Rect, int]] = {}
        """
        The dictionary for accessing the cards and their
        data by their id.
        Structured as:

        id: (self.main_list_cards_index, rectangle_for_card_image, rectangle_for_text_surfaces, y-position)

        The rectangles are relative to self.frame_dim
        """
        self.main_list_cards_rects: dict[int, list[ tuple[int, int, pygame.Rect, pygame.Rect] ]] = {}
        """
        The dictionary for accessing rows of cards ids and their rects.
        Structured as:

        y_position: [(self.main_list_cards_index, card_id, image rect, text rect), ...]

        image and text rect are relative to self.frame_dim.
        """
        self.rendered_rows: list[ tuple[ int, int, int, pygame.Rect, pygame.Rect ] ] = []
        """
        Saving the rendered rows for later access.
        Structured as:
        [(y_position, card_id, self.main_list_cards_index, image_rect, text_rect), ...]

        image and text rect are relative to self.frame_dim.
        """
        self.main_list_cards: cardlist_t = []
        """
        The list of the currently loaded cards of the group, loaded as [(cardclass, amount)],
        """
        self.n_cards_shown: int = 0
        """
        The number of individual card previews currently inside the main list.
        """
        self.focused_text_input_subframe: RenderableCardListviewer.FocusedTextInputFrame = None
        """
        Reference to the FocusedTextInputFrame if any kind of textinput
        is required.
        """
        self.fastscroll_enabled: bool = False
        """
        If fastscroll is enabled self.fastscroll_duration will be used instead
        of self.rowscroll_duration.
        """
        self.group_creation_enabled: bool = group_creation_enabled
        """
        Determines whether this frame's group creation feature is enabled.
        """
        self.group_selection_enabled = group_selection_enabled
        """
        Determines whether this frame's group selection feature is enabled.
        """
        self.card_pressed_size_change_percentage: float = card_pressed_size_change_percentage
        """
        The percentage of size change of the card for its pressed animation.
        """

        #==================================
        # TIME CONTROL
        #==================================
        self.intro_delay: float = 100#ms
        """
        The intro delay.
        """
        self.intro_delay_clock: Clock = Clock()
        """
        The intro delay clock.
        """
        self.key_delay: float = key_delay
        """
        The delay between picking up key press events.
        """
        self.key_clock: Clock = Clock()
        """
        The clock for enforcing the delay between key press detection.
        """
        self.rowscrolling_clock: Clock = Clock()
        """
        The clock for the rowscrolling animation.
        """
        self.rowscrolling_duration: float = rowscrolling_duration
        """
        Duration of the rowscrolling animation of one row.
        """
        self.rowscrolling_all_duration: float = rowscrolling_all_duration
        """
        The duration of the animation when scrolling up all rows.
        """
        self.fastscroll_duration: float = fastscroll_duration
        """
        The scrolling duration for when fastscroll is enabled.
        """
        self.rowscroll_copy: float = None
        """
        A copy of the original self.rowscroll_duration,
        when it needs to be swapped out for an animation.
        """
        self.deckname_selected_animation_clock: Clock = Clock()
        """
        Clock for the select animation of the deck name in the menu bar.
        """
        self.deckname_selected_animation_duration: float = deckname_selected_animation_duration
        """
        Duration of the select animation of the deck name in the menu bar.
        """
        self.menu_button_selected_animation_clock: Clock = Clock()
        """
        The clock for the menu button selection animation.
        """
        self.enter_clock: Clock = Clock()
        """
        The clock for determining if an enter press is
        a long enter press.
        """
        self.time_until_long_enter_pressed: float = time_until_long_enter_pressed
        """
        If enter is pressed, after self.time_until_long_enter_pressed
        ms of pressing enter the enter press is considered  a long enter pressed.
        """
        self.enter_pressed_on_card_percentage: float = 0
        """
        The percentage of time passed until the enter press becomes a
        long enter press.
        """
        self.card_snapback_clock: Clock = Clock()
        """
        The clock for the snapback animation.
        """
        self.card_snapback_duration: float = card_snapback_duration
        """
        The duration of the snapback duration of a card.
        """

        self.cards_dict_before_enter: tuple[int, pygame.Rect, pygame.Rect, int] = None
        """
        Saving the entry of the selected card in self.main_list_cards_dict,
        for restoring after any animation involving this card.
        """
        self.cards_rects_before_enter: list[ tuple[int, int, pygame.Rect, pygame.Rect] ] = None
        """
        Saving the entry of the selected card in self.main_list_cards_rects,
        for restoring after any animation involving this card.
        """
        self.cards_rects_before_enter_index: int = -1
        """
        The saved main list index before any selection process.
        """

        #==================================
        # FINAL ADJUSTMENTS
        #==================================

        #adding the full cardlist to the group
        self.groups[RenderableCardListviewer.FULL_CARDLIST_NAME] = {
                                                                    RenderableCardListviewer.CARDLIST_KEY: self.full_cardlist,
                                                                    RenderableCardListviewer.MUTABLE_KEY: False,
                                                                    RenderableCardListviewer.IS_COPYLIST_KEY: True,
                                                                    RenderableCardListviewer.RENAMABLE_KEY: False #not renamable
                                                                    }

        #setting the shown group
        self.shown_group = (shown_group if shown_group is not None else list(self.groups.keys())[0])

        #rerendering
        self.rerender()

    #==================================
    # PROPERTIES
    #==================================

    @property
    def state(self) -> id_t:
        """
        For getting self._state via self.state.
        """
        return self._state

    @state.setter
    def state(self, new_state: id_t) -> None:
        """
        Sets the new state, updates self.prev_state.
        """
        self.prev_state = self._state
        self._state = new_state

    #==================================
    # VALIDITY CHECKS
    #==================================

    def _check_validity(self) -> None:
        """
        Checks the validity of the own variables.
        """
        if len(self.groups) == 0:
            raise RuntimeError("You need at least one group")
        if len(self.groups) > self.max_group_number:
            raise RuntimeError("Too many groups. Adjust your max_group_size")
        if self.cards_per_line <= 0 or self.cards_per_column <= 0:
            raise RuntimeError("cards_per_line and cards_per_column have to be greater than 0")

        #checking the group and full cardlists consistency.
        #if the group has a cardclass where the amount is greater than the full cardlist
        #and is no copylist, its invalid.

        for (groupname, group) in self.groups.items():

            #checking if it is copylist
            is_copylist: bool = group[RenderableCardListviewer.IS_COPYLIST_KEY]
            if is_copylist:
                #skip copylists
                continue

            #otherwise, check amounts
            cardlist: dict_cardlist_t = group[RenderableCardListviewer.CARDLIST_KEY]
            for (cardclass, amount) in cardlist.items():

                if amount > self.full_cardlist[cardclass]: #a group has more of this card than allowed: error
                    raise RuntimeError(
                                        f"ERROR:    Group {groupname} has more copies of {str(cardclass)} than the full cardlist.\n"\
                                        f"          {groupname}: {str(amount)} > full_cardlist: {str(self.full_cardlist[cardclass])}"
                                        )

        #no error, groups were valid

    #==================================
    # RENDERING
    #==================================

    @override
    def rerender(self) -> None:
        """
        Rerendering
        """

        """
        VALIDITY CHECK
        """
        self._check_validity()

        """
        INFO TEXT
        """

        iheight: int = int(self.height * self.info_text_vlen_p)

        self.info_text_frame = pygame.Rect( 0,
                                            self.height - iheight,
                                            int(self.width * self.info_text_hlen_p),
                                            iheight
                                            )

        self.info_text_surface = pygame.Surface((self.info_text_frame.width, self.info_text_frame.height), pygame.SRCALPHA)
        self.info_text_rendered = None

        """
        FULL FRAME + BORDER FRAME
        """

        #resetting card index
        self.selected_card_index = 0
        #creating the full image surface
        self.full_image_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        #getting border width and height
        self.border_width = int(self.border_frame_margin * self.width)
        self.border_height = int(self.border_frame_margin * self.height)
        #the inner area is the frame inside without the border
        self.inner_area = pygame.Rect(
                                        self.x + self.border_width,
                                        self.y + self.border_height,
                                        self.width - 2*self.border_width,
                                        self.height - 2*self.border_height

                                        )
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
        def rs(p1: point_t, p2: point_t) -> pygame.Rect:
            """
            This inner function calculates
            the rectangles for the inner outline.
            """

            x: int = p1[0]
            y: int = p1[1]
            #x and y of the first point

            w: int = p2[0] - p1[0]
            if w == 0:
                w = self.used_border_outline_size

            h: int = p2[1] - p1[1]
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

            #x, y are the top left, w and h the width
            #if any of the width or height are the same,
            #they are on top of each other and need to be
            #expanded by the used border outline size

            return pygame.Rect(x, y, w, h)

        #creating the render rectangles
        for i in range(len(self.inner_border_corners)+1):
            #wrap around by one to connect the last point with the first

            i1: int = i % len(self.inner_border_corners)
            i2: int = (i+1) % len(self.inner_border_corners)
            #indices
            p1: point_t = None #the first point
            p2: point_t = None #the second point
            p1, p2 = self.inner_border_corners[i1], self.inner_border_corners[i2]
            #constructing and adding a rect to the border lines.
            self.border_lines.append((rs(p1, p2), self.border_frame_outline_color))

        """
        MENU LABEL AND INNER MENU LABEL
        """
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
        self.menu_button_frame,\
        self.deckname_frame,\
        self.decksize_frame = graphics.split_rect_horizontally(
                                                                    pygame.Rect(
                                                                                    self.inner_menu_label_frame.x - self.menu_label_frame.x,
                                                                                    self.inner_menu_label_frame.y - self.menu_label_frame.y,
                                                                                    self.inner_menu_label_frame.width,
                                                                                    self.inner_menu_label_frame.height
                                                                    ),

                                                                    [
                                                                        self.menu_label_menu_button_hmargin,
                                                                        1.0-(self.menu_label_menu_button_hmargin + self.menu_label_decksize_text_hmargin),
                                                                        self.menu_label_decksize_text_hmargin
                                                                    ]
                                                                )
        #now rendering the menu items
        #rendering the menu button
        self.menu_button_unfocused_image_rendered,\
        self.menu_button_unfocused_image_rendered_pos = graphics.img_load_and_position_smoothscale(self.menu_button_unfocused_image, self.menu_button_frame)
        self.menu_button_focused_image_rendered,\
        self.menu_button_focused_image_rendered_pos = graphics.img_load_and_position_smoothscale(self.menu_button_focused_image, self.menu_button_frame)

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
        self.create_deckname_text()
        #rendering the decksize
        self.create_decksize_text()
        #creating the cardmenu
        self.create_dropdown_menu()
        #now getting the card positions
        self.recalculate_main_list_positions()

        self.key_clock.start()
        self.intro_delay_clock.start()
        #prerendering
        self.raise_prerender_flag()

    @override
    def prerender(self) -> None:
        """
        Prerendering.
        """

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

    def create_deckname_text(self) -> None:
        """
        Creates self.deckname_rendered_and_positions.
        """

        self.deckname_rendered_and_positions = graphics.render_page_from_chars_color(
                                                                                        font=self.font,
                                                                                        page=[[(self.shown_group, self.menu_label_text_color)]],
                                                                                        frame=self.deckname_frame,
                                                                                        text_color=self.menu_label_text_color,
                                                                                        centered=True,
                                                                                        vertical_centered=True
                                                                                    )
    def create_decksize_text(self):
        """
        Creates self.decksize_rendered_and_positions.
        """

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

    def recalculate_main_list_positions(self) -> None:

        """
        The method to recalculate
        the rectangles and positions of the card previews.
        """
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

        """
        Creating and assigning card previews.
        """

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

    def render_list_with_yscroll(self) -> None:
        """
        Renders the card previews,
        iterates over each row and only
        renders it if it is visible.
        Takes precached variables whenever possible.
        """

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
                    img, img_pos = graphics.img_load_and_position_smoothscale(cinfo.card_image_path, pygame.Rect(0, 0, img_rect.width, img_rect.height))
                    self.card_render_cache[cinfo.card_image_path] = (img, img_pos, img_rect.copy())

                img_render_pos = (img_rect.x + img_pos[0], img_rect.y + img_pos[1] + self.main_list_yscroll)

                shadow_rect = None


                if self.selected_card_index == id_index and self.state == RenderableCardListviewer.MAIN_LIST_FOCUSED:

                    #scaling up selected card
                    img_x_inc, img_y_inc = img.get_width() * 0.1, img.get_height() * 0.1
                    img = pygame.transform.scale(img, (img.get_width() + img_x_inc, img.get_height() + img_y_inc))
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

    def render_full_image(self, cinfo: Renderable_CardInfo) -> None:
        """
        Renders the image of the given cardinfo as a full image.
        """
        cw, ch = self.width // 2, int(self.height * 0.9)
        center_frame = pygame.Rect(cw // 2, (self.height - ch) // 2, cw, ch)
        cimage = cinfo.get_card_image_rendered(center_frame)
        cpos = graphics.get_center_with_surface(cimage, center_frame)

        self.full_image_surface.fill((*Colors.BLACK, 200))
        self.full_image_surface.blit(cimage, cpos)

    #==================================
    # GROUP ACTIONS
    #==================================

    def reload_current_group(self) -> None:
        """
        Does all rerendering needed after
        changing the current group,
        or anything in the current group.
        """

        self.create_deckname_text()
        self.create_decksize_text()
        self.create_dropdown_menu()
        self.recalculate_main_list_positions()

        self.raise_prerender_flag()

    def get_shown_group_decksize(self) -> int:
        """
        Returns the number of cards in the currently shown group.
        """
        return sum(self.groups[self.shown_group][RenderableCardListviewer.CARDLIST_KEY].values())

    def add_group(
                    self,
                    groupname: str,
                    cardlist: dict_cardlist_t = None,
                    mutable: bool = True,
                    is_copylist: bool = False,
                    renamable: bool = True

                    ) -> bool:
        """
        This creates a mew group with the given variables.
        Returns True on success, False on failure.
        """

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

    #==================================
    # INFO TEXT ACTIONS
    #==================================

    #for getting the info text flag
    def info_text_active(self) -> bool:
        """
        If the info text is currently active or not.
        """
        return (self.info_text_rendered is not None)

    def print_info_text(
                            self,
                            text_page: colored_page_t,
                            text_color: color_t,
                            fade_duration: float
                        ) -> None:
        """
        Creates an Info text with text_page
        as text, text_color as backup color,
        and fade_duration as the duration this info text stays on screen.
        """
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

    def info_text_tick(self) -> None:
        """
        Handles the info text updates.
        """

        percentage = self.info_text_fading_clock.elapsed() / self.current_info_text_fadeout_duration

        if percentage >= 1.0:
            self.info_text_rendered = None
        else:
            fade = int((1.0 - percentage) * 255)
            self.info_text_surface.set_alpha(fade)

    #==================================
    # DROPDOWN MENU ACTIONS
    #==================================

    def create_dropdown_menu_dict(self) -> scrollable_tuple_options_t:
        """
        Creates the tuple options for the own dropdown menu.
        """

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


    def handle_dropdown_menu_selection(self, event: pygame.event.Event) -> None:
        """
        Handles actions taken when a event
        from the own dropdown menu is received.
        """

        if event.type == ScrollableDropdownMenu.EventTypes.SELECT_ANIMATION_ENDED:
            #selection was done
            if self.state == RenderableCardListviewer.DROPDOWN_MENU_ACTIVE:
                #getting the selected instance
                full_trace: list[tuple[str]] = event.selected_option_tuples
                selection: tuple[str] = full_trace[-1]

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
                elif full_trace[0] == RenderableCardListviewer.MENU_OPTIONS.SELECT_GROUP_OPTION_KEY:

                    self.shown_group = selection[0]
                    self.reload_current_group()

                elif selection == RenderableCardListviewer.MENU_OPTIONS.CREATE_GROUP_OPTION_KEY:
                    self.initialize_deck_creation_frame()

                self.reload_dropdown_menu_with_progress()



    def create_dropdown_menu(self) -> None:
        """
        Creates the own dropdown menu.
        """
        self.dropdown_menu_tuple_options_dict = self.create_dropdown_menu_dict()
        self.dropdown_menu_options_dict = ScrollableDropdownMenu.page_keys_to_dropdownkey(
                                                                                            self.dropdown_menu_tuple_options_dict,
                                                                                            Colors.WHITE,
                                                                                            Colors.BLACK
                                                                                            )
        #creating the dropdown menu
        self.dropdown_menu_frame = pygame.Rect(
                                                    self.inner_area.x,
                                                    self.inner_area.y + self.menu_label_height,
                                                    int(self.dropdown_menu_hlen_p * self.inner_area.width),
                                                    int(self.dropdown_menu_vlen_p * self.inner_area.height)
                                            )

        self.dropdown_menu = ScrollableDropdownMenu(
                                                        frame_dim=self.dropdown_menu_frame,
                                                        options=self.dropdown_menu_options_dict,
                                                        parent_frame=self,
                                                        background_color=Colors.BLACK,
                                                        highlighted_background_color=Colors.WHITE
                                                    )

    def reload_dropdown_menu_with_progress(self) -> None:
        """
        Reloads the dropdown menu whilst keeping the
        selection state the same.
        """
        if self.dropdown_menu is not None:

            trace: scrollable_option_trace_t = self.dropdown_menu.get_option_trace()
            self.create_dropdown_menu()
            self.dropdown_menu.select_option_expanded(trace)

    #==================================
    # TICK FUNCTIONS AND ANIMATION HANDLING
    #==================================

    @override
    def tick(self) -> None:
        """
        Tick function.
        """

        if self.intro_delay_clock.elapsed() >= self.intro_delay:
            self.manage_pygame_events()

        if self.exit_flag_raised():
            return None

        if self.is_focused():

            """
            INFO TEXT
            """

            if self.info_text_active():
                self.info_text_tick()

            """
            DROPDOWN MENU
            """

            if self.state == RenderableCardListviewer.DROPDOWN_MENU_ACTIVE:
                self.dropdown_menu.tick()

                #dropdown events
                dropdown_events = self.dropdown_menu.poll_events()

                for event in dropdown_events:
                    self.handle_dropdown_menu_selection(event)

            """
            STATE ACTIONS
            """
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
                            self.create_deckname_text()
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

        self.raise_prerender_flag()

        #prerendering
        if self.prerender_flag_raised():
            self.prerender()
            self.reset_prerender_flag()

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
        self.menu_button_focused_image_rendered, self.menu_button_focused_image_rendered_pos = graphics.img_load_and_position_smoothscale(self.menu_button_focused_image, self.menu_button_frame)

    def finalize_menu_button_selected_animation(self):

        self.menu_button_focused_image_rendered = self.menu_button_focused_image_rendered_copy
        self.menu_button_focused_image_rendered_pos = self.menu_button_focused_image_rendered_pos_copy
        self.menu_button_frame = self.menu_button_frame_copy
        self.state = RenderableCardListviewer.DROPDOWN_MENU_ACTIVE
        self.dropdown_menu.unselect_options()

    def prerender_full_image(self):

        self.full_image_surface.fill((*self.full_image_background_color, self.full_image_background_alpha))
        #rendering the image
        main_list_card_idx = self.main_list_cards_dict[self.selected_card_index][0]
        cinfo = self.main_list_cards[main_list_card_idx][0].info()

        img_path = cinfo.card_image_path

        isurf, ipos = graphics.img_load_and_position_smoothscale(img_path, self.frame_dim)
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
