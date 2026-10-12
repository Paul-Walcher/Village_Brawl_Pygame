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
                textfield_hmargin=0.2,
                textfield_vmargin=0.4,
                starting_text="",
                n_chars_shown=10,
                max_textlength=50,
                cursor_color=Colors.GRAY,
                cursor_margin=5,#px
                cursor_width=5#px
                ):

        super().__init__(frame_dim)

        self.font = font
        self.fontsize = 0
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
        self.cursor_margin = cursor_margin
        self.cursor_width = cursor_width

        self.n_chars_shown = n_chars_shown
        self.max_textlength = max_textlength

        self.text_rendered = None

        self.outline_shown = False
        self.cursor_shown = True

        self.rerender()

    def rerender(self):

        self.surface = pygame.Surface((self.width, self.height))

        textrect = pygame.Rect(0, 0, self.width, self.height)

        if self.outline_shown:
            trect = pygame.Rect(self.outline_size, self.outline_size, self.width - self.outline_size, self.height - self.outline_size)
            textrect = graphics.apply_margins(trect, self.textfield_hmargin, self.textfield_vmargin)
        else:
            textrect = graphics.apply_margins(textrect, self.textfield_hmargin, self.textfield_vmargin)

        textrect.width -= (2 * self.cursor_margin + self.cursor_width)

        self.textrect = textrect

        self.fontsize = graphics.get_fontsize(self.font, [" "*self.n_chars_shown], textrect)

        self.rtext = self.text[self.cursor_offset:self.cursor_offset+self.n_chars_shown]

        self.front_text = self.rtext[:self.cursor_pos]
        self.cursor_text = TextInput.CURSOR_SYMBOL
        self.back_text = self.rtext[self.cursor_pos:]

        self.front_text_rendered = graphics.render_text(self.font, self.fontsize, self.front_text, self.text_color)
        self.back_text_rendered = graphics.render_text(self.font, self.fontsize, self.back_text, self.text_color)

        textlen = self.front_text_rendered.get_width() + self.back_text_rendered.get_width() + (2* self.cursor_margin + self.cursor_width if self.cursor_shown else 0)
        textheight = max([self.front_text_rendered.get_height(), self.back_text_rendered.get_height()])

        x_offset = (0 if not self.cursor_shown else self.cursor_margin)
        y_offset = (textrect.height - textheight) // 2

        cx = textrect.x + x_offset
        cy = textrect.y + y_offset

        ftext_pos = (cx, cy)
        cx += self.front_text_rendered.get_width()
        if self.cursor_shown:
            cx += self.cursor_margin
            self.cursor_render_pos = pygame.Rect(cx, cy, self.cursor_width, textheight)
            cx += self.cursor_margin + self.cursor_width
        btext_pos = (cx, cy)

        self.text_rendered = [(self.front_text_rendered, ftext_pos),
                            (self.back_text_rendered, btext_pos)]

        self.render()

    def render(self):

        self.surface.fill(self.background_color)

        for surf, pos in self.text_rendered:
            self.surface.blit(surf, pos)

        #drawing cursor
        if self.cursor_shown:
            pygame.draw.rect(self.surface, self.cursor_color, self.cursor_render_pos)

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
