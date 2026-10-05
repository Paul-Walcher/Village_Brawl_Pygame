import os
import pygame
import threading

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, FrameDataID, Alpha
import graphics
from clock import Clock
from modules import Modules
import constants

class ExplorerInfoFrame(Frame):

    def __init__(self, data=None, frame_dim=None):

        super().__init__(FrameEnums.CHOOSE_EXPLORER_FRAME, data, frame_dim)

        self.modules = self.data[FrameDataID.MODULES]
        self.explorer_enum = self.data["ExplorerEnum"]

        self.surface = pygame.Surface((self.width, self.height))
        self.surface.set_alpha(Alpha.HALF_FULL)


        self.key_delay = 200#ms
        self.key_clock = Clock()

        self.key_clock.start()

    def tick(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (None, None)

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_ESCAPE]):
            return (None, None)



        return (FrameEnums.EXPLORER_INFO_FRAME, self.data)


    def draw(self, screen):

        if self.surface is not None:
            self.surface.fill(Colors.DARK_GRAY)
            screen.blit(self.surface, (self.x, self.y))

        pygame.display.flip()
