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

class Textbox:

    def __init__(self, font, fontsize, text, width, height, outline_size=0, outline_color=Colors.BLACK, text_color=Colors.BLACK,
                background_color=Colors.TRANSPARENT, wmargin=5, hmargin=5, line_margin=2, centered=False

                ):

        self.text = text
        self.width, self.height = width, height
        self.outline_size = outline_size
        self.outline_color = outline_color
        self.text_color = text_color
        self.background_color = background_color
        self.font = font
        self.fontsize = fontsize
        self.wmargin = wmargin
        self.hmargin = hmargin
        self.line_margin = line_margin
        self.centered = centered

        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

        self.page_index = 0
        self.rpage = []
        self.n_pages = 0


        self.calculate_pages()
        self.render()

    def calculate_pages(self):
        self.pages = graphics.page_by_chars(self.text)
        self.n_pages = len(self.pages)

    def render_page(self):
        self.rpage = graphics.render_page_from_chars(Fonts.MINECRAFT, self.pages[self.page_index],
                                                    pygame.Rect(self.outline_size+self.wmargin, self.outline_size+self.hmargin,
                                                    self.width-self.wmargin-self.outline_size, self.height-self.hmargin-self.outline_size),
                                                    Colors.GREEN, centered=True, line_margin=self.line_margin
                                                    )

    def num_pages(self):
        return self.n_pages

    def next_page(self):

        self.page_index += 1
        self.page_index %= self.n_pages
        self.render()

    def prev_page(self):

        self.page_index -= 1
        self.page_index %= sself.n_pages
        self.render()

    def render(self):
        self.render_page()
        self.surface.fill(self.background_color)

        if self.outline_size > 0:

            pygame.draw.rect(self.surface, self.outline_color, (0, 0, self.width, self.height), width=self.outline_size)

        for rfont, pos in self.rpage:

            self.surface.blit(rfont, pos)

    def get_surface(self):
        return self.surface
