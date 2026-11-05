from __future__ import annotations
from typing import Any, Callable

import pygame

from constants import Colors
from Frames.widgets.slider import Slider

class CustomSlider(Slider):
    """
    Takes already created surfaces to make a slider.
    """

    def __init__(
        self,
        frame_dim,
        surfaces, #list of the surfaces.
        selected_surfaces=None, #selected surfaces
        back_surfaces=None,#list of back surfaces
        selected_back_surfaces=None,#selected back surfaces.
        sliding_duration=500,  # ms
        select_animation_duration=400,#ms
        alphas=None,
        span=1,
        background_color=Colors.TRANSPARENT,
        size_decrease_scale=0.5,
        horizontal=True,
        start_index=0,
        cutoff=False,
        max_slides=2,
        flip_duration=400,#ms
        slide_input_delay=250#ms
    ):


        Slider.__init__(
                        self,
                        frame_dim,
                        surface_distance_p = surface_distance_p,
                        sliding_duration=sliding_duration,  # ms
                        select_animation_duration=select_animation_duration,#ms
                        alphas=alphas,
                        span=span,
                        background_color=background_color,
                        size_decrease_scale=size_decrease_scale,
                        horizontal=horizontal,
                        start_index=start_index,
                        cutoff=cutoff,
                        max_slides=max_slides,
                        flip_duration=flip_duration,#ms
                        slide_input_delay=slide_input_delay#ms
                        )

        self.internal_surfaces: list[pygame.Surface] = surfaces
        """
        The given surfaces.
        """
        self.internal_selected_surfaces: list[pygame.Surface] = (selected_surfaces if selected_surfaces is not None else self.surfaces.copy())
        """
        The selected surfaces. If they are None, they keep the same surface references.
        """
        self.internal_back_surfaces: list[pygame.Surface] = (back_surfaces if back_surfaces is not None else self.surfaces.copy())
        """
        The back surfaces.
        """
        self.internal_selected_back_surfaces: list[pygame.Surface] = (selected_back_surfaces if selected_back_surfaces is not None else self.selected_surfaces.copy())
        """
        Selected back surfaces.
        """

    def create_surfaces(self) -> None:
        """
        Copies surfaces.
        """
        self.surfaces = [surf.copy() for surf in self.internal_surfaces]
        self.selected_surfaces = [surf.copy() for surf in self.internal_selected_surfaces]

    def create_back_surfaces(self) -> None:
        """
        Already has all surfaces.
        """
        self.back_surfaces = [surf.copy() for surf in self.internal_back_surfaces]
        self.selected_back_surfaces = [surf.copy() for surf in self.internal_selected_back_surfaces]
