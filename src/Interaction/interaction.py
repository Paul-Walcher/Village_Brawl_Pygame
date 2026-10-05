from Frames.frame import Frame
from Frames.frame_enum import FrameEnums

class Interaction(Frame):

    def __init__(self, parent_frame, follow_up_function=None):

        self.parent_frame = parent_frame
        self.follow_up_function = follow_up_function
        super().__init__(FrameEnums.INTERACTION_FRAME, None, self.parent_frame.frame)
