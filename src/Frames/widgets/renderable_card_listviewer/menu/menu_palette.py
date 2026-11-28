"""
The palette for the menu label,
defining its looks.
"""
from __future__ import annotations
from typing import Type, Any, override, Callable, TYPE_CHECKING

from constants import Colors

if TYPE_CHECKING:
    from constants import color_rgb_t, color_rgba_t, color_t

class MenuPalette:

    def __init__(
                    self,
                    menu_label_menu_button_hmargin: float = 0.2,
                    #percentage of width used for the menu button,
                    #relative to the width of the menu label
                    menu_label_decksize_text_hmargin: float = 0.2,
                    #percentage of width used for the decksize text,
                    #relative to the width of the menu label
                    menu_label_vmargin: float = 0.1,
                    #percentage of height used for the menu label relative to the inner area
                    #in renderable_card_listviewer
                    menu_label_highlighted_color: color_rgb_t = Colors.YELLOW,
                    #the color that will be layed behind the currently
                    #selected menu widget.
                    menu_label_highlighted_alpha: int = 64,
                    #the alpha for the background of the currently highlighted widget

                    #the margins that will be applied to the menu label,
                    #so that widgets are not directly at the borders
                    menu_label_inner_hmargin: float = 0.1,
                    menu_label_inner_vmargin: float = 0.1,
                    #background color of the menu label,
                    menu_label_color: color_rgb_t = Colors.BLACK,
                    menu_label_text_color: color_rgb_t = Colors.WHITE,
                    # alpha of the menu label
                    menu_label_alpha: int = 200,
                    #menu button
                    # menu label assets
                    menu_button_unfocused_image: str = MENU_BUTTON_UNFOCUSED_IMAGE,
                    menu_button_focused_image: str = MENU_BUTTON_FOCUSED_IMAGE,
                    #deckname

                    # in which color the group name will be shown
                    group_name_color: color_rgb_t = Colors.WHITE,

                    # determines if while typing the searched up cards should be shown
                    search_while_typing: bool = True,

                    # dropdown menu
                    dropdown_menu_hlen_p: float = 0.5, #relative to the main list width
                    dropdown_menu_vlen_p: float = 0.4, #relative to the main list height.

                    #animation times

                    deckname_selected_animation_duration: float = 400,  # ms
                    menu_button_selected_animation_duration: float = 400  # ms
                    ):

        self.group_name_color: color_rgb_t = group_name_color
        """
        Color the name of the group will be shown in.
        """
        self.search_while_typing: bool = search_while_typing
        """
        Clarifies whether a preview of the cards matching the current search string
        should be used after every key input. Might be slowing down the program if True.
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
        self.menu_label_color: color_rgb_t = menu_label_color
        """
        Color of the menu label.
        """
        self.menu_label_text_color: color_rgb_t = menu_label_text_color
        """
        Color of the text rendered onto the menu.
        """
        self.menu_label_alpha: int = menu_label_alpha
        """
        Alpha value of the menu label.
        """
        self.menu_label_highlighted_color: color_rgb_t = menu_label_highlighted_color
        """
        Color for the highlighted menu label, layed on top
        of the background.
        """
        self.menu_label_highlighted_alpha: int = menu_label_highlighted_alpha
        """
        Alpha value for the highlighted menu label, to blend
        into the menu label background.
        """

        # ==================================
        # MENU BUTTON
        # ==================================

        self.menu_button_unfocused_image: str = menu_button_unfocused_image
        """
        Path to the image used as the unfocused menu button image.
        """
        self.menu_button_focused_image: str = menu_button_focused_image
        """
        Path to the image used as the focused menu button image.
        """
        self.menu_button_selected_animation_duration: float = menu_button_selected_animation_duration
        """
        Copy of the original selected menu button position for animation purposes.
        """

        # ==================================
        # DECKNAME
        # ==================================

        self.deckname_selected_animation_duration: float = deckname_selected_animation_duration
        """
        Duration of the select animation of the deck name in the menu bar.
        """
