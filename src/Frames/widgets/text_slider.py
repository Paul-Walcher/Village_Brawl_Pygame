from __future__ import annotations
from typing import Type, Any, Callable, override

import pygame

from constants import (
    PLAYSETS_FOLDER,
    Colors,
    Fonts,
    Fontsizes,
    KeyAlternatives,
    color_t,
    point_t
)
import graphics
from graphics import page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t

from clock import Clock

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.slider import Slider

class TextSlider(Slider):
    """
    Inherits from Slider.

    Receives a list of colored_page_t pages.

    If selected_text_pages is None:
        selected_text_pages = text_pages

    if back_text_pages is None:
        back_text_pages = text_pages

    if selected_back_text_pages is None:
        selected_back_text_pages = selected_text_pages
    """

    SURFACE_SCALE: float = 250 #for rendering the surfaces
    """
    The height used when rendering text.
    """

    def __init__(
                    self,
                    frame_dim: pygame.Rect,

                    text_pages: list[colored_page_t], #the list of colored pages
                    selected_text_pages: list[colored_page_t] = None, #the list of colored pages for when the text is selected
                    back_text_pages: list[colored_page_t] = None, #back text pages
                    selected_back_text_pages: list[colored_page_t] = None,
                    font: pygame.font.Font = Fonts.STANDARD_FONT,
                    line_margin_percentage: float = 0.05,
                    text_color: color_t =  Colors.STANDARD_TEXT_COLOR, #default text color
                    text_aspect_ratio: float = 4.0, #width / height

                    sliding_duration: float = 500,  # ms
                    select_animation_duration: float = 400,#ms
                    flip_duration: float = 400,#ms
                    text_alphas: list[int] = None,
                    text_span: int = 1,
                    background_color: color_t = Colors.TRANSPARENT,
                    size_decrease_scale: float = 0.5,
                    horizontal: bool = True,
                    start_index: int = 0,
                    cutoff: bool = False,
                    max_slides: int = 10
                ):

        self.text_pages: list[colored_page_t] = text_pages
        """
        The standard text pages.
        """
        self.selected_text_pages: list[colored_page_t] = (self.text_pages if selected_text_pages is None else selected_text_pages)
        """
        The selected text pages. Is equal to self.text_pages if not explicitly given.
        """
        self.back_text_pages: list[colored_page_t] = (back_text_pages if back_text_pages is not None else text_pages)
        """
        The standard back text pages. Is equal to self.text_pages if not explicitly given.
        """
        self.selected_back_text_pages: list[colored_page_t] = (self.selected_text_pages if selected_back_text_pages is None else selected_back_text_pages)
        """
        The selected back text pages. Is equal to self.selected_text_pages if not explicitly given.
        """
        self.font: pygame.font.Font = font
        """
        Font the pages will be rendered in.
        """
        self.text_color: color_t = text_color
        """
        The alternative text color for graphics.render_page_from_chars_color
        """
        self.line_margin_percentage: float = line_margin_percentage
        """
        The distance between lines, as a percentage of the height of the rect
        the page will be rendered in.
        """
        self.text_aspect_ratio: float = text_aspect_ratio
        """
        Aspect ratio given as width / height
        """

        self.text_aspect_ratio_frame: pygame.Rect = pygame.Rect(
                                                                    0,
                                                                    0,
                                                                    int(self.text_aspect_ratio * TextSlider.SURFACE_SCALE),
                                                                    TextSlider.SURFACE_SCALE
                                                                )
        """
        The aspect ratio frame used for rendering text.
        """

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


    @override
    def create_surfaces(self) -> None:
        """
        Creates self.surfaces and self.selected_surfaces.
        """

        #resetting surfaces
        self.surfaces = []
        self.selected_surfaces = []

        #rendering all pages
        for page in self.text_pages:

            surf: pygame.Surface = pygame.Surface((self.text_aspect_ratio_frame.width, self.text_aspect_ratio_frame.height), pygame.SRCALPHA)

            rendered_text: rendered_surface_position_tuples_t = graphics.render_page_from_chars_color(
                                                                                                        font=self.font,
                                                                                                        page=page,
                                                                                                        frame=self.text_aspect_ratio_frame,
                                                                                                        text_color=Colors.STANDARD_TEXT_COLOR,
                                                                                                        centered=True,
                                                                                                        vertical_centered=True,
                                                                                                        line_margin_as_percentage=self.line_margin_percentage
                                                                                                    )
            graphics.render_rendered_surface_position_tuples(surf, rendered_text)
            self.surfaces.append(surf)


        for page in self.selected_text_pages:

            surf: pygame.Surface = pygame.Surface((self.text_aspect_ratio_frame.width, self.text_aspect_ratio_frame.height), pygame.SRCALPHA)

            rendered_text: rendered_surface_position_tuples_t = graphics.render_page_from_chars_color(
                                                                                                        font=self.font,
                                                                                                        page=page,
                                                                                                        frame=self.text_aspect_ratio_frame,
                                                                                                        text_color=Colors.STANDARD_TEXT_COLOR,
                                                                                                        centered=True,
                                                                                                        vertical_centered=True,
                                                                                                        line_margin_as_percentage=self.line_margin_percentage
                                                                                                    )
            graphics.render_rendered_surface_position_tuples(surf, rendered_text)
            self.selected_surfaces.append(surf)


    @override
    def create_back_surfaces(self) -> None:
        """
        Creates self.back_surfaces and self.selected_back_surfaces
        """

        self.back_surfaces = []
        self.selected_back_surfaces = []

        for page in self.back_text_pages:

            surf: pygame.Surface = pygame.Surface((self.text_aspect_ratio_frame.width, self.text_aspect_ratio_frame.height), pygame.SRCALPHA)

            rendered_text: rendered_surface_position_tuples_t = graphics.render_page_from_chars_color(
                                                                                                        font=self.font,
                                                                                                        page=page,
                                                                                                        frame=self.text_aspect_ratio_frame,
                                                                                                        text_color=Colors.STANDARD_TEXT_COLOR,
                                                                                                        centered=True,
                                                                                                        vertical_centered=True,
                                                                                                        line_margin_as_percentage=self.line_margin_percentage
                                                                                                    )
            graphics.render_rendered_surface_position_tuples(surf, rendered_text)
            self.back_surfaces.append(surf)


        for page in self.selected_back_text_pages:

            surf: pygame.Surface = pygame.Surface((self.text_aspect_ratio_frame.width, self.text_aspect_ratio_frame.height), pygame.SRCALPHA)

            rendered_text: rendered_surface_position_tuples_t = graphics.render_page_from_chars_color(
                                                                                                        font=self.font,
                                                                                                        page=page,
                                                                                                        frame=self.text_aspect_ratio_frame,
                                                                                                        text_color=Colors.STANDARD_TEXT_COLOR,
                                                                                                        centered=True,
                                                                                                        vertical_centered=True,
                                                                                                        line_margin_as_percentage=self.line_margin_percentage
                                                                                                    )
            graphics.render_rendered_surface_position_tuples(surf, rendered_text)
            self.selected_back_surfaces.append(surf)
