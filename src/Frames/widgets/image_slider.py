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
from clock import Clock
from event_queue_manager import Event

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.slider import Slider


class ImageSlider(Slider):
    """
    Inherits from slider.
    Displays the images given onto surfaces.
    """

    def __init__(
                    self,
                    frame_dim: pygame.Rect,

                    images: list[str],#the image list
                    selected_images: list[str] = None, #the selected images
                    back_images: list[str] = None, #back images
                    selected_back_images: list[str] = None, #back images for when an image is selected

                    sliding_duration: float = 500,  # ms
                    select_animation_duration: float = 400,#ms
                    flip_duration: float = 400,#ms
                    images_alphas: list[int] = None,
                    images_span: int = 1,
                    background_color: color_t = Colors.TRANSPARENT,
                    size_decrease_scale: float = 0.5,
                    horizontal: bool = True,
                    start_index: int = 0,
                    cutoff: bool = False,
                    max_slides: int = 10
                ):

        self.images: list[str] = images
        """
        List of image paths for the standard surfaces.
        """
        self.selected_images: list[str] = (selected_images if selected_images is not None else images)
        """
        List of image paths for the selected surfaces.
        self.images is used if it is None.
        """
        self.back_images: list[str] = (back_images if back_images is not None else images)
        """
        List of back image paths for the standard surfaces.
        self.images is used if it is None.
        """
        self.selected_back_images: list[str] = (selected_back_images if selected_back_images is not None else self.selected_images)
        """
        List of image paths for the selected back surfaces.
        self.selected_images is used if it is None.
        """

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
    @override
    def create_surfaces(self) -> None:
        """
        Creates all surfaces by just rendering the images.
        """
        self.surfaces = list(map(lambda x: graphics.render_image(x), self.images))
        self.selected_surfaces = list(map(lambda x: graphics.render_image(x), self.selected_images))

    @override
    def create_back_surfaces(self) -> None:
        """
        Creates all back surfaces by just rendering the back images.
        """
        self.back_surfaces = list(map(lambda x: graphics.render_image(x), self.back_images))
        self.selected_back_surfaces = list(map(lambda x: graphics.render_image(x), self.selected_back_images))
