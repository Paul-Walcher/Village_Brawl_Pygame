from Frames.frame_enums import FrameEnums

from Frames.intro_frame import IntroFrame
from Frames.intro_menu_frame import IntroMenuFrame
from Frames.choose_playset_frame import ChoosePlaysetFrame
from Frames.choose_save_name_frame import ChooseSaveNameFrame

frame_mappings = {
                    FrameEnums.INTRO_FRAME: IntroFrame,
                    FrameEnums.INTRO_MENU_FRAME: IntroMenuFrame,
                    FrameEnums.CHOOSE_PLAYSET_FRAME: ChoosePlaysetFrame,
                    FrameEnums.CHOOSE_SAVE_NAME_FRAME: ChooseSaveNameFrame
                    }
