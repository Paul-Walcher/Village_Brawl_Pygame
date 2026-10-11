import pygame

from Frames.empty_frame import EmptyFrame
from Frames.frame_enums import FrameEnums

from widgets.dropdown_menu import DropdownMenu
from constants import Colors, KeyAlternatives
from clock import Clock
import time

class TestFrame(EmptyFrame):

    def __init__(self, data, frame_dim):
        super().__init__(data, frame_dim)

        self.frame_enum = FrameEnums.TEST_FRAME

        self.dropdown_frame = pygame.Rect(self.x + 100, self.y + 100, 200, 500)

        self.surface = pygame.Surface((self.frame_dim.w, self.frame_dim.h))

        self.dropdown = DropdownMenu(   self.dropdown_frame,
                                        [["Line 1"], ["L1", "and L2"], ["DDD", "DDD", "DDD"]],
                                        background_color=Colors.WHITE,
                                        text_color=Colors.RED
                                        )



        self.key_clock = Clock()
        self.key_delay = 300#ms

        self.key_clock.start()

    def tick(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (None, None)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            return (None, None)

        self.dropdown.tick()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            return (None, None)

        if self.key_clock.elapsed() > self.key_delay and not self.input_blocked:

            if keys[pygame.K_UP] or keys[KeyAlternatives.UP_ALTERNATIVE]:
                self.dropdown.move_up()
                self.key_clock.start()
            elif keys[pygame.K_DOWN] or keys[KeyAlternatives.DOWN_ALTERNATIVE]:
                self.dropdown.move_down()
                self.key_clock.start()
            elif keys[pygame.K_RETURN] or keys[KeyAlternatives.ENTER_ALTERNATIVE]:

                time.sleep(0.3)
                return (FrameEnums.FRAME_REFERENCE, self.parent_frame)

        return (self.frame_enum, None)

    def draw(self, screen):

        self.surface.fill(Colors.BLACK)

        screen.blit(self.surface, (self.x, self.y))
