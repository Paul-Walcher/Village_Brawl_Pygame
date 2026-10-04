import pygame
from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import Colors

class IntroMenuFrame(Frame):

    def __init__(self, width, height, data=None):

        super().__init__(FrameEnums.INTRO_MENU_FRAME, width, height, data)


    def tick(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (None, None)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            return (None, None)

        return (FrameEnums.INTRO_MENU_FRAME, None)

    def draw(self, screen):

        screen.fill(Colors.WHITE)
        pygame.display.flip()
