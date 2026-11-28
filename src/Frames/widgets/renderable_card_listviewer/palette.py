"""
This file provides a palette, meaning all visual information for the RenderableCardListviewer.
"""
from __future__ import annotations
from typing import Type, Any, Callable, override, TYPE_CHECKING

from constants import Colors, Fonts

from Frames.widgets.renderable_card_listviewer.menu.menu_palette import MenuPalette
from Frames.widgets.renderable_card_listviewer.info_text import InfoTextPalette

if TYPE_CHECKING:
    from constants import (
                            id_t,
                            color_rgb_t,
                            color_rgba_t,
                            color_t
                            )

class Palette:

    def __init__(
                    self,
                    #the used font
                    font: pygame.font.Font = Fonts.STANDARD_FONT,
                    # card dimensions
                    cards_per_line: int = 8,
                    cards_per_column: int = 4,

                    # full image data
                    full_image_background_color: color_rgb_t = Colors.BLACK,
                    full_image_background_alpha: int = 180,

                    #cards
                    #the margins for the subtext of the card previews.
                    cardtext_hmargin: float = 0.2,
                    cardtext_vmargin: float = 0.2,
                    # description text shown under a card
                    card_text_description_color: color_rgb_t = Colors.BLACK,
                    # margin between the image and any text rendered below
                    subtext_margin: float = 0.2,

                    # shadow offsets for the cards, relative to tbe card length
                    cardshadow_hoffset_p: float = 0.075,
                    cardshadow_voffset_p: float = 0.075,
                    cardshadow_alpha: int = 120,
                    selected_card_size_increase_percentage: float = 0.05,
                    selected_cardshadow_alpha: int = 120,
                    # percentage when card is selected for the selection animation.
                    card_pressed_size_change_percentage: float = 0.25,

                    #main list

                    # background color of the list
                    main_list_color: color_rgba_t = Colors.rgba(Colors.CYAN, 255),

                    # margins for the main list
                    main_list_hmargin: float = 0.1,
                    main_list_vmargin: float = 0.1,
                    # margins for the cards inside the main list
                    inner_frame_hmargin: float = 0.1,
                    inner_frame_vmargin: float = 0.05,

                    # how much the cards should be separated, based on the cardlist width and height
                    #e.g. if the percentage = 0.1, 10% of pixels will be used for the space between cards
                    main_list_separator_h_percentage: float = 0.1,
                    main_list_separator_v_percentage: float = 0.1,

                    #border

                    # what percentage of width and height is used for the border
                    border_frame_margin: float = 0.02,
                    # fill color of the border
                    border_frame_color: color_rgb_t = Colors.DARK_CYAN,
                    # the frame outline is drawn once on the outer edge and once in the inner edge
                    border_frame_outline_margin: float = 0.2, #relative to the whole border size
                    border_frame_outline_color: color_rgb_t = Colors.BLACK,

                    #popup

                    # popup margins
                    popup_hmargin: float = 0.5,  # Horizontal margin for the popup frame dim
                    popup_vmargin: float = 0.4,  # Vertical margin for the popup frame dim

                    # main list state

                    # colors for the main list states
                    info_main_list_state_color: color_rgb_t = Colors.WHITE,
                    select_main_list_state_color: color_rgb_t = Colors.ORANGE,
                    # color for the the cards in the selected state
                    card_selected_in_selection_state_color: color_rgb_t = Colors.YELLOW,

                    # main list state info panel

                    # Percentage of width used relative to self.main_list_frame.
                    main_list_state_info_panel_width_p: float = 0.2,
                    # Percentage of height used relative too self.main_list_frame.
                    main_list_state_info_panel_height_p: float = 0.1,
                    # Horizontal margin for the info panel
                    main_list_state_info_panel_hmargin: float = 0.1,
                    # Vertical margin for the info panel
                    main_list_state_info_panel_vmargin: float = 0.25,
                    # Alpha value for the info panel.
                    main_list_state_info_panel_alpha: int = 200,
                    # Background color for the info panel.
                    main_list_state_info_panel_background_color: color_rgb_t = Colors.BLACK,
                    # Outline color of the info panel.
                    main_list_state_info_panel_outline_color: color_rgb_t = Colors.BLACK,
                    # if the info panel starts out shown or not.
                    main_list_state_info_panel_shown: bool = True,

                    #animation times

                    # ms when scrolling one row upor down, this is the duration it takes
                    rowscrolling_duration: float = 300,
                    rowscrolling_all_duration: float = 500,  # ms #rowscrolling all rows up
                    fastscroll_duration: float = 50,  # ms for fast scrolling

                    # ms, time it takes for a card to snap back and do the card pressed animation in reverse
                    card_snapback_duration: float = 200,
                    cardinfo_frame_sliding_duration: float = 400,  # ms
                    # ms, how long until the long enter state is reached
                    time_until_long_enter_pressed: float = 400,

                    #the menu palette
                    menu_palette: MenuPalette = None,
                    info_text_palette: InfoTextPalette = None
                ):

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
        self.card_text_description_color: color_rgb_t = card_text_description_color
        """
        The color used for any description text under the card images shown.
        """

        # ==================================
        # POPUP
        # ==================================

        self.popup_hmargin: float = popup_hmargin
        """
        Horizontal margin for the popup frame dim,
        relative to self.inner_frame.
        """
        self.popup_vmargin: float = popup_vmargin
        """
        Vertical margin for the popup frame dim,
        relative to self.inner_frame.
        """
