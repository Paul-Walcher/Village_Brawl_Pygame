from __future__ import annotations
from typing import Any, Callable, override

import os
import pygame
import threading

from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives
import graphics
from context_data import ContextData
from clock import Clock
from modules import Modules
import constants

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.choose_explorer_frame import ChooseExplorerFrame
from Frames.widgets.label import Label
from Frames.widgets.button import Button

class LoadPlaysetFrame(Frame):

    def __init__(
                    self,
                    data: Any = None,
                    frame_dim: pygame.Rect = None,
                    parent_frame: Frame = None,
                    focus_group: str = "",
                    has_focus: bool = True
                    ):

        super().__init__(
                            frame_enum=FrameEnums.LOAD_PLAYSET_FRAME,
                            data=data,
                            frame_dim=frame_dim,
                            parent_frame=parent_frame,
                            focus_group=focus_group,
                            has_focus=has_focus

                        )

        self.loading_text: str = "Loading"
        """
        Text shown while loading
        """
        self.n_dots: int = 0
        """
        Current number of dots in the animation.
        """
        self.max_dots: int = 5
        """
        Maximum number of dots in the animation.
        """
        self.loading_text_wp: float = 0.5
        """
        Width of the loading text relative to self.width.
        """
        self.loading_text_hp: float = 0.4
        """
        Height of the loading text relative to self.height.
        """
        self.rendered_loading_text: pygame.Surface = None
        """
        The Rendered Loading text.
        """
        self.rendered_loading_text_pos: tuple[int, int] = None
        """
        Position of the rendered text.
        """
        self.loading_text_fontsize: int = None
        """
        The loading text fontsize.
        """
        self.loading_delay: int = 200#ms
        """
        Loading delay for the text animation.
        """
        self.loading_clock: Clock = Clock()
        """
        The clock for the loading animation.
        """
        self.extra_clock: Clock = Clock()
        """
        The extra clock, for waiting for constants.__ADDITIONAL_LOAD_TIME__.
        """
        self.loading_finished: bool = False
        """
        If the loading is finished or not.
        """
        self.loading_lock: threading.Lock = threading.Lock()
        """
        Lock for setting self.loading finished.
        """
        self.intro_delay: float = 100#ms
        """
        Intro delay.
        """
        self.intro_delay_clock: Clock = Clock()
        """
        Clock for the intro delay.
        """
        self.thread: threading.Thread = None
        """
        The thread loading the playset.
        """
        self.rerender()

    @override
    def rerender(self) -> None:
        """
        Recalculating and rerendering from scratch.
        """

        self.loading_finished = False
        self.n_dots = 0

        text_rect: pygame.Rect = pygame.Rect(
                                                0, 0,
                                                int(self.width * self.loading_text_hp),
                                                int(self.height * self.loading_text_hp)
                                            )
        self.loading_text_fontsize = graphics.get_fontsize(font=Fonts.STANDARD_FONT, lines=[self.loading_text + "." * self.max_dots], frame=text_rect)
        self.loading_text_pos = graphics.get_center_with_rect(outer_rect=self.frame_dim, inner_rect=text_rect)

        self.render_loading_text()

        self.reset_exit_flag()
        self._next_frame = None

        self.prerender()

        self.loading_clock.start()
        self.intro_delay_clock.start()

        #starting the loading thread
        self.thread = threading.Thread(target=self.load_playset)
        self.thread.start()

    @override
    def prerender(self) -> None:
        """
        Rendering function.
        """

        self.surface.fill(Colors.BLACK)
        self.surface.blit(self.rendered_loading_text, self.loading_text_pos)


    def render_loading_text(self) ->  None:
        """
        Renders the loading text.
        """

        self.rendered_loading_text = graphics.render_text(  Fonts.STANDARD_FONT,
                                                            self.loading_text_fontsize,
                                                            self.loading_text + "."*self.n_dots,
                                                            Colors.STANDARD_TEXT_COLOR
                                                            )

    def load_playset(self) -> None:
        """
        Used by self.thread to load the playset in contextdata.current_playset
        """
        if type(self.data) == ContextData:
            self.data.modules = Modules.load_playset(self.data.current_playset)
        else:
            return

        with self.loading_lock:
            self.loading_finished = True
            self.extra_clock.start()

    @override
    def tick(self):

        self.manage_pygame_events()

        if self.exit_flag_raised():
            if self._next_frame is not None:
                self._next_frame.rerender()
                self._next_frame.focus()
            return self._next_frame

        if self.loading_clock.elapsed() > self.loading_delay:

            self.n_dots += 1
            self.n_dots %= self.max_dots

            self.render_loading_text()
            self.loading_clock.start()

        with self.loading_lock:
            if self.loading_finished and self.extra_clock.elapsed() > constants.__ADDITIONAL_LOAD_TIME__:

                self._next_frame = ChooseExplorerFrame(
                                                data=self.data,
                                                frame_dim=self.frame_dim.copy(),
                                                parent_frame=None, #resetting parent_frame_list
                                                focus_group=self.focus_group,
                                                has_focus=True
                                                )
                self.raise_exit_flag()

        self.prerender()


        return self
