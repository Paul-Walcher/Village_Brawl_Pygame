from __future__ import annotations
from typing import Any, Type, Callable, override

import os
import pygame
import threading

import graphics
from graphics import text_t, colored_text_t, page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t
from clock import Clock
from modules import Modules
import constants
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, color_t

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.label import Label

class Textbox(Frame):
    """
    This class provides a textbox widget.
    """

    def __init__(
                    self,
                    frame_dim: pygame.Rect,
                    text: colored_text_t, #the colored text for the textbox
                    font: pygame.font.Font = Fonts.STANDARD_FONT,
                    chars_per_line: int = 40,
                    lines_per_page: int = 5,
                    outline_size_p: float = 0.0, #size percentage of the outline
                    outline_color: color_t = Colors.BLACK,
                    background_color: color_t = Colors.TRANSPARENT,
                    hmargin: float = 0.1,
                    vmargin: float = 0.2,
                    line_margin_p: float = 0.02, #percentage of space between lines relative to self.height
                    pagenumber_color: color_t = Colors.WHITE, #color of the pagenumber
                    startpage_index: int = 0, #the starting page.
                ):

        super().__init__(
                            frame_enum=FrameEnums.TEXTBOX_WIDGET,
                            data=None,
                            frame_dim=frame_dim,
                            focus_group=None,
                            has_focus=False
                            )

        self.surface: pygame.Surface = None
        """
        The own surface.
        """
        self.inner_frame_dim: pygame.Rect = None
        """
        The inner frame dim into which the text is rendered.
        """
        self.text: colored_text_t = text
        """
        The text, as a colored text type.
        """
        self.chars_per_line: int = chars_per_line
        """
        The characters per line on a page
        """
        self.lines_per_page: int = lines_per_page
        """
        After how many lines a new break is forced.
        """
        self.outline_size_p: float = outline_size_p
        """
        The size percentage of the outline relative to min(self.width, self.height)
        """
        self.outline_size: int = -1
        """
        The actual size of the outline.
        """
        self.outline_color: color_t = outline_color
        """
        The color of the outline.
        """
        self.background_color: color_t = background_color
        """
        Background color of the textbox.
        """
        self.font: pygame.font.Font = font
        """
        Font of the textbox.
        """
        self.hmargin: float = hmargin
        """
        The horizontal margin, into which the text will be rendered.
        """
        self.vmargin: float = vmargin
        """
        The vertical margin, into which the text will be rendered.
        """
        self.line_margin_p: float = line_margin_p
        """
        Percentage of the distance between lines, relative to self.height.
        """
        self.page_index: int = startpage_index
        """
        The page index. If the startpage index is invalid, it will be reset to 0.
        """
        self.pages: list[colored_page_t] = None
        """
        The list of pages in this textbox.
        """
        self.rendered_page_label: Label = None
        """
        The label that displays the currently rendered page.
        """
        self.rendered_pagenumber_label: Label = None
        """
        The rendered pagenumber.
        """
        self.n_pages: int = 0
        """
        The number of pages available.
        """
        self.pagenumber_shown: bool = False
        """
        If the pagenumber is shown or not.
        Needs to be activated or deactivated explicitly.
        """
        self.pagenumber_percentage: float = 0.125
        """
        The amount of height the pagenumber occupies.
        """
        self.pagenumber_color: color_t = pagenumber_color
        """
        Color of the the pagenumber.
        """

        self.rerender()

    def set_outline_size(self, size: float) -> None:
        """
        Directly sets the outline size to the given percentage
        """
        if size == self.outline_size_p:
            return

        self.outline_size_p = size
        self.prerender()

    def set_outline_color(self, color: color_t) -> None:
        """
        Directly sets the outline color.
        """
        if color == self.outline_color:
            return

        self.outline_color = color
        self.prerender()

    def calculate_pages(self) -> None:
        """
        Creates self.pages from self.text.
        """
        if len(self.text) == 0:
            self.pages = None
        #creating the pages
        self.pages = graphics.page_by_chars_color(self.text, line_length=self.chars_per_line, paragraph_length=self.lines_per_page)
        self.n_pages = len(self.pages)

        if self.page_index >= self.n_pages:
            self.page_index = 0

    @override
    def rerender(self) -> None:
        """
        Rerendering
        """
        #creating the surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.calculate_pages()
        self.prerender()

    def render_page(self) -> None:
        """
        Renders the page.
        """
        #calculating the outline size
        self.outline_size = int(min(self.width, self.height) * self.outline_size_p)
        #resetting the labels
        self.rendered_page_label = None
        self.rendered_pagenumber_label = None
        #now if there are no pages to render, stop right here.
        if self.pages is None:
            return
        #calculating the inner rect
        self.inner_frame_dim = graphics.apply_margins(self.frame_dim, self.hmargin, self.vmargin)
        relative_inner_frame_dim = pygame.Rect(self.inner_frame_dim.x - self.x, self.inner_frame_dim.y - self.y, self.inner_frame_dim.width, self.inner_frame_dim.height)
        #the distance between the page number and the text
        dist_p: float = (0.05 if self.pagenumber_shown else 0.0)
        pagenum_p: float = (self.pagenumber_percentage if self.pagenumber_shown else 0.0)
        split_percentages: list[float] = [1.0 - (dist_p + pagenum_p), dist_p, pagenum_p]
        #creating the rects
        text_frame, distance_frame, number_frame = graphics.split_rect_vertically(relative_inner_frame_dim, split_percentages)

        #creating the textlabel
        self.rendered_page_label = Label(
                                            frame_dim=text_frame,
                                            font=self.font,
                                            label_page=self.pages[self.page_index],
                                            background_color=self.background_color,
                                            line_margin_percentage=self.line_margin_p
                                            )

        if self.pagenumber_shown:

            pagenumber_text: str = f"{self.page_index+1}/{self.n_pages}"

            self.rendered_pagenumber_label = Label(
                                                    frame_dim=number_frame,
                                                    font=self.font,
                                                    label_page=graphics.str_to_colored_page(pagenumber_text, self.pagenumber_color),
                                                    background_color=self.background_color,
                                                    line_margin_percentage=self.line_margin_p
                                                    )


    def add_pages(self, pages: list[colored_page_t]) -> None:
        """
        Adds the given pages at the end of the textbox
        """
        if self.pages is not None:
            self.pages.extend(pages)
        else:
            self.pages = pages
        self.n_pages = len(self.pages)

        self.prerender()

    def insert_page(self, index: int, page: colored_page_t) -> None:
        """
        Inserts the given page at index into self.pages.
        If the index is too small, it gets inserted at 0,
        if it is too large it is inserted at the end.
        """
        if self.pages is None:
            self.pages = [page]
        else:
            if index < 0:
                self.pages.insert(0, page)

            elif index >= self.n_pages:
                self.pages.append(page)

            else:
                self.pages.insert(index, page)

        self.n_pages += 1

        if self.page_index >= index:
            self.page_index += 1


    def show_pagenumber(self) -> None:
        """
        Makes the pagenumber shown.
        """
        self.pagenumber_shown = True
        self.prerender()

    def hide_pagenumber(self) -> None:
        """
        Hides the pagenumber.
        """
        self.pagenumber_shown = False
        self.prerender()

    def n_pages(self) -> int:
        """
        returns the number of pages
        """
        return self.n_pages

    def next_page(self) -> None:
        """
        Shows the next page of the textbox
        """
        self.page_index += 1
        self.page_index %= self.n_pages
        self.prerender()

    def prev_page(self) -> None:
        """
        Shows the previous page of the textbox.
        """
        self.page_index -= 1
        self.page_index %= self.n_pages
        self.prerender()

    def skip_to_page(self, page_index: int) -> None:
        """
        Skips to the given page index.
        """
        self.page_index = page_index
        self.page_index %= self.n_pages
        self.prerender()

    def prerender(self) -> None:
        """
        redraws without recalculating
        """
        self.render_page()

        self.surface.fill(self.background_color)

        if self.rendered_page_label is not None:
            self.rendered_page_label.render(self.surface)

        if self.rendered_pagenumber_label is not None:
            self.rendered_pagenumber_label.render(self.surface)

        if self.outline_size > 0:
            pygame.draw.rect(self.surface, self.outline_color, pygame.Rect(0, 0, self.width, self.height), width=self.outline_size)

    @override
    def render(self, screen: pygame.Surface):
        """
        Overrides rendering
        """

        screen.blit(self.surface, (self.x, self.y))

    @override
    def tick(self):

        if self.rendered_page_label is not None:
            self.rendered_page_label.tick()
        if self.rendered_pagenumber_label is not None:
            self.rendered_pagenumber_label.tick()
