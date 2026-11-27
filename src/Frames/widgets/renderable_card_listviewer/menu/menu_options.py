"""
This file provides the MENU_OPTIONS
class, filled with the keys as tuples,
"""
from Frames.widgets.scrollable_dropdown_menu import (
    ScrollableDropdownMenu,
    scrollable_tuple_options_t,
    scrollable_dropdown_options_t,
    scrollable_option_trace_t,
    scrollable_option_trace_element_t
)

# ==================================
# MENU OPTIONS
# ==================================

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

    SHOWN_AMOUNT: int = 5  # shown amount of options

    # sorting
    SORTING_OPTION_KEY: tuple[str] = ("Sort Group",)
    # suboptions
    RANDOMIZED_SORTING: tuple[str] = ("Randomized",)
    NAME_DESCENDING_SORTING: tuple[str] = ("Name Descending",)
    NAME_ASCENDING_SORTING: tuple[str] = ("Name Ascending",)
    AMOUNT_DESCENDING_SORTING: tuple[str] = ("Amount Descending",)
    AMOUNT_ASCENDING_SORTING: tuple[str] = ("Amount Ascending",)
    # shown_amount
    SORTING_OPTIONS_SHOWN_AMOUNT: int = 5

    # display type
    DISPLAY_TYPE_KEY: tuple[str] = ("Display Type",)
    # options for display type
    SHOW_EACH_CARD_DISPLAY_TYPE: tuple[str] = ("Show Each Card",)
    SHOW_WITH_AMOUNT_DISPLAY_TYPE: tuple[str] = ("Show With Amount",)
    # shown amount
    DISPLAY_OPTIONS_SHOWN_AMOUNT: int = 5

    # group selection
    SELECT_GROUP_OPTION_KEY: tuple[str] = ("Select Group",)
    SELECT_GROUP_OPTIONS_SHOWN_AMOUNT: int = 5
    # group creation
    CREATE_GROUP_OPTION_KEY: tuple[str] = ("Create Group",)
    # group deletion
    DELETE_GROUP_OPTION_KEY: tuple[str] = ("Delete Group",)
    DELETE_GROUP_OPTIONS_SHOWN_AMOUNT: int = 5
    # group importing
    IMPORT_GROUP_OPTION_KEY: tuple[str] = ("Import ",)
    IMPORT_GROUP_OPTIONS_SHOWN_AMOUNT: int = 5
    # show main list state
    MAIN_LIST_STATE_INFO_PANEL_KEY: tuple[str] = (
        "Editing State Info Panel",)

    # options in the main list state
    SHOW_MAIN_LIST_STATE_KEY: tuple[str] = ("Show Editing State",)
    HIDE_MAIN_LIST_STATE_KEY: tuple[str] = ("Hide Editing State",)

    MAIN_LIST_STATE_ACTION_SHOWN_AMOUNT: int = 5

    # editing state
    CHANGE_EDITING_STATE_KEY: tuple[str] = ("Change Editing State",)

    # all editing options
    CHANGE_EDITING_TO_INFO_STATE_KEY: tuple[str] = ("Info State",)
    CHANGE_EDITING_TO_SELECTION_STATE_KEY: tuple[str] = (
        "Selection State",)
    CHANGE_EDITING_TO_MOVING_STATE_KEY: tuple[str] = ("Moving State",)

    CHANGE_EDITING_STATE_SHOWN_AMOUNT: int = 5
