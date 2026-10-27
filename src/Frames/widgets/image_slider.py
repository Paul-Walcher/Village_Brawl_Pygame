import os
import pygame
import threading

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.slider import Slider
from constants import (
    PLAYSETS_FOLDER,
    Colors,
    Fonts,
    Fontsizes,
    KeyAlternatives
)
from enum import Enum, auto
import graphics
from clock import Clock
from modules import Modules
import constants
from event_queue_manager import Event


class ImageSlider(Slider):



    def __init__(
        self,
        images,
        frame_dim,
        back_images=None,
        sliding_duration=500,  # ms
        select_animation_duration=800,#ms
        images_alphas=None,
        images_span=1,
        background_color=Colors.TRANSPARENT,
        size_decrease_scale=0.5,
        horizontal=True,
        start_index=0,
        cutoff=False,
        max_slides=10,
        flip_duration=400#ms
    ):

        self.images = images
        self.back_images = (back_images if back_images is not None else images)

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
        self.surfaces = list(map(lambda x: graphics.render_image(x), self.images))

    def create_back_surfaces(self):
        self.back_surfaces = list(map(lambda x: graphics.render_image(x), self.back_images))
