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
from widgets.textbox import Textbox

class ExplorerInfoFrame(Frame):

    def __init__(self, data=None, frame_dim=None):

        super().__init__(FrameEnums.CHOOSE_EXPLORER_FRAME, data, frame_dim)

        self.modules = self.data[FrameDataID.MODULES]
        self.explorer_enum = self.data["ExplorerEnum"]

        self.explorer_ref = self.modules.mappings.explorer_mappings[self.explorer_enum]
        self.explorer_info = self.explorer_ref.info()

        self.headline_area = pygame.Rect(0, 0, self.width, self.height // 8)
        self.explorer_image_area = pygame.Rect(0, self.headline_area.height + self.headline_area.y, self.width, self.height // 8 * 3)
        self.textbox_area = pygame.Rect(0, self.explorer_image_area.y + self.explorer_image_area.height, self.width, self.height // 8 * 2)

        self.surface = pygame.Surface((self.width, self.height))
        self.surface.set_alpha(Alpha.LEVEL_5)

        self.top_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.key_delay = 200#ms
        self.key_clock = Clock()

        self.NO_FOCUS = -1
        self.DESCRIPTION_FOCUSED = 0
        self.MENU_FOCUSED = 1

        self.state = self.NO_FOCUS

        #rendering
        self.rerender()

        self.key_clock.start()

    def render_headline(self):

        self.headline_surface = pygame.Surface((self.headline_area.w, self.headline_area.h), pygame.SRCALPHA)
        self.margin_percentage = 0.2

        headline_dist = 5

        self.headline_frame_dim = graphics.apply_margins(self.headline_area, self.margin_percentage, self.margin_percentage)
        self.headline_font = Fonts.MINECRAFT
        self.headline_fontsize = graphics.get_fontsize(self.headline_font, [self.explorer_info.name], self.headline_frame_dim)

        self.headline = graphics.render_text(self.headline_font, self.headline_fontsize, self.explorer_info.name, self.explorer_info.name_color)
        self.headline_pos = graphics.get_center_with_surface(self.headline, self.headline_frame_dim)

    def render_explorer(self):

        self.explorer_image_path = self.explorer_info.standard_image_path
        self.explorer_image = graphics.render_image(self.explorer_image_path)

        wh_ratio = self.explorer_image.get_width() / self.explorer_image.get_height()

        self.explorer_image = pygame.transform.scale(self.explorer_image, (int(self.explorer_image_area.height * wh_ratio), self.explorer_image_area.height))
        self.explorer_image_pos = graphics.get_center_with_surface(self.explorer_image, self.explorer_image_area)

    def render_textbox(self):

        self.textbox_hmargin = 0.2
        self.textbox_vmargin = 0.4
        self.textbox_dim = graphics.apply_margins(self.textbox_area, self.textbox_hmargin, self.textbox_vmargin)

        text = self.explorer_info.description

        self.textbox = Textbox(Fonts.MINECRAFT, Fontsizes.SMALL, text, self.textbox_dim.width, self.textbox_dim.height, text_color=(*Colors.GREEN, 255), centered=True)
        self.textbox_pos = graphics.get_center_with_surface(self.textbox.get_surface(), self.textbox_dim)

        self.textbox.show_pagenumber()

        if self.state == self.DESCRIPTION_FOCUSED:
            self.textbox.set_outline_size(5)

    def rerender(self):

        self.explorer_enum = self.data["ExplorerEnum"]

        self.explorer_ref = self.modules.mappings.explorer_mappings[self.explorer_enum]
        self.explorer_info = self.explorer_ref.info()

        self.render_headline()
        self.render_explorer()
        self.render_textbox()

    def tick(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (None, None)

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_ESCAPE]):
            return (None, None)

        if self.key_clock.elapsed() > self.key_delay:

            if keys[pygame.K_LEFT] or keys[KeyAlternatives.LEFT_ALTERNATIVE]:

                if self.state == self.NO_FOCUS:
                    self.state = self.DESCRIPTION_FOCUSED
                    self.textbox.set_outline_size(5)
                elif self.state == self.DESCRIPTION_FOCUSED:
                    self.textbox.prev_page()
                    self.key_clock.start()

            if keys[pygame.K_RIGHT] or keys[KeyAlternatives.RIGHT_ALTERNATIVE]:

                if self.state == self.NO_FOCUS:
                    self.state = self.DESCRIPTION_FOCUSED
                    self.textbox.set_outline_size(5)
                elif self.state == self.DESCRIPTION_FOCUSED:
                    self.textbox.next_page()
                    self.key_clock.start()

            if keys[pygame.K_UP] or keys[KeyAlternatives.UP_ALTERNATIVE]:

                if self.state == self.NO_FOCUS or self.state == self.MENU_FOCUSED:
                    self.state = self.DESCRIPTION_FOCUSED
                    self.textbox.set_outline_size(5)

            if keys[pygame.K_DOWN] or keys[KeyAlternatives.DOWN_ALTERNATIVE]:

                if self.state == self.NO_FOCUS or self.state == self.DESCRIPTION_FOCUSED:
                    self.state = self.MENU_FOCUSED
                    self.textbox.set_outline_size(0)





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
            self.top_surface.blit(self.textbox.get_surface(), self.textbox_pos)

            screen.blit(self.surface, (self.x, self.y))
            screen.blit(self.top_surface, (self.x, self.y))

        pygame.display.flip()
