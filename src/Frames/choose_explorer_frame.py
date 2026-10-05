import os
import pygame
import threading

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, FrameDataID
import graphics
from clock import Clock
from modules import Modules
import constants

class ChooseExplorerFrame(Frame):

    def __init__(self, width, height, data=None):

        super().__init__(FrameEnums.CHOOSE_EXPLORER_FRAME, width, height, data)

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


        return (FrameEnums.CHOOSE_EXPLORER_FRAME, self.data)


    def draw(self, screen):

        screen.fill(Colors.BLACK)

        pygame.display.flip()
