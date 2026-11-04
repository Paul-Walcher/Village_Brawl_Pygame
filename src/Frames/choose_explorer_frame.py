from __future__ import annotations
from typing import Any, Callable, Type

import os
import pygame
import threading

import constants
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, R_ID
import graphics
from clock import Clock
from modules import Modules

from templates.explorer_card_template import Explorer_Card_Template, ExplorerCardInfo

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.explorer_info_frame import ExplorerInfoFrame
from Frames.widgets.label import Label
from Frames.widgets.custom_same_size_slider import CustomSameSizeSlider

from context_data import ContextData

class ChooseExplorerFrame(Frame):
    """
    Frame for choosing an explorer.
    """
    #states
    IDLE: int = R_ID()
    SLIDING: int = R_ID()
    INFO_FRAME_ACTIVE: int = R_ID()
    INFO_FRAME_SLIDING_IN: int = R_ID()
    INFO_FRAME_SLIDING_OUT: int = R_ID()

    def __init__(
                    self,
                    data: Any = None,
                    frame_dim: pygame.Rect = None,
                    parent_frame: Frame = None,
                    focus_group: str = "",
                    has_focus: bool = True

                    ):

        self.info_frame: ExplorerInfoFrame = None
        """
        The info frame shown. Set before init for bind_events.
        """
        super().__init__(
                            frame_enum=FrameEnums.CHOOSE_EXPLORER_FRAME,
                            data=data,
                            frame_dim=frame_dim,
                            parent_frame=parent_frame,
                            focus_group=focus_group,
                            has_focus=has_focus
                            )

        self.modules: Modules = None
        """
        Reference to the loaded modules.
        """
        if type(self.data) == ContextData:
            self.modules = self.data.modules

        #getting all explorers
        self.explorer_enums: list[int] = list(self.modules.enums.ExplorerEnums)
        """
        List of loaded explorer enums.
        """
        self.explorer_refs: list[Type(Explorer_Card_Template)] = [self.modules.mappings.explorer_mappings[explorer_enum] for explorer_enum in self.explorer_enums]
        """
        List of loaded explorer classes
        """
        self.explorer_infos: list[ExplorerCardInfo] = [ref.info() for ref in self.explorer_refs]
        """
        List of explorer infos.
        """
        self.explorer_index: int = 0
        """
        index of the current explorer shown.
        """
        self.intro_delay: float = 100#ms
        """
        Intro delay when frame is rerendered.
        """
        self.intro_delay_clock: Clock = Clock()
        """
        The intro delay clock.
        """
        self.state: int = ChooseExplorerFrame.IDLE
        """
        State of this frame.
        """
        self.info_frame_sliding_time: float = 500#ms
        """
        Time the sliding animation of the info frame takes.
        """
        self.info_frame_clock: Clock = Clock()
        """
        Clock for the info frame sliding animation.
        """
        self.explorer_slider: CustomSameSizeSlider = None
        """
        Slider for the explorer.
        """

        self.rerender()

    def rerender(self):
        """
        Rerendering.
        """

        #creating the image surfaces
        explorer_surfaces: list[pygame.Surface] = self.create_explorer_surfaces()

        self.explorer_slider = CustomSameSizeSlider(
                                                        frame_dim=self.frame_dim.copy(),
                                                        surfaces=explorer_surfaces,
                                                        span=0,
                                                        sliding_duration=250#ms
                                                    )

        self._next_frame = None
        self.state = ChooseExplorerFrame.IDLE
        self.intro_delay_clock.start()

    def create_explorer_surfaces(self) -> list[pygame.Surface]:
        """
        Creates the explorer surfaces.
        """
        headline_height_p: float = 0.2
        image_height_p: float = 0.8
        headline_area, image_area = graphics.split_rect_vertically(self.frame_dim, [headline_height_p, image_height_p])

        #compressing the headline area
        headline_frame_dim = graphics.apply_margins(headline_area, 0.5, 0.1)
        image_frame_dim = graphics.apply_margins(image_area, 0.0, 0.1)

        esurfaces: list[pygame.Surface] = []

        for i in range(len(self.explorer_enums)):

            einfo = self.explorer_infos[i]

            rendered_headline = graphics.render_page_from_chars_color(
                                                                        font=Fonts.STANDARD_FONT,
                                                                        page=graphics.page_to_colored_page(einfo.name, einfo.name_color),
                                                                        frame=headline_frame_dim,
                                                                        centered=True,
                                                                        vertical_centered=True
                                                                        )
            rendered_image, rendered_image_pos = graphics.img_load_and_position(
                                                                                    img_path=einfo.card_image_path,
                                                                                    frame=image_frame_dim
                                                                                )

            esurf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            for text, pos in rendered_headline:
                esurf.blit(text, pos)

            esurf.blit(rendered_image, rendered_image_pos)

            esurfaces.append(esurf)

        return esurfaces




    def initialize_info_frame(self):


        iframe = pygame.Rect(self.width, 0, self.width // 2, self.height)
        self.info_frame = ExplorerInfoFrame(self.explorer_enums[self.explorer_index], self.data, iframe, self)

        self.state = ChooseExplorerFrame.INFO_FRAME_SLIDING_IN
        self.info_frame_clock.start()

    def deinitialize_info_frame(self):

        self.state = ChooseExplorerFrame.IDLE
        self.info_frame = None

    def finalize_info_frame(self):

        final_frame = pygame.Rect(self.width//2, 0, self.width//2, self.height)
        self.info_frame.frame_dim = final_frame

        self.state = ChooseExplorerFrame.INFO_FRAME_ACTIVE

        #adding callback
        self.add_pygame_key_callback(key=pygame.K_i, data=None, putback=True, func=self.i_pressed_info_frame_active)
        self.add_pygame_key_callback(key=KeyAlternatives.BACK_KEY, data=None, putback=True, func=self.i_pressed_info_frame_active)

    def bind_events(self):

        if self.is_focused():

            self.add_default_escape_callback()

            self.add_pygame_key_callback(pygame.K_LEFT, None, putback=False, func=self.left_pressed)
            self.add_pygame_key_callback(KeyAlternatives.LEFT_ALTERNATIVE, None, putback=False, func=self.left_pressed)

            self.add_pygame_key_callback(pygame.K_RIGHT, None, putback=False, func=self.right_pressed)
            self.add_pygame_key_callback(KeyAlternatives.RIGHT_ALTERNATIVE, None, putback=False, func=self.right_pressed)

            self.add_pygame_key_callback(pygame.K_i, None, putback=False, func=self.i_pressed)


    def left_pressed(self, event, data):
        """
        Starts sliding if left is pressed
        """
        if self.state == ChooseExplorerFrame.IDLE:

            self.explorer_slider.slide_left()
            self.state = ChooseExplorerFrame.SLIDING

    def right_pressed(self, event, data):
        """
        Starts sliding if right is pressed
        """
        if self.state == ChooseExplorerFrame.IDLE:

            self.explorer_slider.slide_right()
            self.state = ChooseExplorerFrame.SLIDING

    def i_pressed(self, event, data):

        if self.state == ChooseExplorerFrame.IDLE:
            self.initialize_info_frame()

    def i_pressed_info_frame_active(self, event, data):
        self.info_frame.raise_exit_flag()


    def tick(self):

        if self.intro_delay_clock.elapsed() > self.intro_delay:
            self.manage_pygame_events()

        if self.exit_flag_raised():
            if self._next_frame is not None:
                self._next_frame.rerender()
                self._next_frame.focus()
            return self._next_frame

        self.explorer_slider.tick()

        for event in self.explorer_slider.poll_events():
            if event.type == CustomSameSizeSlider.EventTypes.SLIDING_ANIMATION_ENDED:
                self.state = ChooseExplorerFrame.IDLE

        if self.info_frame is not None:
            ret: Frame = self.info_frame.tick()

            if ret is None:
                if self.state != ChooseExplorerFrame.INFO_FRAME_SLIDING_OUT:
                    self.state = ChooseExplorerFrame.INFO_FRAME_SLIDING_OUT
                    self.info_frame_clock.start()


        if self.state == ChooseExplorerFrame.INFO_FRAME_SLIDING_IN:

            if self.info_frame_clock.elapsed() >= self.info_frame_sliding_time:
                self.finalize_info_frame()
            else:
                info_frame_frame_dim = pygame.Rect(int(self.width - (self.info_frame_clock.elapsed() / self.info_frame_sliding_time * self.width//2)), 0, self.width//2, self.height)
                self.info_frame.frame_dim = info_frame_frame_dim

        elif self.state == ChooseExplorerFrame.INFO_FRAME_SLIDING_OUT:

            if self.info_frame_clock.elapsed() >= self.info_frame_sliding_time:
                self.deinitialize_info_frame()
            else:
                info_frame_frame = pygame.Rect(int(self.width // 2 + (self.info_frame_clock.elapsed() / self.info_frame_sliding_time * self.width//2)), 0, self.width//2, self.height)
                self.info_frame.frame_dim = info_frame_frame


        return self


    def render(self, screen):

        screen.fill(Colors.BLACK)

        self.explorer_slider.render(screen)

        if self.info_frame is not None:
            self.info_frame.render(screen)
