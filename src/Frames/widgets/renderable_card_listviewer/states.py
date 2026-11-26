"""
Provides the states used in
renderable_card_listviewer.
"""

from constants import id_t, R_ID

# ==================================
# STATES
# ==================================

NOTHING_FOCUSED: id_t = R_ID()  # nothing is focused
MAIN_LIST_FOCUSED: id_t = R_ID()  # the cards in the list are focused
MENU_BUTTON_FOCUSED: id_t = R_ID()  # menu button in the menu label
MENU_DECKNAME_FOCUSED: id_t = R_ID()
MENU_DECKSIZE_FOCUSED: id_t = R_ID()
DROPDOWN_MENU_FOCUSED: id_t = R_ID()  # means the dropdown menu is shown
SEARCHBAR_FOCUSED: id_t = R_ID()  # the textinput is focused
# displays the groups available (Should show if a group is a copy group or not)
GROUP_SELECTION: id_t = R_ID()
# if the main list is focused, the selected image is shown on fullscreen
FULL_IMAGE_SHOWN: id_t = R_ID()
DROPDOWN_MENU_ACTIVE: id_t = R_ID()
# enter states
ENTER_PRESSED: id_t = R_ID()
# if a card was pressed, it needs to animate back into its original state
CARD_SNAPBACK_ANIMATION: id_t = R_ID()

INITIALIZE_DECK_RENAMING_FRAME: id_t = R_ID()
DECK_RENAMING_FRAME_ACTIVE: id_t = R_ID()

INITIALIZE_MENU_FRAME: id_t = R_ID()
MENU_FRAME_ACTIVE: id_t = R_ID()

# Group Creation states
INITIALIZE_DECK_CREATION_FRAME: id_t = R_ID()
DECK_CREATION_FRAME_ACTIVE: id_t = R_ID()

# animation states
MOVING_ONE_ROW_UP: id_t = R_ID()
MOVING_ONE_ROW_DOWN: id_t = R_ID()
MOVING_ALL_ROWS_UP: id_t = R_ID()

DECKNAME_SELECTED_ANIMATION: id_t = R_ID()
MENU_BUTTON_SELECTED_ANIMATION: id_t = R_ID()

# popups
GROUP_DELETION_POPUP_SHOWN: id_t = R_ID()
GROUP_IMPORTING_POPUP_SHOWN: id_t = R_ID()

CARDINFO_SLIDING_IN: id_t = R_ID()  # the cardinfo is currently sliding in
CARDINFO_SHOWN: id_t = R_ID()  # in this state, the cardinfo is shown
CARDINFO_SLIDING_OUT: id_t = R_ID()  # the cardinfo is sliding out.

# ==================================
# VIEW STATES
# ==================================

SHOW_WITH_AMOUNT: id_t = R_ID()
SHOW_EACH_CARD: id_t = R_ID()

# ==================================
# MAIN LIST ACTION STATES
# ==================================

class MainListState:
    # state where no main list action can be done by pressing enter
    INFO_STATE: id_t = R_ID()
    SELECTION_STATE: id_t = R_ID()  # state in which cards can be selected
    # state in which cards can be moved around, changing the order
    MOVING_STATE: id_t = R_ID()
