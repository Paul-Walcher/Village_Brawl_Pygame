import pygame

from Frames.empty_frame import EmptyFrame
from Frames.frame_enums import FrameEnums

from widgets.dropdown_menu import DropdownMenu
from constants import Colors

class TestFrame(EmptyFrame):

    def __init__(self, data, frame_dim):
        super().__init__(data, frame_dim)

        self.dropdown_frame = pygame.Rect(self.x + 100, self.y + 100, 200, 500)

        self.dropdown = DropdownMenu(   self.dropdown_frame,
                                        [["Line 1"], ["L1", "and L2"], ["DDD", "DDD", "DDD"]],
                                        background_color=Colors.WHITE,
                                        text_color=Colors.RED
                                        )

        self.widgets.append(self.dropdown)


    def tick(self):
        stick_data = super().tick()

        return (FrameEnums.TEST_FRAME, stick_data[1])

    def draw(self, screen):
        super().draw(screen)
