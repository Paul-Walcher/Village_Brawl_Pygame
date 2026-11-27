"""
This file provides the frame that handles text input
in RenderableCardListviewer.
"""
from __future__ import annotations
from typing import Type, Any, Callable, override, TYPE_CHECKING

import pygame
from constants import R_ID, Colors
from clock import Clock
import graphics

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.text_input import TextInput

if TYPE_CHECKING:
    from constants import (
                            id_t,
                            color_t
                            )

class FocusedTextInputFrame(Frame):
    """
    Provides a text input frame.
    """

    TEXT_ENTERED: id_t = R_ID()
    ESCAPE: id_t = R_ID()

    def __init__(
        self,
        frame_dim: pygame.Rect,
        parent_frame: Frame,
        focus_group: str = "",
        has_focus: bool = True
    ):

        # initializing
        Frame.__init__(
            self,
            frame_enum=FrameEnums.UNDEFINED,
            data=None,
            frame_dim=frame_dim,
            parent_frame=parent_frame,
            focus_group=focus_group,
            has_focus=has_focus
        )

        self.text_input: TextInput = None
        """
        Text input reference.
        """
        self.text_input_frame: pygame.Rect = None
        """
        Frame_dim for self.text_input.
        """
        self.background_color: color_t = Colors.BLACK
        """
        Background color.
        """
        self.background_alpha: int = 127
        """
        Alpha value for the background.
        """
        self.escape_released: bool = False
        """
        For checking if escaping the frame is possible.
        """
        self._exit_type: id_t = None
        """
        The state describing how the frame was exited.
        """
        self.intro_delay: float = 100  # ms
        """
        The intro delay.
        """
        self.intro_delay_clock: Clock = Clock()
        """
        Intro delay clock.
        """

        self.rerender()

    @override
    def rerender(self) -> None:
        """
        Rerendering.
        """

        self.text_input_frame = pygame.Rect(0, 0, self.width//2, self.height//10)

        xc, yc = graphics.get_center_with_rect(self.frame_dim, self.text_input_frame)
        # setting the centered position
        self.text_input_frame.x = xc
        self.text_input_frame.y = yc
        # creating the text input
        self.text_input = TextInput(
            self.text_input_frame,
            focus_group=self.focus_group,
            has_focus=True  # starts out with focus
        )

        self.raise_prerender_flag()
        self.intro_delay_clock.start()

    @override
    def prerender(self) -> None:
        """
        Prerendering.
        """
        self.surface.fill((*self.background_color, self.background_alpha))
        self.text_input.render(self.surface)

    def set_input_text(self, text: str = "") -> None:
        """
        Sets the text for self.input_text_frame.
        """
        self.text_input.set_text(text)

    def get_input_text(self) -> str:
        """
        Returns the text of self.text_input.
        """
        return self.text_input.get_text()

    def reset_exit_type(self) -> None:
        """
        Resets the exit type.
        """
        self._exit_type = None

    def exit_with_enter(self) -> bool:
        """
        Is true if this frame exited with an enter pressed.
        """
        return (self._exit_type == FocusedTextInputFrame.TEXT_ENTERED)

    def exit_with_escape(self) -> bool:
        """
        Is true if this frame was aborted.
        """
        return (self._exit_type == FocusedTextInputFrame.ESCAPE)

    @override
    def tick(self) -> None:
        """
        Tick function.
        """

        if self.intro_delay_clock.elapsed() > self.intro_delay:
            self.manage_pygame_events()

        ret: Frame = self.text_input.tick()
        # polling textinput events
        for event in self.text_input.poll_events():

            # propagating events
            self.push_event(event)

            if event.type == TextInput.EventTypes.TEXT_ENTERED:
                self._exit_type = FocusedTextInputFrame.TEXT_ENTERED
                self.raise_exit_flag()

        if self.exit_flag_raised():
            return None

        if self.is_focused():
            # checking for any movement key
            if self.key_pressed(pygame.K_LEFT) or self.key_pressed(KeyAlternatives.LEFT_ALTERNATIVE)\
                    or self.key_pressed(pygame.K_RIGHT) or self.key_pressed(KeyAlternatives.RIGHT_ALTERNATIVE)\
                    or self.key_pressed(pygame.K_UP) or self.key_pressed(KeyAlternatives.UP_ALTERNATIVE)\
                    or self.key_pressed(pygame.K_DOWN) or self.key_pressed(KeyAlternatives.DOWN_ALTERNATIVE):

                self.text_input.focus()

            if (self.key_pressed(KeyAlternatives.BACK_KEY) or self.key_pressed(pygame.K_ESCAPE)) and self.escape_released:
                self._exit_type = FocusedTextInputFrame.ESCAPE
                self.raise_exit_flag()

            if not (self.key_pressed(KeyAlternatives.BACK_KEY) and self.key_pressed(pygame.K_ESCAPE)) and not self.escape_released:
                self.escape_released = True

        if not self.text_input.is_focused() and not self.is_focused():
            self.focus()
            self.escape_released = False

        if self.text_input.is_focused():
            self.raise_prerender_flag()

        if self.prerender_flag_raised():
            self.prerender()
            self.reset_prerender_flag()

        return self
