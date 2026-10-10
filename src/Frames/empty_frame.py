import pygame

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums

from constants import Colors

class EmptyFrame(Frame):

    def __init__(self, data, frame_dim, background_color=(*Colors.BLACK, 255)):
        super().__init__(FrameEnums.EMPTY_FRAME, data, frame_dim)
        self.background_color = background_color

        self.surface = pygame.Surface((self.frame_dim.width, self.frame_dim.height), pygame.SRCALPHA)

    def tick(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (None, self.data)

        super().tick()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            return (None, self.data)

        return (self.frame_enum, self.data)


    def draw(self, screen):


        self.surface.fill(self.background_color)
        screen.blit(self.surface, (self.frame_dim.x, self.frame_dim.y))
        super().draw(screen)
