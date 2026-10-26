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
from event_queue_manager import Event

from Frames.widgets.slider import Slider

class TextSlider(Slider):

    def __init__(
        self,
        text,
        frame_dim,
        back_text=None,
        font=Fonts.MINECRAFT,
        sliding_duration=500,  # ms
        select_animation_duration=800,#ms
        flip_duration=400,#ms
        images_alphas=None,
        images_span=1,
        background_color=Colors.TRANSPARENT,
        size_decrease_scale=0.5,
        horizontal=True,
        start_index=0,
        cutoff=False,
        max_slides=10,
        line_margin_percentage=0.05,
        text_color=Colors.BLACK,
        text_is_colored=False,
        text_width_to_height_ratio=7/5
    ):

        self.text = text
        self.back_text = (back_text if back_text is not None else text)
        self.font = font
        self.text_is_colored = text_is_colored
        self.text_color = text_color
        self.text_width_to_height_ratio = text_width_to_height_ratio
        self.line_margin_width = int(line_margin_percentage * frame_dim.height)

        Slider.__init__(
                        self,
                        frame_dim=frame_dim,
                        sliding_duration=sliding_duration,
                        select_animation_duration=select_animation_duration,
                        alphas=images_alphas,
                        span=images_span,
                        background_color=background_color,
                        size_decrease_scale=size_decrease_scale,
                        horizontal=horizontal,
                        start_index=start_index,
                        cutoff=cutoff,
                        max_slides=max_slides,
                        flip_duration=flip_duration
                        )

    def create_surfaces(self):

        self.surfaces = []

        ssize = (int(100 * self.text_width_to_height_ratio), 100)

        if self.text_is_colored:

            for i in range(len(self.text)):
                surf = pygame.Surface(ssize, pygame.SRCALPHA)
                txt = graphics.render_page_from_chars_color(self.font, self.text[i],
                                                            pygame.Rect(0, 0, *ssize),
                                                            text_color=self.text_color,
                                                            centered=True,
                                                            vertical_centered=True,
                                                            line_margin=self.line_margin_width
                                                            )

                for s, pos in txt:
                    surf.blit(s, pos)

                self.surfaces.append(surf)

        else:

            for i in range(len(self.text)):
                surf = pygame.Surface(ssize, pygame.SRCALPHA)
                txt = graphics.render_page_from_chars(self.font, self.text[i],
                                                            pygame.Rect(0, 0, *ssize),
                                                            text_color=self.text_color,
                                                            centered=True,
                                                            vertical_centered=True,
                                                            line_margin=self.line_margin_width
                                                            )

                for s, pos in txt:
                    surf.blit(s, pos)

                self.surfaces.append(surf)


    def create_back_surfaces(self):

        self.back_surfaces = []

        ssize = (int(100 * self.text_width_to_height_ratio), 100)

        if self.text_is_colored:

            for i in range(len(self.back_text)):
                surf = pygame.Surface(ssize, pygame.SRCALPHA)
                txt = graphics.render_page_from_chars_color(self.font, self.back_text[i],
                                                            pygame.Rect(0, 0, *ssize),
                                                            text_color=self.text_color,
                                                            centered=True,
                                                            vertical_centered=True,
                                                            line_margin=self.line_margin_width
                                                            )

                for s, pos in txt:
                    surf.blit(s, pos)

                self.back_surfaces.append(surf)

        else:

            for i in range(len(self.back_text)):
                surf = pygame.Surface(ssize, pygame.SRCALPHA)
                txt = graphics.render_page_from_chars(self.font, self.back_text[i],
                                                            pygame.Rect(0, 0, *ssize),
                                                            text_color=self.text_color,
                                                            centered=True,
                                                            vertical_centered=True,
                                                            line_margin=self.line_margin_width
                                                            )

                for s, pos in txt:
                    surf.blit(s, pos)

                self.back_surfaces.append(surf)
