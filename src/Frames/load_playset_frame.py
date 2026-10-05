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

class LoadPlaysetFrame(Frame):

    def __init__(self, width, height, data=None):

        super().__init__(FrameEnums.LOAD_PLAYSET_FRAME, width, height, data)

        self.modules = None


        self.loading_text = None
        self.loading_text_pos = None
        self.n_dots = 0
        self.max_dots = 5

        self.loading_delay = 200#ms
        self.loading_clock = Clock()
        self.loading_clock.start()

        self.extra_clock = Clock()

        self.loading_finished = False
        self.loading_lock = threading.Lock()

        self.thread = threading.Thread(target=self.load_playset)
        self.thread.start()

        self.render_loading()


    def render_loading(self):

        self.loading_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.BIG_HEADLINE,
                                                "Loading." + "."*(self.n_dots-1),
                                                Colors.WHITE
                                                )

        self.loading_text_pos = graphics.center_at(self.loading_text, self.center)



    def load_playset(self):

        playset_name = self.data[FrameDataID.GAMEINFO].playset
        self.modules = Modules.load_playset(playset_name)

        with self.loading_lock:
            self.loading_finished = True
            self.extra_clock.start()


    def tick(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (None, None)

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_ESCAPE]):
            return (None, None)

        if self.loading_clock.elapsed() > self.loading_delay:

            self.n_dots += 1
            self.n_dots %= (self.max_dots-1)

            self.render_loading()
            self.loading_clock.start()

        with self.loading_lock:

            if self.loading_finished and self.extra_clock.elapsed() > constants.__ADDITIONAL_LOAD_TIME__:

                self.data[FrameDataID.MODULES] = self.modules
                print(self.modules.explorer_module)
                return (None, None)


        return (FrameEnums.LOAD_PLAYSET_FRAME, self.data)


    def draw(self, screen):

        screen.fill(Colors.BLACK)

        screen.blit(self.loading_text, self.loading_text_pos)

        pygame.display.flip()
