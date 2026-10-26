from enum import Enum, auto

class FrameEnums(Enum):

    UNDEFINED = auto()
    PLAYSET_ENTITY = auto()

    EMPTY_FRAME = auto()
    TEST_FRAME = auto()

    INTRO_FRAME = auto()
    INTRO_MENU_FRAME = auto()
    CHOOSE_PLAYSET_FRAME = auto()
    CHOOSE_SAVE_NAME_FRAME = auto()
    LOAD_PLAYSET_FRAME = auto()
    CHOOSE_EXPLORER_FRAME = auto()
    CARDINFO_FRAME = auto()

    EXPLORER_INFO_FRAME = auto()
    SHOW_EXPLORER_STARTING_CARDS_FRAME = auto()

    INTERACTION_FRAME = auto()

    #WIDGETS
    TEXTBOX_WIDGET = auto()
    TEXTSLIDER_WIDGET = auto()
    TEXTINPUT_WIDGET = auto()
    RENDERABLE_CARDLIST_VIEWER_WIDGET = auto()
    SLIDER_WIDGET = auto()
    LABELED_IMAGE_SLIDER_WIDGET = auto()
    IMAGESLIDER_WIDGET = auto()
    DROPDOWN_MENU_WIDGET = auto()
