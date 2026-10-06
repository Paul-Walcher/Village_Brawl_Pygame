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

        self.explorer_ref = self.modules.mappings.explorer_mappings[self.explorer_enum]
        self.explorer_info = self.explorer_ref.info()

        self.headline_area = pygame.Rect(0, 0, self.width, self.height // 8)
        self.explorer_image_area = pygame.Rect(0, self.headline_area.height + self.headline_area.y, self.width, self.height // 8 * 3)

        self.surface = pygame.Surface((self.width, self.height))
        self.surface.set_alpha(Alpha.LEVEL_5)

        self.top_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.key_delay = 200#ms
        self.key_clock = Clock()

        #rendering
        self.rerender()

        self.key_clock.start()

    def render_headline(self):

        self.headline_surface = pygame.Surface((self.headline_area.w, self.headline_area.h), pygame.SRCALPHA)
        self.margin_percentage = 0.2

        headline_dist = 5

        self.headline_frame_dim = graphics.apply_margins(self.headline_area, self.margin_percentage, self.margin_percentage)
        self.headline_font = Fonts.MINECRAFT
        self.headline_fontsize = graphics.get_fontsize(self.headline_font, self.explorer_info.name, self.headline_frame_dim)

        self.headline = graphics.render_text(self.headline_font, self.headline_fontsize, self.explorer_info.name, self.explorer_info.name_color)
        self.headline_pos = graphics.get_center_with_surface(self.headline, self.headline_frame_dim)

    def render_explorer(self):

        self.explorer_image_path = self.explorer_info.standard_image_path
        self.explorer_image = graphics.render_image(self.explorer_image_path)

        wh_ratio = self.explorer_image.get_width() / self.explorer_image.get_height()

        self.explorer_image = pygame.transform.scale(self.explorer_image, (int(self.explorer_image_area.height * wh_ratio), self.explorer_image_area.height))
        self.explorer_image_pos = graphics.get_center_with_surface(self.explorer_image, self.explorer_image_area)


    def rerender(self):

        self.explorer_enum = self.data["ExplorerEnum"]

        self.explorer_ref = self.modules.mappings.explorer_mappings[self.explorer_enum]
        self.explorer_info = self.explorer_ref.info()

        self.render_headline()
        self.render_explorer()

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
            self.top_surface.fill(Colors.TRANSPARENT)

            if self.headline_surface is not None:

                self.headline_surface.fill((*Colors.BLACK, Alpha.LEVEL_4))
                self.headline_surface.blit(self.headline, self.headline_pos)

            self.top_surface.blit(self.headline_surface, (self.headline_area.x, self.headline_area.y))
            self.top_surface.blit(self.explorer_image, self.explorer_image_pos)

            screen.blit(self.surface, (self.x, self.y))
            screen.blit(self.top_surface, (self.x, self.y))

        pygame.display.flip()
