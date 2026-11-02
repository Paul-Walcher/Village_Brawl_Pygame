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
    KeyAlternatives
)
import graphics
from graphics import page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t
from clock import Clock
from modules import Modules
import constants
from event_queue_manager import Event

from Frames.widgets.slider import Slider

class TextSlider(Slider):

    def __init__(
        self,
        frame_dim,
        text_pages: list[colored_page_t], #the list of colored pages
        selected_text_pages: list[colored_page_t] = None, #the list of colored pages for when the text is selected
        back_text_pages: list[colored_page_t] = None, #back text pages
        selected_back_text_pages: list[colored_page_t] = None,
        font=Fonts.MINECRAFT,
        sliding_duration=500,  # ms
        select_animation_duration=400,#ms
        flip_duration=400,#ms
        text_alphas=None,
        text_span=1,
        background_color=Colors.TRANSPARENT,
        size_decrease_scale=0.5,
        horizontal=True,
        start_index=0,
        cutoff=False,
        max_slides=10,
        line_margin_percentage=0.05,
        text_color=Colors.STANDARD_TEXT_COLOR
    ):

        self.text_pages = text_pages
        self.selected_text_pages = (self.text_pages if selected_text_pages is None else selected_text_pages)
        self.back_text_pages = (back_text_pages if back_text_pages is not None else text_pages)
        self.selected_back_text_pages = (self.selected_text_pages if selected_back_text_pages is None else selected_back_text_pages)
        self.font = font
        self.text_color = text_color
        self.line_margin_percentage: float = line_margin_percentage

        Slider.__init__(
                        self,
                        frame_dim=frame_dim,
                        sliding_duration=sliding_duration,
                        select_animation_duration=select_animation_duration,
                        alphas=text_alphas,
                        span=text_span,
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
        self.selected_surfaces = []

        for page in self.text_pages:

            surf: pygame.Surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            rendered_text: rendered_surface_position_tuples_t = graphics.render_page_from_chars_color(
                                                                                                        font=self.font,
                                                                                                        page=page,
                                                                                                        frame=pygame.Rect(0, 0, self.width, self.height),
                                                                                                        text_color=Colors.STANDARD_TEXT_COLOR,
                                                                                                        centered=True,
                                                                                                        vertical_centered=True,
                                                                                                        line_margin_as_percentage=self.line_margin_percentage
                                                                                                    )
            graphics.render_rendered_surface_position_tuples(surf, rendered_text)
            self.surfaces.append(surf)


        for page in self.selected_text_pages:

            surf: pygame.Surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            rendered_text: rendered_surface_position_tuples_t = graphics.render_page_from_chars_color(
                                                                                                        font=self.font,
                                                                                                        page=page,
                                                                                                        frame=pygame.Rect(0, 0, self.width, self.height),
                                                                                                        text_color=Colors.STANDARD_TEXT_COLOR,
                                                                                                        centered=True,
                                                                                                        vertical_centered=True,
                                                                                                        line_margin_as_percentage=self.line_margin_percentage
                                                                                                    )
            graphics.render_rendered_surface_position_tuples(surf, rendered_text)
            self.selected_surfaces.append(surf)



    def create_back_surfaces(self):

        self.back_surfaces = []
        self.selected_back_surfaces = []

        for page in self.back_text_pages:

            surf: pygame.Surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            rendered_text: rendered_surface_position_tuples_t = graphics.render_page_from_chars_color(
                                                                                                        font=self.font,
                                                                                                        page=page,
                                                                                                        frame=pygame.Rect(0, 0, self.width, self.height),
                                                                                                        text_color=Colors.STANDARD_TEXT_COLOR,
                                                                                                        centered=True,
                                                                                                        vertical_centered=True,
                                                                                                        line_margin_as_percentage=self.line_margin_percentage
                                                                                                    )
            graphics.render_rendered_surface_position_tuples(surf, rendered_text)
            self.back_surfaces.append(surf)


        for page in self.selected_back_text_pages:

            surf: pygame.Surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            rendered_text: rendered_surface_position_tuples_t = graphics.render_page_from_chars_color(
                                                                                                        font=self.font,
                                                                                                        page=page,
                                                                                                        frame=pygame.Rect(0, 0, self.width, self.height),
                                                                                                        text_color=Colors.STANDARD_TEXT_COLOR,
                                                                                                        centered=True,
                                                                                                        vertical_centered=True,
                                                                                                        line_margin_as_percentage=self.line_margin_percentage
                                                                                                    )
            graphics.render_rendered_surface_position_tuples(surf, rendered_text)
            self.selected_back_surfaces.append(surf)
