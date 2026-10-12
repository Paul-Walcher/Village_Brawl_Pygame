import os
import pygame
import threading

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import (
    PLAYSETS_FOLDER,
    Colors,
    Fonts,
    Fontsizes,
    KeyAlternatives,
    FrameDataID
)
import graphics
from clock import Clock
from modules import Modules
import constants

from event_queue_manager import EventQueueManager, Event
from widgets.widget import Widget

class TextInput(Widget):

    CURSOR_SYMBOL = "|"

    def __init__(self,
                frame_dim,
                font=Fonts.MINECRAFT,
                text_color=Colors.BLACK,
                background_color=Colors.WHITE,
                outline_size=5,
                outline_color=Colors.BLACK,
                textfield_hmargin=0.1,
                textfield_vmargin=0.05,
                starting_text="",
                n_chars_shown=10,
                max_textlength=50,
                cursor_color=Colors.GRAY
                ):

        super().__init__(frame_dim)

        self.font = font
        self.text_color = text_color
        self.background_color = background_color
        self.outline_size = outline_size
        self.outline_color = outline_color
        self.textfield_hmargin = textfield_hmargin
        self.textfield_vmargin = textfield_vmargin

        self.text = starting_text
        self.fontsize = None
        self.cursor_pos = 0
        self.cursor_color = cursor_color
        self.cursor_offset = 0

        self.n_chars_shown = n_chars_shown
        self.max_textlength = max_textlength

        self.text_rendered = None

        self.outline_shown = False
        self.cursor_shown = True

        self.rerender()

    def rerender(self):

        self.surface = pygame.Surface((self.width, self.height))

        textrect = None

        if self.outline_shown:
            trect = pygame.Rect(self.outline_size, self.outline_size, self.width - self.outline_size, self.height - self.outline_size)
            textrect = graphics.apply_margins(trect, self.textfield_hmargin, self.textfield_vmargin)
        else:
            textrect = graphics.apply_margins(self.frame_dim, self.textfield_hmargin, self.textfield_vmargin)
            textrect.x -= self.x
            textrect.y -= self.y

        self.text_to_render = [[(self.text[self.cursor_offset:self.cursor_offset+self.cursor_pos], self.text_color),
                                (TextInput.CURSOR_SYMBOL, self.cursor_color), (self.text[self.cursor_offset+self.cursor_pos:], self.text_color)]]

        self.text_to_render = graphics.render_page_from_chars_color(self.font, self.text_to_render, textrect, self.text_color, centered=True, vertical_centered=True)


        self.render()

    def render(self):

        self.surface.fill(self.background_color)

        for surf, pos in self.text_to_render:
            self.surface.blit(surf, pos)

        if self.outline_shown:

            pygame.draw.rect(self.surface, self.outline_color, self.frame_dim, width=self.outline_size)

    def tick(self):
        pass

    def get_surfaces(self):
        return [self.surface]

    def get_surfaces_with_position(self):
        return [(self.surface, (self.x, self.y))]

    def get_text(self):
        pass

    def set_text(self, text):
        pass

    def start_input(self):
        pass

    def end_input(self):
        pass

    def show_outline(self):
        self.outline_shown = True
        self.render()

    def hide_outline(self):
        self.outline_shown = False
        self.render()

    def move_cursor_left(self):
        pass

    def move_cursor_right(self):
        pass

    def show_cursor(self):
        pass

    def hide_cursor(self):
        pass
