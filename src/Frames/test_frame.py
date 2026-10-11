from Frames.empty_frame import EmptyFrame
from Frames.frame_enums import FrameEnums

class TestFrame(EmptyFrame):

    def __init__(self, data, frame_dim):
        super().__init__(data, frame_dim)


    def tick(self):
        stick_data = super().tick()

        return (FrameEnums.TEST_FRAME, stick_data[1])

    def draw(self, screen):
        super().draw(screen)
