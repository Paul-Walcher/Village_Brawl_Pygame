from typing import Type

from Frames.frame_enums import FrameEnums
from Frames.intro_frame import IntroFrame
from Frames.intro_menu_frame import IntroMenuFrame
from Frames.choose_playset_frame import ChoosePlaysetFrame
from Frames.choose_save_name_frame import ChooseSaveNameFrame
from Frames.load_playset_frame import LoadPlaysetFrame
from Frames.choose_explorer_frame import ChooseExplorerFrame
from Frames.explorer_info_frame import ExplorerInfoFrame
from Frames.empty_frame import EmptyFrame
from Frames.test_frame import TestFrame
from Frames.show_explorer_starting_cards_frame import ShowExplorerStartingCardsFrame
from Frames.cardinfo_frame import CardinfoFrame

frame_mappings: dict[FrameEnums, Type[Frame] ] = {
                                                    FrameEnums.INTRO_FRAME: IntroFrame,
                                                    FrameEnums.INTRO_MENU_FRAME: IntroMenuFrame,
                                                    FrameEnums.CHOOSE_PLAYSET_FRAME: ChoosePlaysetFrame,
                                                    FrameEnums.CHOOSE_SAVE_NAME_FRAME: ChooseSaveNameFrame,
                                                    FrameEnums.LOAD_PLAYSET_FRAME: LoadPlaysetFrame,
                                                    FrameEnums.CHOOSE_EXPLORER_FRAME: ChooseExplorerFrame,
                                                    FrameEnums.EXPLORER_INFO_FRAME: ExplorerInfoFrame,
                                                    FrameEnums.EMPTY_FRAME: EmptyFrame,
                                                    FrameEnums.TEST_FRAME: TestFrame,
                                                    FrameEnums.SHOW_EXPLORER_STARTING_CARDS_FRAME: ShowExplorerStartingCardsFrame,
                                                    FrameEnums.CARDINFO_FRAME: CardinfoFrame
                                                }
"""
Mappings of Enum -> Frame Class
"""
