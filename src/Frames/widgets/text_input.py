from __future__ import annotations
from typing import Any, Callable

import os
import pygame
import threading

from constants import (
    PLAYSETS_FOLDER,
    Colors,
    Fonts,
    Fontsizes,
    KeyAlternatives,
    R_ID,
    color_t,
    id_t
)
import graphics
from graphics import page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t
from clock import Clock
from modules import Modules
import constants

from event_queue_manager import EventQueueManager, Event

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums

class TextInput(Frame):
    """
    Provides a textfield, that when it has focus saves the textinput from the used.
    Deactivates textinput via pygame.key.stop_text_input() when losing focus.
    """

    #symbols
    CURSOR_SYMBOL: str = "|"
    #for determining the fontsize
    SIZE_REFERENCE_CHARACTER: str = "W"

    class EventTypes:
        #events
        TEXT_ENTERED: id_t = R_ID()
        UNFOCUSED: id_t = R_ID()


    #events
    class TextEnteredEvent(Event):
        """
        Event for when enter is pressed on the text input.
        Contains the text entered.
        """

        def __init__(self, input_text: str, data: Any = None):

            Event.__init__(self, etype=TextInput.EventTypes.TEXT_ENTERED, data=data)

            self.input_text: str = input_text
            """
            The text inside the textinput when enter was pressed.
            """

        def copy(self) -> TextInput.TextEnteredEvent:
            """
            Returns a copy of the event.
            """
            copy_event: TextInput.TextEnteredEvent = TextInput.TextEnteredEvent(self.input_text, self.data)
            return copy_event

    class UnfocusedEvent(Event):
        """
        Event that signals this frame unfocused itself.
        """

        def __init__(self, data: Any = None):

            Event.__init__(self, etype=TextInput.EventTypes.UNFOCUSED, data=data)

        #uses parent class copy function


    def __init__(self,
                frame_dim: pygame.Rect,
                parent_frame: Frame = None,
                focus_group: str = "",
                has_focus: bool = False,
                textfield_hmargin: float = 0.1,
                textfield_vmargin: float = 0.2,
                font: pygame.font.Font = Fonts.STANDARD_FONT,
                text_color: color_t = Colors.BLACK,
                background_color: color_t = Colors.WHITE,
                outline_size_p: float = 0.05,
                outline_color: color_t = Colors.BLACK,
                outline_shown: bool = False,
                starting_text: str = "",
                cursor_color: color_t = Colors.BLACK,
                cursor_margin_p: float = 0.01,#px
                cursor_width_p: float = 0.01,#px
                cursor_height_p: float = 0.5, #px
                cursor_shown: bool = True,
                n_chars_shown: int = 30,
                max_textlength: int = 50,
                intro_delay: float = 100,#ms
                input_delay: float = 10,#ms
                backspace_delay: float = 100,#ma
                cursor_flickering: bool = True, #if the cursor flickers when the textinput is focused
                cursor_flickering_frequency: float = 400,#ms
                tab_out_key_combination: list[int] = None
                ):

        Frame.__init__(
                        self,
                        frame_enum=FrameEnums.TEXTINPUT_WIDGET,
                        data=None,
                        frame_dim=frame_dim,
                        parent_frame=parent_frame,
                        focus_group=focus_group,
                        has_focus=has_focus
                        )

        self.surface: pygame.Surface = None
        """
        The own surface, onto which everything is rendered.
        """
        self.textfield_hmargin: float = textfield_hmargin
        """
        The horizontal margin for the textrect.
        """
        self.textfield_vmargin: float = textfield_vmargin
        """
        The vertical margin for the textrect.
        """
        self.textfield_frame_dim: pygame.Rect = None
        """
        The dimension for the inner textfield.
        """
        self.relative_textfield_frame_dim: pygame.Rect = None
        """
        The textfield_frame_dim relative to self.surface.
        """
        self.font: pygame.font.Font = font
        """
        The font for the TextInput
        """
        self.fontsize: int = -1
        """
        The fontsize of the whole textinput.
        """
        self.text_color: color_t = text_color
        """
        Color of the text inside the TextInput.
        """
        self.background_color: color_t = background_color
        """
        Color of the background for the TextInput.
        """
        self.outline_size_p: float = outline_size_p
        """
        Percentage of the outline size,
        relative to self.width, self.height,
        whatever is lower.
        """
        self.outline_size: int = None
        """
        The actual outline size.
        """
        self.outline_color: color_t = outline_color
        """
        The color of the outline.
        """
        self.outline_shown: bool = outline_shown
        """
        If the outline is shown.
        """
        self.text: str = starting_text
        """
        The text inside the InputText.
        """
        self.cursor_pos: int = 0
        """
        The cursor position, element of[0, self.n_chars_shown]
        """
        self.cursor_offset: int = 0
        """
        Offset of the cursor, the cursor is shown at: self.cursor_offset+self.cursor_pos
        """
        self.cursor_color: color_t = cursor_color
        """
        Color of the cursor.
        """
        self.cursor_margin_p: float = cursor_margin_p
        """
        Distance from the cursor to the text as a percentage of self.textfield_frame_dim.width
        """
        self.cursor_margin: int = None
        """
        The actual cursor margin
        """
        self.cursor_width_p: float = cursor_width_p
        """
        Width of the cursor as a percentage of self.textfield_frame_dim.width
        """
        self.cursor_width: int = None
        """
        The actual cursor width.
        """
        self.cursor_height_p: float = cursor_height_p
        """
        Height of the cursor as a percentage of self.textfield_frame_dim.height.
        """
        self.cursor_height: int = None
        """
        Actual cursor height.
        """
        self.cursor_render_pos: tuple[int, int] = None
        """
        The cursor render pos.
        """
        self._cursor_shown: bool = cursor_shown
        """
        If the cursor is shown or not.
        """
        self.n_chars_shown: int = n_chars_shown
        """
        The number of characters after which the text starts being offset.
        """
        self.max_textlength: int = max_textlength
        """
        Number after which the TextInput stops accepting input if len(self.text) >= self.max_textlength.
        """
        self.rendered_front_text: rendered_surface_position_tuples_t = None
        """
        The rendered text before the cursor.
        """
        self.front_text_pos: tuple[int, int] = None
        """
        Position of the front text.
        """
        self.rendered_back_text: rendered_surface_position_tuples_t = None
        """
        The rendered text after the cursor.
        """
        self.back_text_pos: tuple[int, int] = None
        """
        Position of the back text.
        """
        self.input_delay: float = input_delay
        """
        The delay between inputs.
        """
        self.input_delay_clock: Clock = Clock()
        """
        The clock for the input delay.
        """
        self.backspace_delay: float = backspace_delay
        """
        Delay between backspace pressed detections.
        """
        self.backspace_delay_clock: Clock = Clock()
        """
        Clock for backspace delay.
        """
        self.intro_delay: float = intro_delay
        """
        Delay when this frame becomes focused, as not to swallow key pressed events.
        """
        self.intro_delay_clock: Clock = Clock()
        """
        Clock for the intro delay.
        """
        self.input_active: bool = True
        """
        If the input is active or not.
        """
        self.cursor_flickering: bool = cursor_flickering
        """
        If the cursor should flicker when the textinput is focused.
        """
        self.cursor_flickering_frequency: float = cursor_flickering_frequency
        """
        The time until the state of the cursor makes one round of (shown, unshown) and reverts
        back to shown. Both states last self.cursor_flickering_frequency // 2.
        """
        self.cursor_flickering_clock: Clock = Clock()
        """
        Clock for cursor flickering.
        """
        self.tab_out_key_combination: list[int] = ([pygame.K_LCTRL, KeyAlternatives.BACK_KEY] if tab_out_key_combination is None else tab_out_key_combination)
        """
        If all of the keys in the list are pressed at once, the textinput will act as if escape was pressed.
        """
        self.rerender()

    @property
    def cursor_shown(self):
        """
        If the cursor is shown or not.
        """
        return self._cursor_shown


    def on_focus_gained(self, lost_focus_frame: Frame) -> None:
        """
        Activates the text input.
        """
        pygame.key.start_text_input()
        self.reset_keys_pressed()
        self.prerender()
        self.intro_delay_clock.start()
        self._cursor_shown = True
        if self.cursor_flickering:
            self.cursor_flickering_clock.start()

    def on_focus_lost(self, gained_focus_frame: Frame) -> None:
        """
        Deactivates the text input.
        """
        self._cursor_shown = True
        pygame.key.stop_text_input()
        self.prerender()


    def rerender(self) -> None:
        """
        Recalculates positions, then renders.
        """
        #resetting the text.
        self.text = ""
        self.cursor_pos = 0
        self.cursor_offset = 0
        self.input_active = True
        #creating the surface
        self.surface = pygame.Surface((self.width, self.height))
        #the size of the outline
        self.outline_size = int(min(self.width * self.outline_size_p, self.height * self.outline_size_p))

        trect: pygame.Rect = self.frame_dim.copy()
        if self.outline_shown:
            trect = pygame.Rect(self.outline_size, self.outline_size, self.width - self.outline_size, self.height - self.outline_size)

        self.textfield_frame_dim = graphics.apply_margins(trect, self.textfield_hmargin, self.textfield_vmargin)
        self.relative_textfield_frame_dim = pygame.Rect(
                                                        self.textfield_frame_dim.x-self.x,
                                                        self.textfield_frame_dim.y-self.y,
                                                        self.textfield_frame_dim.width,
                                                        self.textfield_frame_dim.height
                                                        )

        self.fontsize = graphics.get_fontsize(
                                                font=self.font,
                                                lines=graphics.str_to_page(TextInput.SIZE_REFERENCE_CHARACTER * self.n_chars_shown),
                                                frame=self.textfield_frame_dim
                                                )

        #calculating the cursor dimensions
        self.cursor_margin = max(int(self.textfield_frame_dim.width * self.cursor_margin_p), 1)
        self.cursor_width = max(int(self.textfield_frame_dim.width * self.cursor_width_p), 1)
        self.cursor_height = max(int(self.textfield_frame_dim.height * self.cursor_height_p), 1)

        self.prerender()

        self.reset_exit_flag()
        self.intro_delay_clock.start()
        self.input_delay_clock.start()
        self.backspace_delay_clock.start()


    def render_text(self) -> None:
        """
        Renders the text inside the textfield.
        """
        front_text: str = self.get_front_text()
        back_text: str = self.get_back_text()

        cx: int = self.relative_textfield_frame_dim.x
        cy: int = self.relative_textfield_frame_dim.y

        if front_text:
            self.rendered_front_text = graphics.render_text(font=self.font, fontsize=self.fontsize, text=front_text, color=self.text_color)
            self.front_text_pos = (cx, cy + (self.relative_textfield_frame_dim.height - self.rendered_front_text.get_height()) // 2) #centered pos
            cx += self.rendered_front_text.get_width()
            self.cursor_render_pos = (cx + self.cursor_margin, cy + (self.relative_textfield_frame_dim.height - self.cursor_height) // 2)
            cx += self.get_cursor_widths()
        else:
            self.rendered_front_text = None
            self.front_text_pos = None
            self.cursor_render_pos = (cx + self.cursor_margin, cy + (self.relative_textfield_frame_dim.height - self.cursor_height) // 2)
            cx += self.get_cursor_widths()

        if back_text:
            self.rendered_back_text = graphics.render_text(font=self.font, fontsize=self.fontsize, text=back_text, color=self.text_color)
            self.back_text_pos = (cx, cy + (self.relative_textfield_frame_dim.height - self.rendered_back_text.get_height()) // 2) #centered pos
        else:
            self.rendered_back_text = None
            self.back_text_pos = None

    def prerender(self) -> None:
        """
        Prerendering occurs whenever something changes
        """
        self.surface.fill(self.background_color)
        #getting the rendered text
        self.render_text()

        #then rendering the text
        if self.rendered_front_text is not None:
            self.surface.blit(self.rendered_front_text, self.front_text_pos)
        if self.rendered_back_text is not None:
            self.surface.blit(self.rendered_back_text, self.back_text_pos)
        #drawing cursor
        if self.cursor_shown:
            pygame.draw.rect(self.surface, self.cursor_color, (*self.cursor_render_pos, self.cursor_width, self.cursor_height))
        #drawing the outline
        if self.outline_shown:
            pygame.draw.rect(self.surface, self.outline_color, self.frame_dim, width=self.outline_size)

    def render(self, screen: pygame.Surface) -> None:
        """
        Blitting the surface.
        """
        screen.blit(self.surface, (self.x, self.y))

    def get_front_text(self) -> str:
        """
        Getting the text before the cursor to render.
        """
        return self.text[self.cursor_offset:self.cursor_offset+self.cursor_pos]

    def get_back_text(self) -> str:
        """
        Getting the text after the cursor to render.
        """
        return self.text[self.cursor_offset+self.cursor_pos:self.cursor_offset+self.n_chars_shown]

    def get_cursor_widths(self) -> int:
        """
        Returns all the width occupied by the cursor.
        """
        if self.cursor_shown:
            return (2 * self.cursor_margin + self.cursor_width)
        else:
            return 0

    def bind_events(self) -> None:
        """
        Binding events.
        """
        if self.is_focused():
            #adding textinput event
            self.add_pygame_event_callback(etype=pygame.TEXTINPUT, data=None, putback=False, func=self.on_textinput)
            self.add_pygame_key_callback(key=pygame.K_LEFT, data=None, putback=False, func=self.on_left_pressed)
            self.add_pygame_key_callback(key=pygame.K_RIGHT, data=None, putback=False, func=self.on_right_pressed)
            self.add_pygame_key_callback(key=pygame.K_ESCAPE, data=None, putback=False, func=self.on_escape_pressed)
            self.add_pygame_key_callback(key=pygame.K_RETURN, data=None, putback=False, func=self.on_enter_pressed)
            self.add_pygame_event_callback(etype=pygame.KEYDOWN, data=None, putback=True, func=self.on_keypress)


    def on_textinput(self, event: pygame.event.Event, data=None) -> None:
        """
        When textinput is done.
        """
        if self.input_delay_clock.elapsed() > self.input_delay:
            if self.input_active:

                tadd = event.text
                addlen = self.max_textlength - len(self.text)
                tadd = tadd[:addlen]

                self.text = self.text[:self.cursor_offset+self.cursor_pos] + tadd + self.text[self.cursor_offset+self.cursor_pos:]

                self.move_cursor_right(len(tadd))

                self.input_delay_clock.start()

                #resetting the flickering#
                if self.cursor_flickering:
                    self._cursor_shown = True
                    self.cursor_flickering_clock.start()



    def on_left_pressed(self, event: pygame.event.Event, data=None) -> None:
        """
        left pressed event.
        """
        self.move_cursor_left()
        if self.cursor_flickering:
            self._cursor_shown = True
            self.cursor_flickering_clock.start()

    def on_right_pressed(self, event: pygame.event.Event, data=None) -> None:
        """
        left pressed event.
        """
        self.move_cursor_right()
        if self.cursor_flickering:
            self._cursor_shown = True
            self.cursor_flickering_clock.start()

    def on_escape_pressed(self, event: pygame.event.Event, data=None) -> None:
        """
        Escape pressed event.
        """
        self.unfocus()
        self.push_event(TextInput.UnfocusedEvent())

    def on_enter_pressed(self, event: pygame.event.Event, data=None) -> None:
        """
        enter pressed event.
        """
        self.push_event(TextInput.TextEnteredEvent(input_text=self.get_text()))

    def on_keypress(self, event: pygame.event.Event, data=None) -> None:
        """
        Checks for tab out.
        """
        if all([self.key_pressed(key) for key in self.tab_out_key_combination]):
            self.on_escape_pressed(event, data)
            return Frame.EventCallback.SUCCESS

        return Frame.EventCallback.FAILURE

    def tick(self) -> None:
        """
        Tick function.
        """

        if self.intro_delay_clock.elapsed() > self.intro_delay:
            self.manage_pygame_events()

        if self.exit_flag_raised():
            return None

        if self.key_pressed(pygame.K_BACKSPACE) and self.backspace_delay_clock.elapsed() > self.backspace_delay:
            if self.input_active:
                if self.cursor_pos > 0:

                    self.text = self.text[:self.cursor_offset+self.cursor_pos-1] + self.text[self.cursor_offset+self.cursor_pos:]
                    self.cursor_pos -= 1
                    self.prerender()
                    self.backspace_delay_clock.start()

                else:

                    self.cursor_offset -= 1
                    self.cursor_offset = max(self.cursor_offset, 0)
                    self.prerender()
                    self.backspace_delay_clock.start()

        #checking for flickering
        if self.cursor_flickering and self.is_focused():
            if self.cursor_flickering_clock.elapsed() > self.cursor_flickering_frequency:

                self._cursor_shown = not self._cursor_shown
                self.prerender()
                self.cursor_flickering_clock.start()

        return self

    def get_text(self) -> str:
        """
        Gets the text.
        """
        return self.text

    def set_text(self, text: str) -> None:
        """
        Sets the text.
        """
        self.text = text
        self.cursor_pos = 0
        self.cursor_offset = 0
        self.prerender()

    def activate_input(self) -> None:
        """
        activates the input.
        """
        self.input_active = True

    def deactivate_input(self) -> None:
        """
        deactivates the input.
        """
        self.input_active = False

    def show_outline(self) -> None:
        """
        Makes the outline visible.
        """
        self.outline_shown = True
        self.prerender()

    def hide_outline(self) -> None:
        """
        Hides the outline.
        """
        self.outline_shown = False
        self.prerender()

    def move_cursor_left(self, n: int = 1) -> None:
        """
        Moves the cursor left.
        """
        for i in range(n):
            if self.cursor_pos == 0:
                if self.cursor_offset > 0:
                    self.cursor_offset -= 1
            else:
                self.cursor_pos -= 1

        self.prerender()

    def move_cursor_right(self, n: int = 1) -> None:
        """
        Moves the cursor right.
        """

        for i in range(n):
            if self.cursor_pos == self.n_chars_shown:
                if self.cursor_offset < len(self.text)-1:
                    self.cursor_offset += 1
            elif self.cursor_pos < len(self.text):
                self.cursor_pos += 1

        self.prerender()

    def show_cursor(self) -> None:
        """
        Makes the cursor shown.
        """
        self.cursor_shown = True
        self.prerender()

    def hide_cursor(self) -> None:
        """
        Hides the cursor.
        """
        self.cursor_shown = False
        self.prerender()
