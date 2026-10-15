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
from constants import KeyAlternatives

from event_queue_manager import EventQueueManager, Event

class TextInput(Frame):

    CURSOR_SYMBOL = "|"

    def __init__(self,
                frame_dim,
                font=Fonts.MINECRAFT,
                text_color=Colors.BLACK,
                background_color=Colors.WHITE,
                outline_size=5,
                outline_color=Colors.BLACK,
                textfield_hmargin=0.1,
                textfield_vmargin=0.2,
                starting_text="",
                n_chars_shown=30,
                max_textlength=50,
                cursor_color=Colors.BLACK,
                cursor_margin=5,#px
                cursor_width=5,#px
                key_delay=0#ms
                ):

        super().__init__(FrameEnums.TeXTINPUT_WIDGET, None, frame_dim)

        self.has_focus = False

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
        self.cursor_shown = False

        self.input_active = self.has_focus
        self.key_delay = key_delay
        self.key_clock = Clock()

        self.button_down = None

        self.rerender()

        self.key_clock.start()

    def __del__(self):
        if self.input_active:
            pygame.key.stop_text_input()

    def rerender(self):

        self.surface = pygame.Surface((self.width, self.height))

        textrect = pygame.Rect(0, 0, self.width, self.height)

        if self.outline_shown:
            trect = pygame.Rect(self.outline_size, self.outline_size, self.width - self.outline_size, self.height - self.outline_size)
            textrect = graphics.apply_margins(trect, self.textfield_hmargin, self.textfield_vmargin)
        else:
            textrect = graphics.apply_margins(textrect, self.textfield_hmargin, self.textfield_vmargin)

        if self.cursor_shown:
            textrect.x += (2 * self.cursor_margin + self.cursor_width) // 2
            textrect.width -= (2 * self.cursor_margin + self.cursor_width)

        self.textrect = textrect

        self.fontsize = graphics.get_fontsize(self.font, ["W"*self.n_chars_shown], textrect)

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

        full_length = self.front_text_rendered.get_width() + self.back_text_rendered.get_width() + (2*self.cursor_margin + self.cursor_width if self.cursor_shown else 0)

        cx += (textrect.width - full_length) // 2

        ftext_pos = (cx, cy)
        cx += self.front_text_rendered.get_width()
        if self.cursor_shown:
            cx += self.cursor_margin
            self.cursor_render_pos = pygame.Rect(cx, cy, self.cursor_width, textheight)
            cx += self.cursor_margin + self.cursor_width
        btext_pos = (cx, cy)

        self.text_rendered = [(self.front_text_rendered, ftext_pos),
                            (self.back_text_rendered, btext_pos)]

        self.prerender()

    def prerender(self):

        self.surface.fill(self.background_color)

        for surf, pos in self.text_rendered:
            self.surface.blit(surf, pos)

        #drawing cursor
        if self.cursor_shown:
            pygame.draw.rect(self.surface, self.cursor_color, self.cursor_render_pos)

        if self.outline_shown:
            pygame.draw.rect(self.surface, self.outline_color, self.frame_dim, width=self.outline_size)

    def render(self, screen):

        self.prerender()
        screen.blit(self.surface, (self.x, self.y))

    def tick(self):

        events_processed = []
        should_rerender = False

        if self.has_focus:

            for event in pygame.event.get():

                etext = False

                if event.type == pygame.TEXTINPUT:
                    etext = True

                    if self.key_clock.elapsed() >= self.key_delay:
                        if self.input_active:
                            tadd = event.text
                            addlen = self.max_textlength - len(self.text)
                            tadd = tadd[:addlen]

                            self.text = self.text[:self.cursor_offset+self.cursor_pos] + tadd + self.text[self.cursor_offset+self.cursor_pos:]
                            self.move_cursor_right(len(tadd))
                            self.key_clock.start()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        etext = True

                        if self.key_clock.elapsed() >= self.key_delay:
                            if self.input_active:
                                if self.cursor_pos > 0:
                                    self.text = self.text[:self.cursor_offset+self.cursor_pos-1] + self.text[self.cursor_offset+self.cursor_pos:]
                                    if self.cursor_offset > 0:
                                        self.cursor_offset -= 1
                                    else:
                                        self.cursor_pos -= 1
                                    should_rerender = True
                                self.key_clock.start()

                    if event.key == pygame.K_LEFT:
                        etext = True

                        if self.key_clock.elapsed() >= self.key_delay:
                            if self.input_active:
                                self.move_cursor_left()
                                self.key_clock.start()

                    if event.key == pygame.K_RIGHT:
                        etext = True

                        if self.key_clock.elapsed() >= self.key_delay:
                            if self.input_active:
                                self.move_cursor_right()
                                self.key_clock.start()


        for event in events_processed:
            pygame.event.post(event)

        if should_rerender:
            self.rerender()

    def get_surfaces(self):
        return [self.surface]

    def get_surfaces_with_position(self):
        return [(self.surface, (self.x, self.y))]

    def get_text(self):
        return self.text

    def set_text(self, text):

        self.text = text
        self.cursor_pos = 0
        self.cursor_offset = 0
        self.rerender()

    def focus(self):
        pygame.key.start_text_input()
        self.has_focus = True
        self.input_active = True
        self.show_cursor()

    def unfocus(self):
        pygame.key.stop_text_input()
        self.has_focus = False
        self.input_active = False
        self.hide_cursor()

    def show_outline(self):
        self.outline_shown = True
        self.prerender()

    def hide_outline(self):
        self.outline_shown = False
        self.prerender()

    def move_cursor_left(self, n=1):

        for i in range(n):
            if self.cursor_pos == 0:
                if self.cursor_offset > 0:
                    self.cursor_offset -= 1
            else:
                self.cursor_pos -= 1

        self.rerender()


    def move_cursor_right(self, n=1):

        for i in range(n):
            if self.cursor_pos == self.n_chars_shown:
                if self.cursor_offset < len(self.text)-1:
                    self.cursor_offset += 1
            else:
                self.cursor_pos += 1

        self.rerender()

    def show_cursor(self):

        self.cursor_shown = True
        self.rerender()

    def hide_cursor(self):
        self.cursor_shown = False
        self.rerender()
