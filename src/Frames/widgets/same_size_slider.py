from __future__ import annotations
from typing import Any, Callable, override

import pygame

import graphics
from constants import (
                        Colors,
                        color_t
                        )
from event_queue_manager import Event

from Frames.widgets.slider import Slider

class SameSizeSlider(Slider):
    """
    Creates a slider with same sized surfaces.
    """
    def __init__(
                    self,
                    frame_dim: pygame.Rect,
                    surface_distance_p: float = 0.0,
                    span: int = 1,
                    background_color: color_t = Colors.TRANSPARENT,
                    horizontal: bool = True,
                    start_index: int = 0,
                    cutoff: bool = False,
                    max_slides: int = 2,

                    sliding_duration: float = 500,  # ms
                    select_animation_duration: float = 400,#ms
                    flip_duration: float = 400,#ms
                    slide_input_delay: float = 250#ms
                ):

        self.surface_distance_p: float = surface_distance_p
        """
        The distance between surfaces as a percentage of self.width.
        """
        self.surface_distance: int = None
        """
        Actual surface distance, calculated in self.rerender.
        """

        Slider.__init__(
                        self,
                        frame_dim,
                        sliding_duration=sliding_duration,  # ms
                        select_animation_duration=select_animation_duration,#ms
                        alphas=None,
                        span=span,
                        background_color=background_color,
                        size_decrease_scale=Slider.NO_SIZE_DECREASE,
                        horizontal=horizontal,
                        start_index=start_index,
                        cutoff=cutoff,
                        max_slides=max_slides,
                        flip_duration=flip_duration,#ms
                        slide_input_delay=slide_input_delay#ms
                        )


    @override
    def rerender_images(self) -> None:
        """
        Rerendering.
        """

        self.surface_distance = int(self.surface_distance_p * self.width)
        self.fixed_image_positions = self.get_fixed_image_positions()

        self.top_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.bottom_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.rendered_surfaces = []
        self.rects = []

        #indices referencing the surfaces
        self.indices =   ([(self.surface_index - i - 1) % len(self.surfaces) for i in range(self.span)]
                    + [self.surface_index]
                    + [(self.surface_index + i + 1) % len(self.surfaces) for i in range(self.span)]
                    )

        self.original_indices = ([self.surface_index - i - 1 for i in range(self.span)]
                                + [self.surface_index]
                                + [self.surface_index + i + 1 for i in range(self.span)])


        for i in range(1 + 2 * self.span):

            start_pos, length = self.fixed_image_positions[i]
            rect = None

            if self.horizontal:
                rect = pygame.Rect(
                                    start_pos,
                                    0,
                                    length,
                                    self.height
                                    )

            else:

                rect = pygame.Rect(
                                    0,
                                    start_pos,
                                    self.width,
                                    length
                                )

            surf = None
            if i == self.span:
                surf = self.selected_surfaces[self.indices[i]]
            else:
                surf = self.surfaces[self.indices[i]]

            surf = graphics.scale_surface(surf, self.get_scale_fraction(surf, rect))
            sx, sy = graphics.get_center_with_surface(surf, rect)
            rendered: bool = self.is_rendered(self.original_indices[i])

            self.rendered_surfaces.append([
                                            surf,
                                            sx,
                                            sy,
                                            rendered
                                            ])

            self.rects.append(rect)

        self.prerender()


    @override
    def get_fixed_image_positions(self) -> list[tuple[int, int]]:
        """
        Creates the fixed image positions.
        """
        surface_distance_covered: int = self.surface_distance * 2 * self.span
        remaining_space: int = (
                                self.width - surface_distance_covered if self.horizontal\
                                else self.height - surface_distance_covered
                                )

        space_split: int = remaining_space // (1 + 2 * self.span)

        dspaces: list[tuple[int, int]] = []
        #list of position tuples: (start, length)
        cx: int = 0
        """
        Start position.
        """
        for i in range(1 + 2 * self.span):

            dspaces.append((cx, space_split))
            cx += space_split + self.surface_distance

        return dspaces

    @override
    def initialize_slide_left(self) -> None:
        """
        Overwrites slide left.
        """
        #enter new image from the right

        surf_index: int = (self.indices[-1] + 1) % len(self.surfaces)

        new_surface: pygame.Surface = self.surfaces[surf_index]
        new_surface = graphics.scale_surface(new_surface, self.get_scale_fraction(new_surface, self.rects[-1]))

        new_rect = self.rects[-1].copy()
        if self.horizontal:
            new_rect.x += self.surface_distance + new_rect.width
        else:
            new_rect.y += self.surface_distance + new_rect.height

        self.indices.append(surf_index)
        self.original_indices.append(self.original_indices[-1] + 1)

        self.rendered_surfaces.append([
                                        new_surface,
                                        new_rect.x,
                                        new_rect.y,
                                        self.is_rendered(self.original_indices[-1])
                                        ])
        self.rects.append(new_rect)

        #building starting positions and end positions
        self.start_positions = [[x, y] for (surf, x, y, rend) in self.rendered_surfaces]
        self.target_positions = self.start_positions.copy()[:-1]

        #adding first position
        target_rect = self.rects[0].copy()
        if self.horizontal:
            target_rect.x -= (self.surface_distance + target_rect.width)
        else:
            target_rect.y -= (self.surface_distance + target_rect.height)

        self.target_positions.insert(0, (target_rect.x, target_rect.y))

        self.sliding_clock.start()

    @override
    def render_slide_left(self) -> None:
        """
        Renders slide left.
        """
        progress = self.sliding_clock.elapsed() / self.sliding_duration
        progress = min(1.0, progress)

        rimages = []

        for i in range(len(self.indices)):

            surf = self.rendered_surfaces[i][0]

            x = (self.start_positions[i][0] + (self.target_positions[i][0] - self.start_positions[i][0]) * progress)
            y = (self.start_positions[i][1] + (self.target_positions[i][1] - self.start_positions[i][1]) * progress)

            rendered = self.is_rendered(self.original_indices[i])

            rimages.append(
                            [
                                surf,
                                int(x),
                                int(y),
                                rendered
                            ]
                        )

        self.rendered_surfaces = rimages
        self.prerender()

    @override
    def finalize_slide_left(self) -> None:
        """
        Finalizes slide left.
        """

        # Moving left means moving to the next image.
        self.surface_index = (self.surface_index + 1) % len(self.surfaces)

        self.slides += 1
        self.state = Slider.NOT_SLIDING
        self.push_event(Event(SameSizeSlider.EventTypes.SLIDING_ANIMATION_ENDED, None))

        # Rebuild everything from the actual logical state.
        self.rerender_images()

    @override
    def initialize_slide_right(self) -> None:
        """
        Overwrites initialize slide right.
        """
        #enter new image from the left

        surf_index: int = (self.indices[0] - 1) % len(self.surfaces)

        new_surface: pygame.Surface = self.surfaces[surf_index]
        new_surface = graphics.scale_surface(new_surface, self.get_scale_fraction(new_surface, self.rects[0]))

        new_rect = self.rects[0].copy()
        if self.horizontal:
            new_rect.x -= (self.surface_distance + new_rect.width)
        else:
            new_rect.y -= (self.surface_distance + new_rect.height)

        self.indices.insert(0, surf_index)
        self.original_indices.insert(0, self.original_indices[0] - 1)

        self.rendered_surfaces.insert(0, [
                                        new_surface,
                                        new_rect.x,
                                        new_rect.y,
                                        self.is_rendered(self.original_indices[0])
                                        ])
        self.rects.insert(0, new_rect)

        #building starting positions and end positions
        self.start_positions = [[x, y] for (surf, x, y, rend) in self.rendered_surfaces]
        self.target_positions = self.start_positions.copy()[1:]

        #adding first position
        target_rect = self.rects[-1].copy()
        if self.horizontal:
            target_rect.x += (self.surface_distance + target_rect.width)
        else:
            target_rect.y += (self.surface_distance + target_rect.height)

        self.target_positions.append((target_rect.x, target_rect.y))

        self.sliding_clock.start()

    @override
    def render_slide_right(self) -> None:
        """
        Rendering slide right.
        """

        progress = self.sliding_clock.elapsed() / self.sliding_duration
        progress = min(1.0, progress)

        rimages = []

        for i in range(len(self.indices)):

            surf = self.rendered_surfaces[i][0]

            x = (self.start_positions[i][0] + (self.target_positions[i][0] - self.start_positions[i][0]) * progress)
            y = (self.start_positions[i][1] + (self.target_positions[i][1] - self.start_positions[i][1]) * progress)

            rendered = self.is_rendered(self.original_indices[i])

            rimages.append(
                            [
                                surf,
                                int(x),
                                int(y),
                                rendered
                            ]
                        )

        self.rendered_surfaces = rimages
        self.prerender()

    @override
    def finalize_slide_right(self) -> None:
        """
        Finalizes slide right.
        """
        # Moving left means moving to the next image.
        self.surface_index = (self.surface_index - 1) % len(self.surfaces)

        self.slides -= 1
        self.state = Slider.NOT_SLIDING
        self.push_event(Event(SameSizeSlider.EventTypes.SLIDING_ANIMATION_ENDED, None))

        # Rebuild everything from the actual logical state.
        self.rerender_images()
