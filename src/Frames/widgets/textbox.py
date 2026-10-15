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
from Frames.frame import Frame
from Frames.frame_enums import FrameEnums

class Textbox(Frame):

    def __init__(self, frame_dim, font, text, line_length=40, paragraph_length=5, outline_size=0, outline_color=Colors.BLACK, text_color=Colors.BLACK,
                background_color=Colors.TRANSPARENT, wmargin=5, hmargin=5, line_margin=2, centered=False,
                pagenumber_color=Colors.WHITE, startpage=0, text_colored=False

                ):

        super().__init__(FrameEnums.TEXTBOX_WIDGET, None, frame_dim)

        self.text = text
        self.line_length = line_length
        self.paragraph_length = paragraph_length
        self.outline_size = outline_size
        self.outline_color = outline_color
        self.text_color = text_color
        self.background_color = background_color
        self.font = font
        self.wmargin = wmargin
        self.hmargin = hmargin
        self.line_margin = line_margin
        self.centered = centered
        self.text_colored = text_colored

        self.page_index = startpage
        self.rpage = []
        self.n_pages = 0

        self.pagenumber_shown = False

        self.pagenumber_percentage = 0.2
        self.pagenumber_color = pagenumber_color

        self.calculate_pages()
        self.prerender()

    def set_outline_size(self, size):

        if size == self.outline_size:
            return
        self.outline_size = size
        self.prerender()

    def set_outline_color(self, color):

        if color == self.outline_color:
            return

        self.outline_color = color
        self.prerender()

    def calculate_pages(self):
        if not self.text_colored:
            self.pages = graphics.page_by_chars(self.text, line_length=self.line_length, paragraph_length=self.paragraph_length)
        else:
            self.pages = graphics.page_by_chars_color(self.text, line_length=self.line_length, paragraph_length=self.paragraph_length)

        self.n_pages = len(self.pages)
        self.page_index %= self.n_pages

    def rerender(self):
        self.prerender()

    def render_page(self):

        pdist = (int(0.05 * self.height) if self.pagenumber_shown else 0)
        aheight = self.height - 2*self.outline_size - 2*self.hmargin
        awidth = self.width - 2*self.outline_size - 2*self.wmargin

        pagenum_height = (int(self.pagenumber_percentage * (self.height)) if self.pagenumber_shown else 0)
        text_height = self.height - pagenum_height

        toprect = pygame.Rect(self.wmargin + self.outline_size, self.hmargin + self.outline_size, awidth, text_height - 2 * self.outline_size - pdist)
        numrect = pygame.Rect(self.outline_size, pdist + self.outline_size + text_height, self.width - 2*self.outline_size, pagenum_height - self.outline_size)

        self.boxrect = pygame.Rect(0, 0, self.width, text_height)

        if self.pagenumber_shown:

            toprect.height -= numrect.height

            pagestr = f"{self.page_index+1}/{self.n_pages}"

            if not self.text_colored:
                self.rpage = graphics.render_page_from_chars(self.font, self.pages[self.page_index],
                                                            toprect,
                                                            self.text_color, centered=True, line_margin=self.line_margin
                                                            )
            else:
                self.rpage = graphics.render_page_from_chars_color(self.font, self.pages[self.page_index],
                                                            toprect,
                                                            self.text_color, centered=True, line_margin=self.line_margin
                                                            )

            fsize = graphics.get_fontsize(self.font, [pagestr], numrect)
            pagenum_rendered = graphics.render_text(self.font, fsize, pagestr, self.pagenumber_color)
            pagenum_pos = graphics.get_center_with_surface(pagenum_rendered, numrect)

            self.rpage.append((pagenum_rendered, pagenum_pos))

        else:
            if not self.text_colored:
                self.rpage = graphics.render_page_from_chars(self.font, self.pages[self.page_index],
                                                            toprect,
                                                            self.text_color, centered=True, line_margin=self.line_margin
                                                            )
            else:
                self.rpage = graphics.render_page_from_chars_color(self.font, self.pages[self.page_index],
                                                            toprect,
                                                            self.text_color, centered=True, line_margin=self.line_margin
                                                            )

    def show_pagenumber(self):
        self.pagenumber_shown = True
        self.prerender()

    def hide_pagenumber(self):
        self.pagenumber_shown = False
        self.prerender()

    def num_pages(self):
        return self.n_pages

    def next_page(self):

        self.page_index += 1
        self.page_index %= self.n_pages
        self.prerender()

    def prev_page(self):

        self.page_index -= 1
        self.page_index %= self.n_pages
        self.prerender()

    def skip_to_page(self, page_index):

        self.page_index = page_index
        self.page_index %= self.n_pages
        self.prerender()

    def prerender(self):
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.render_page()
        self.surface.fill(self.background_color)

        if self.outline_size > 0:

            pygame.draw.rect(self.surface, self.outline_color, self.boxrect, width=self.outline_size)

        for rfont, pos in self.rpage:

            self.surface.blit(rfont, pos)

    def render(self, screen):

        self.prerender()
        screen.blit(self.surface, (self.x, self.y))

    def tick(self):
        pass

    def get_surfaces(self):
        return [self.surface]

    def get_surfaces_with_position(self):
        return  [(self.surface, (self.frame_dim.x, self.frame_dim.y))]
