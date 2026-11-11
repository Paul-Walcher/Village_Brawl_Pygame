"""
Base class for sliders
"""
from __future__ import annotations
from typing import Type, Any, Callable, override

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
    R_ID,
    color_t,
    point_t,
    id_t
)
from enum import Enum, auto
import graphics
from clock import Clock
from modules import Modules
import constants
from event_queue_manager import Event
from abc import abstractmethod


class Slider(Frame):

    NO_SIZE_DECREASE = -1

    #states
    SLIDING_LEFT: id_t = R_ID()
    SLIDING_RIGHT: id_t = R_ID()
    NOT_SLIDING: id_t = R_ID()
    SELECT_ANIMATION_PLAYING: id_t = R_ID()
    FLIPPING_ANIMATION_PLAYING: id_t = R_ID()
    FLIPPING_ALL_ANIMATION_PLAYING: id_t = R_ID()

    MIN_SCALE = 0.001

    class EventTypes:

        SELECT_ANIMATION_ENDED: id_t = R_ID()
        FLIPPING_ANIMATION_ENDED: id_t = R_ID()
        SLIDING_ANIMATION_ENDED: id_t = R_ID()

    class SelectAnimationEndedEvent(Event):

        def __init__(self, selected_index: int):

            Event.__init__(self, etype=Slider.EventTypes.SELECT_ANIMATION_ENDED, data=None)

            self.selected_index: int = selected_index
            """
            The index that was selected.
            """

        @override
        def copy(self) -> Slider.SelectAnimationEndedEvent:
            return Slider.SelectAnimationEndedEvent(self.selected_index)


    class FlippingAnimationEndedEvent(Event):

        def __init__(self, selected_index: int, all_flipped: bool):

            Event.__init__(self, etype=Slider.EventTypes.FLIPPING_ANIMATION_ENDED, data=None)

            self.selected_index: int = selected_index
            """
            The index that was selected after flipping.
            """
            self.all_flipped: bool = all_flipped
            """
            If all cards were flipped or just one.
            """

        @override
        def copy(self) -> Slider.FlippingAnimationEndedEvent:
            return Slider.FlippingAnimationEndedEvent(self.selected_index, self.all_flipped)

    class SlidingAnimationEndedEvent(Event):

        def __init__(self, selected_index: int):

            Event.__init__(self, etype=Slider.EventTypes.SLIDING_ANIMATION_ENDED, data=None)

            self.selected_index: int = selected_index
            """
            The index that is selected after sliding.
            """

        @override
        def copy(self) -> Slider.SlidingAnimationEndedEvent:
            return Slider.SlidingAnimationEndedEvent(self.selected_index)

    def __init__(
                    self,
                    frame_dim: pygame.Rect,
                    sliding_duration: float = 500,  # ms
                    select_animation_duration: float = 400,#ms
                    alphas: list[int] = None,
                    span:int = 1,
                    background_color: color_t = Colors.TRANSPARENT,
                    size_decrease_scale: float = 0.5,
                    horizontal: bool= True,
                    start_index: int = 0,
                    cutoff: bool = False,
                    max_slides: int = 2,
                    flip_duration: float = 400,#ms
                    slide_input_delay: float = 250#ms
                ):

        Frame.__init__(
                        self,
                        frame_enum=FrameEnums.SLIDER_WIDGET,
                        data=None,
                        frame_dim=frame_dim,
                        focus_group=None
                        )

        self.surfaces: list[pygame.Surface] = []
        """
        List of the surfaces that are rendered in a non-selected state.
        These surfaces should be provided by subclasses, using
        self.create_surfaces.
        """
        self.selected_surfaces: list[pygame.Surface] = []
        """
        List of the surfaces that are rendered in a selected state.
        These surfaces should be provided by subclasses, using
        self.create_surfaces.
        """
        self.back_surfaces: list[pygame.Surface] = []
        """
        List of the surfaces that are rendered in a non-selected state,
        after flipping the corresponding surface.
        These surfaces should be provided by subclasses, using
        self.create_back_surfaces.
        """
        self.selected_back_surfaces: list[pygame.Surface] = []
        """
        List of the surfaces that are rendered in a selected state,
        after flipping the corresponding surface.
        These surfaces should be provided by subclasses, using
        self.create_back_surfaces.
        """
        self.flip_duration: float = flip_duration
        """
        The duration of the flip animation.
        """
        self.flipping_animation_queued: bool = False
        """
        If this is true, the flip animation will be started inside self.tick()
        """
        self.flipping_all_animation_queued: bool = False
        """
        If this is true, the flip-all animation will be started inside self.tick()
        """
        self.surface_index: int = start_index
        """
        The index thats specifies which surface has the focus when initializing
        the slider.
        """
        self.cutoff: bool = cutoff
        """
        If this is true, the slider wont loop around when the end
        of the surfaces is reached.
        """
        self.max_slides: int = max_slides
        """
        Specifies how many slides can be queued at once.
        """
        self.sliding_duration: float = sliding_duration
        """
        The duration of the sliding animation.
        """
        self.select_animation_duration: float = select_animation_duration
        """
        The duration of the select animation.
        """
        self.span: int = span
        """
        Defines how many images are shown at each side as previews.
        In summary, 1 + 2 * self.span images will be shown.
        """
        self.alphas: list[int] = alphas
        """
        Alpha values that are applied to shown surfaces in the slider.
        """
        self.select_animation_queued: bool = False
        """
        If this is true, a select animation will be started in self.tick()
        """

        if self.alphas is None:

            self.alphas = [255]
            aval = 255

            for _ in range(self.span):
                aval >>= 1
                self.alphas.insert(0, aval)

                self.alphas.append(aval)

        if len(self.alphas) != 1 + 2 * self.span:
            raise ValueError(
                "alphas must contain exactly "
                f"{1 + 2 * self.span} values."
            )

        # Scale multiplier of each visible slot.
        #
        # Example with span = 1:
        #
        # [0.5, 1.0, 0.5]
        #
        if size_decrease_scale == Slider.NO_SIZE_DECREASE:
            self.scale_mults = [1.0] * (1 + 2 * self.span)
        else:
            self.scale_mults = [1.0]
            last_scale = 1.0

            for _ in range(self.span):

                last_scale *= size_decrease_scale

                self.scale_mults.insert(0, last_scale)
                self.scale_mults.append(last_scale)

        self.scale_factors: list[float] = []
        """
        Scale factors, to prevent distorted rendering of the surfaces.
        """
        self.background_color: color_t = background_color
        """
        Background color of the slider.
        """
        self.size_decrease_scale: float = size_decrease_scale
        """
        Defines the size decrease each preview surface receives.
        """
        self.horizontal: bool = horizontal
        """
        If this is false, a vertical slider will be shown
        """
        self.slides: int = 0
        """
        Stores the queued slides.

        -1 -> left
        +1 -> right
        """
        self.extra_surface: pygame.Surface = None
        """
        The additional surface that will be shown while the sliding
        animation is active.
        """
        self.state: id_t = Slider.NOT_SLIDING
        """
        The current state of the Slider.
        """
        self.rendered_surfaces: list[ tuple[pygame.Surface, int, int, bool] ] = []
        """
        The actually rendered surfaces with rendering information.
        (surface, x_position, y_position, rendered (yes or no))
        """
        self.rects: pygame.Rect = []
        """
        Frames containing the shown surfaces
        """
        self.indices: list[int] = []
        """
        indices referencing self.surfaces.
        indices[i] specifies which surface will shown at position i.
        """
        self.original_indices: list[int] = []
        """
        indices without modulo. invalid indices included
        """
        self.fixed_image_positions: list[tuple[int, int]] = None
        """
        The tuples for the calculation of the frames of the surfaces.
        (offset, length)
        """
        self.sliding_clock: Clock = Clock()
        """
        Clock for keeping track of the sliding animation.
        """
        self.select_animation_clock: Clock = Clock()
        """
        Clock for keeping track of the select animation.
        """
        self.flipping_animation_clock: Clock = Clock()
        """
        Clock for keeping track of the flipping animation.
        """
        self.slide_input_delay: float = slide_input_delay
        """
        The delay after which another slide_left/right is executed.
        """
        self.slide_input_delay_clock: Clock = Clock()
        """
        Clock for keeping track of the slide input delay.
        """
        self.top_surface: pygame.Surface = None
        """
        The surface rendered on top.
        """

        self.slide_input_delay_clock.start()

        self.rerender()

    # =============================================================
    # Abstract surface creation methods
    # =============================================================

    @abstractmethod
    def create_surfaces(self) -> None:
        """
        This method should create
        self.surfaces and self.selected_surfaces.

        The length of both lists has to be
        equal to 1 + 2 * self.span
        """
        pass

    @abstractmethod
    def create_back_surfaces(self) -> None:
        """
        This method should create
        self.back_surfaces and self.selected_back_surfaces.

        The length of both lists has to be
        equal to 1 + 2 * self.span
        """
        pass

    # =============================================================
    # Rendering
    # =============================================================
    @override
    def rerender(self) -> None:
        """
        Creates surfaces, then calls self.rerender_images().
        """
        self.create_surfaces() #creates the surfaces for self.surfaces
        self.create_back_surfaces()
        self.rerender_images()

    def rerender_images(self) -> None:
        """
        Rerenders the images, assuming all surfaces
        have been created.
        """

        #resetting variables
        self.rendered_surfaces = []
        self.rects = []
        self.scale_factors = []

        #getting fixed positions
        self.fixed_image_positions = self.get_fixed_surface_positions()

        #creating surfaces
        self.top_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        #indices referencing the surfaces, wrapping around to preserve valid indices
        self.indices =   (
                            [(self.surface_index - i - 1) % len(self.surfaces) for i in range(self.span)]
                            + [self.surface_index]
                            + [(self.surface_index + i + 1) % len(self.surfaces) for i in range(self.span)]
                            )

        #indices without wrapping around
        self.original_indices = (
                                    [self.surface_index - i - 1 for i in range(self.span)]
                                    + [self.surface_index]
                                    + [self.surface_index + i + 1 for i in range(self.span)]
                                )


        #calculating the positions and scales
        for i in range(1 + 2 * self.span):

            pixel_pos: tuple[int, int] = self.fixed_image_positions[i]
            rect: pygame.Rect = None

            if self.horizontal:

                rect = pygame.Rect(
                                    pixel_pos[0], #x position
                                    0,
                                    pixel_pos[1], #width
                                    self.height
                                    )

            else:

                rect = pygame.Rect(
                                    0,
                                    pixel_pos[0], #y position
                                    self.width,
                                    pixel_pos[1] #height
                                )

            #the current surface
            surf: pygame.Surface = None

            if i == self.span:
                surf = self.selected_surfaces[self.indices[i]]
            else:
                surf = self.surfaces[self.indices[i]]

            # Base scale needed to fit this particular image
            # into this particular slot.
            base_scale = (self.get_scale_fraction(surf, rect))
            self.scale_factors.append(base_scale)
            # Apply the slot's visual size multiplier.
            scale = (base_scale * self.scale_mults[i])
            #scaling the surface aptly, whilst also getting a copy of the original surface
            surf = graphics.scale_surface(surf, scale)
            #setting the alpha
            surf.set_alpha(int(self.alphas[i]))
            #getting the surface position
            surf_pos: point_t = (graphics.get_center_with_surface(surf, rect))
            #if the surface should be rendered or not
            rendered: bool = self.is_rendered(self.original_indices[i])

            self.rendered_surfaces.append([
                                            surf,
                                            surf_pos[0], #x_pos
                                            surf_pos[1], #y_pos
                                            rendered
                                        ])
            #adding the rectangle
            self.rects.append(rect)

        self.raise_prerender_flag()

    @override
    def prerender(self) -> None:
        """
        Prerendering
        """

        self.surface.fill(self.background_color)
        self.top_surface.fill(Colors.TRANSPARENT)

        mid_surf = self.rendered_surfaces[self.span]
        for (surf, x, y, rendered) in self.rendered_surfaces:

            if rendered and surf is not mid_surf:
                self.top_surface.blit(surf, (x, y))

        surf, x, y, rendered = self.rendered_surfaces[self.span]
        if rendered:
            self.top_surface.blit(surf, (x, y))

        self.surface.blit(self.top_surface, (0, 0))

    # =============================================================
    # General
    # =============================================================

    def get_selected_index(self) -> int:
        """
        Returns the currently selected index of the surface that
        is the focused at the center.

        This takes into account the remaining amount of slides.
        """
        return self.surface_index - self.slides

    def set_background_color(self, color: color_t):
        """
        Sets the background_color.
        """

        self.background_color = color
        self.raise_prerender_flag()

    def get_focus_index(self) -> int:
        """
        Returns the index of the current focused surface,
        without considering self.slides.
        """
        return self.surface_index

    def slide_left(self) -> None:
        """
        Adds -1 to self.slides (indicating a left slide),
        if sufficient time elapsed since the last call to any slide
        method, and sliding is not cutoff.
        """

        if self.slide_input_delay_clock.elapsed() < self.slide_input_delay:
            return

        if self.cutoff and (self.surface_index - self.slides >= len(self.surfaces) - 1):
            return

        if self.slides > -self.max_slides:
            self.slides -= 1

        self.slide_input_delay_clock.start()

    def slide_right(self) -> None:
        """
        Adds +1 to self.slides (indicating a right slide),
        if sufficient time elapsed since the last call to any slide
        method, and sliding is not cutoff.
        """

        if self.slide_input_delay_clock.elapsed() < self.slide_input_delay:
            return

        if self.cutoff and (self.surface_index - self.slides <= 0):
            return

        if self.slides < self.max_slides:
            self.slides += 1

        self.slide_input_delay_clock.start()

    """
    Just renaming for vertical sliders
    """

    def slide_up(self) -> None:
        """
        Renamed version for a vertical slider.
        """
        self.slide_left()

    def slide_down(self) -> None:
        """
        Renamed version for a vertical slider.
        """
        self.slide_right()


    def reset_slides(self) -> None:
        """
        Sets the slides to 0.
        If the slider is currently sliding,
        it adjust the slide such that when sliding finishes,
        self.slides will be 0.
        """

        if self.state == Slider.SLIDING_LEFT:
            self.slides = -1

        elif self.state == Slider.SLIDING_RIGHT:
            self.slides = 1

        elif self.state == Slider.NOT_SLIDING:
            self.slides = 0

    # =============================================================
    # Rendering / scaling helpers
    # =============================================================

    def get_scale_fraction(self, surf: pygame.Surface, rect: pygame.Rect) -> float:
        """
        Returns the scale to scale a surface by the rect given.
        Does not scale it into the exact rect dimensions, but
        scales up as large as possible still fitting into the rect.
        (Preserving the original aspect ration)
        """

        iw, ih = surf.get_size()

        width_scale = rect.width / iw
        height_scale = rect.height / ih

        return min(width_scale, height_scale)

    def get_absolute_scale(self, surf: pygame.Surface, rect: pygame.Rect, slot_index: int) -> float:
        """
        Returns the absolute scale:

        First the scale to scale the image up as large as possible
        inside the rect is calculated, then the scale for shrinking the image
        depending on the position (indicated by slot index)
        is applied by multiplying it on.
        """

        return (self.get_scale_fraction(
                                        surf,
                                        rect
                                    ) * self.scale_mults[slot_index]
                                )

    def is_rendered(self, original_index: int) -> bool:
        """
        Returns if a surface at the given slot should be rendered or not.
        Is only False if this slider cuts off and the original_index is invalid.
        """

        return not (self.cutoff and (
                                        original_index < 0
                                        or original_index >= len(self.surfaces)
                                    )
                                )

    def select(self) -> bool:
        """
        Returns True if the select call
        executed successfully, False otherwise.
        """
        if not self.state == Slider.SELECT_ANIMATION_PLAYING:
            self.select_animation_queued = True
            return True
        else:
            return False

    def flip_card(self) -> bool:
        """
        Returns True if the flip card call
        executed successfully, False otherwise.
        """
        if not self.flipping_animation_playing():
            self.flipping_animation_queued = True
            return True
        else:
            return False

    def flip_all_cards(self) -> bool:
        """
        Queues a flipping all cards animation.
        Returns True on success, False on failure.
        """

        if not self.flipping_animation_playing():
            self.flipping_all_animation_queued = True
            return True
        else:
            return False

    def sliding_animation_playing(self) -> bool:
        """
        Returns True if the sliding animation is currently playing, else False
        """
        return (self.state == Slider.SLIDING_LEFT or self.state == Slider.SLIDING_RIGHT)

    def select_animation_playing(self) -> bool:
        """
        Returns True if the select animation is currently playing,
        else False
        """
        return (self.state == Slider.SELECT_ANIMATION_PLAYING)

    def flipping_animation_playing(self) -> bool:
        """
        Returns True if the flipping animation is playing, else False.
        """
        return (self.state == Slider.FLIPPING_ANIMATION_PLAYING or self.state == Slider.FLIPPING_ALL_ANIMATION_PLAYING)

    def any_animation_playing(self) -> bool:
        """
        Returns True if any animation is currently playing, else False.
        """
        return (self.select_animation_playing() or self.flipping_animation_playing() or self.sliding_animation_playing())

    # =============================================================
    # Layout
    # =============================================================

    def get_fixed_surface_positions(self) -> list[tuple[int, int]]:
        """
        Calculates the surface positions
        as a list of (startpoint, length) tuples
        from left to right.
        """

        dpixels: int = (self.width if self.horizontal else self.height)
        dspaces: list[tuple[int, int]] = []

        #only one element
        if self.span <= 0:
            dspaces.append((0, dpixels))

        #no size decrease, uniform distribution
        elif self.size_decrease_scale == Slider.NO_SIZE_DECREASE:

            inc = dpixels // (1 + self.span * 2)

            lp = 0

            for i in range(1 + self.span * 2):

                dspaces.append((lp, inc))
                inc += lp

        #distributing
        else:

            frontspace = int(self.size_decrease_scale * dpixels)

            frontstart = (dpixels - frontspace) // 2

            dspaces.append((frontstart, frontspace))

            dpixels = frontstart
            midspace_occupied = frontspace

            for _ in range(self.span-1):#-1 bc we need to assign the remaining space

                space = int(self.size_decrease_scale * dpixels)

                dspaces.insert(0, (dpixels - space, space))
                dspaces.append((dpixels + midspace_occupied, space))

                dpixels -= space
                midspace_occupied += (2 * space)

            dspaces.insert(0, (0, dpixels))
            dspaces.append((dpixels + midspace_occupied, dpixels))

        return dspaces



    # =============================================================
    # LEFT SLIDE
    # =============================================================

    def initialize_slide_left(self) -> None:
        """
        Initializes a slide left.
        """

        visible_count = (1 + 2 * self.span)

        # ---------------------------------------------------------
        # Add the new image entering from the right.
        # ---------------------------------------------------------

        #new index for the extra surface
        surf_index = (self.indices[-1] + 1) % len(self.surfaces)

        self.extra_surface = self.surfaces[surf_index]

        self.indices.append(surf_index)

        self.original_indices.append(self.original_indices[-1] + 1)

        # ---------------------------------------------------------
        # Build absolute start/target scales.
        #
        # old[0] -> disappears
        # old[1] -> slot 0
        # old[2] -> slot 1
        # ...
        # new    -> last slot
        # ---------------------------------------------------------

        self.start_scales = []
        self.target_scales = []

        self.start_alphas = (self.alphas[:] + [0])
        self.target_alphas = ([0] + self.alphas[:])

        self.start_positions = []
        self.target_positions = []

        # ---------------------------------------------------------
        # First image disappearing.
        # ---------------------------------------------------------

        self.start_scales.append(self.scale_factors[0] * self.scale_mults[0])
        self.target_scales.append(self.MIN_SCALE)

        x = self.rendered_surfaces[0][1]
        y = self.rendered_surfaces[0][2]

        cx, cy = graphics.get_center(self.rects[0])

        self.start_positions.append([x, y])

        self.target_positions.append([cx, cy])

        # ---------------------------------------------------------
        # Existing images move one slot to the left.
        # ---------------------------------------------------------

        for old_index in range(1, visible_count):

            new_slot = old_index - 1

            # ALWAYS prerender the original image again.
            #
            # Do not use self.rendered_surfaces[old_index][0]
            # for scale calculations, because that surface is
            # already scaled.

            surf = None
            if old_index == self.span:
                surf = self.selected_surfaces[self.indices[old_index]]
            else:
                surf = self.surfaces[self.indices[old_index]]

            start_scale = (self.scale_factors[old_index] * self.scale_mults[old_index])
            target_base_scale = (self.get_scale_fraction(surf, self.rects[new_slot]))

            target_scale = (target_base_scale * self.scale_mults[new_slot])

            self.start_scales.append(start_scale)
            self.target_scales.append(target_scale)

            x = self.rendered_surfaces[old_index][1]
            y = self.rendered_surfaces[old_index][2]

            target_surf = graphics.scale_surface(surf, target_scale)
            nx, ny = (graphics.get_center_with_surface(target_surf, self.rects[new_slot]))
            self.start_positions.append([x, y])

            self.target_positions.append([nx, ny])

        # ---------------------------------------------------------
        # New image entering from the right.
        # ---------------------------------------------------------

        last_slot = visible_count - 1

        target_base_scale = (self.get_scale_fraction(self.extra_surface, self.rects[last_slot]))

        target_scale = (target_base_scale * self.scale_mults[last_slot])

        self.start_scales.append(self.MIN_SCALE)
        self.target_scales.append(target_scale)

        target_surf = graphics.scale_surface(self.extra_surface, target_scale)

        nx, ny = (graphics.get_center_with_surface(target_surf, self.rects[last_slot]))

        self.start_positions.append([nx, ny])
        self.target_positions.append([nx, ny])

        self.sliding_clock.start()

    def render_slide_left(self) -> None:
        """
        Renders the sliding animation.
        """

        progress = self.sliding_clock.elapsed() / self.sliding_duration
        progress = min(1.0, progress)

        rimages = []

        for i in range(len(self.indices)):

            surf = None
            if i == self.span:
                surf = self.selected_surfaces[self.indices[i]]
            else:
                surf = self.surfaces[self.indices[i]]

            # Interpolate the COMPLETE scale.
            scale = (self.start_scales[i] + (self.target_scales[i] - self.start_scales[i]) * progress)
            alpha = (self.start_alphas[i] + (self.target_alphas[i] - self.start_alphas[i]) * progress)

            x = (self.start_positions[i][0] + (self.target_positions[i][0] - self.start_positions[i][0]) * progress)
            y = (self.start_positions[i][1] + (self.target_positions[i][1] - self.start_positions[i][1]) * progress)

            surf = graphics.scale_surface(surf, max(scale, self.MIN_SCALE))

            surf.set_alpha(int(alpha))

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

        self.raise_prerender_flag()

    def finalize_slide_left(self) -> None:
        """
        Finishes the slide and cleans up.
        """


        # Moving left means moving to the next image.
        self.surface_index = (self.surface_index + 1) % len(self.surfaces)

        self.slides += 1
        self.state = Slider.NOT_SLIDING
        self.push_event(
                            Slider.SlidingAnimationEndedEvent(self.get_selected_index())
                        )

        # Rebuild everything from the actual logical state.
        self.rerender_images()

    # =============================================================
    # RIGHT SLIDE
    # =============================================================

    def initialize_slide_right(self) -> None:
        """
        Initializes the slide right.
        """

        visible_count = (1 + 2 * self.span)

        # ---------------------------------------------------------
        # Add the new image entering from the left.
        # ---------------------------------------------------------

        surf_index = (self.indices[0] - 1) % len(self.surfaces)

        self.extra_surface = self.surfaces[surf_index]

        self.indices.insert(0,surf_index)
        self.original_indices.insert(0, self.original_indices[0] - 1)

        # ---------------------------------------------------------
        # New image -> slot 0
        # old[0]    -> slot 1
        # old[1]    -> slot 2
        # ...
        # old[-1]   -> disappears
        # ---------------------------------------------------------

        self.start_scales = []
        self.target_scales = []

        self.start_alphas = ([0] + self.alphas[:])
        self.target_alphas = (self.alphas[:] + [0])

        self.start_positions = []
        self.target_positions = []

        # ---------------------------------------------------------
        # Extra image entering from the left.
        # ---------------------------------------------------------

        target_base_scale = self.get_scale_fraction(self.extra_surface, self.rects[0])

        target_scale = (target_base_scale * self.scale_mults[0])

        self.start_scales.append(self.MIN_SCALE)
        self.target_scales.append(target_scale)

        target_surf = graphics.scale_surface(self.extra_surface, target_scale)

        nx, ny = (graphics.get_center_with_surface(target_surf, self.rects[0]))

        self.start_positions.append([nx, ny])
        self.target_positions.append([nx, ny])

        # ---------------------------------------------------------
        # Existing images move one slot to the right.
        # ---------------------------------------------------------

        for old_index in range(visible_count - 1):

            old_list_index = old_index + 1
            new_slot = old_index + 1

            # Again, prerender the original image instead of using
            # the already-scaled rendered surface.
            surf = None
            if new_slot == self.span:
                surf = self.selected_surfaces[self.indices[new_slot]]
            else:
                surf = self.surfaces[self.indices[new_slot]]

            start_scale = (self.scale_factors[old_index] * self.scale_mults[old_index])

            target_base_scale = self.get_scale_fraction(surf, self.rects[new_slot])
            target_scale = (target_base_scale * self.scale_mults[new_slot])

            self.start_scales.append(start_scale)
            self.target_scales.append(target_scale)

            x = self.rendered_surfaces[old_index][1]
            y = self.rendered_surfaces[old_index][2]

            target_surf = graphics.scale_surface(surf, target_scale)
            nx, ny = graphics.get_center_with_surface(target_surf, self.rects[new_slot])

            self.start_positions.append([x, y])
            self.target_positions.append([nx, ny])

        # ---------------------------------------------------------
        # Rightmost image disappears.
        # ---------------------------------------------------------

        disappearing_index = visible_count - 1

        start_scale = self.scale_factors[-1] * self.scale_mults[-1]

        self.start_scales.append(start_scale)
        self.target_scales.append(self.MIN_SCALE)

        x = self.rendered_surfaces[disappearing_index][1]
        y = self.rendered_surfaces[disappearing_index][2]

        cx, cy = graphics.get_center(self.rects[-1])

        self.start_positions.append([x, y])
        self.target_positions.append([cx, cy])

        self.sliding_clock.start()

    def render_slide_right(self) -> None:
        """
        Renders the sliding animation.
        """
        progress = self.sliding_clock.elapsed() / self.sliding_duration
        progress = min(1.0, progress)

        rimages = []

        for i in range(len(self.indices)):

            surf = None
            if i == self.span:
                surf = self.selected_surfaces[self.indices[i]]
            else:
                surf = self.surfaces[self.indices[i]]
            # Interpolate the COMPLETE scale.
            scale = (self.start_scales[i] + (self.target_scales[i] - self.start_scales[i]) * progress)
            alpha = (self.start_alphas[i] + (self.target_alphas[i] - self.start_alphas[i]) * progress)

            x = (self.start_positions[i][0] + (self.target_positions[i][0] - self.start_positions[i][0]) * progress)

            y = (self.start_positions[i][1] + ( self.target_positions[i][1] - self.start_positions[i][1]) * progress)

            surf = graphics.scale_surface(surf, max(scale, self.MIN_SCALE))
            surf.set_alpha(int(alpha))

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

        self.raise_prerender_flag()

    def finalize_slide_right(self) -> None:
        """
        Ends and cleans up the sliding animation.
        """
        # Moving right means moving to the previous image.
        self.surface_index = (self.surface_index - 1) % len(self.surfaces)

        self.slides -= 1

        self.state = Slider.NOT_SLIDING

        self.push_event(
                            Slider.SlidingAnimationEndedEvent(self.get_selected_index())
                        )

        # Rebuild everything from the actual logical state.
        self.rerender_images()

    # =============================================================
    # Tick
    # =============================================================
    def render_select_animation(self) -> None:
        """
        Renders the select animation.
        """

        percentage = self.select_animation_clock.elapsed() / self.select_animation_duration

        scale_increase = 0.5

        halfsize = (int(self.selected_surface_startsize[0] * scale_increase) // 2, int(self.selected_surface_startsize[1] * scale_increase) // 2)

        if percentage >= 1.0:
            self.state = Slider.NOT_SLIDING
            self.push_event(
                                Slider.SelectAnimationEndedEvent(self.get_selected_index())
                            )
            self.rerender_images()
        else:

            npos = None
            nscale = None

            if percentage <= 0.5:

                nscale = (int(self.selected_surface_startsize[0] * (1.0 -  scale_increase * 2 * percentage)),
                            int(self.selected_surface_startsize[1] * (1.0 -  scale_increase * 2 *  percentage))
                            )
                npos = (int(self.selected_surface_startpos[0] + halfsize[0] * 2 * percentage),
                            int(self.selected_surface_startpos[1] + halfsize[1] * 2* percentage)
                            )

            else:

                nscale = (int(self.selected_surface_startsize[0] * ((1.0 -  scale_increase) + scale_increase * (percentage - 0.5)*2)),
                            int(self.selected_surface_startsize[1] * ((1.0 -  scale_increase) + scale_increase * (percentage - 0.5)*2))
                            )
                npos = (int(self.selected_surface_startpos[0] + halfsize[0] * (1.0 - 2 * (percentage - 0.5))),
                            int(self.selected_surface_startpos[1] + halfsize[1] * (1.0 - 2* (percentage - 0.5)))
                            )


            new_surf = pygame.transform.smoothscale(self.selected_surface_copy, nscale)


            self.rendered_surfaces[self.span][0] = new_surf
            self.rendered_surfaces[self.span][1], self.rendered_surfaces[self.span][2] = npos

            self.raise_prerender_flag()

    def render_flipping_animation(self) -> None:
        """
        Renders the flipping animation.
        """

        percentage = self.flipping_animation_clock.elapsed() / self.flip_duration

        if percentage >= 1.0:
            self.state = Slider.NOT_SLIDING
            self.push_event(
                                Slider.FlippingAnimationEndedEvent(self.get_selected_index(), False)
                            )
            #changing images
            save = self.surfaces[self.surface_index]
            save2 = self.selected_surfaces[self.surface_index]
            self.surfaces[self.surface_index] = self.back_surfaces[self.surface_index]
            self.selected_surfaces[self.surface_index] = self.selected_back_surfaces[self.surface_index]
            self.back_surfaces[self.surface_index] = save
            self.selected_back_surfaces[self.surface_index] = save2
            self.rerender_images()

        else:

            if percentage <= 0.5:

                fullp = 2 * percentage

                new_width = int((1.0 - fullp) * self.selected_surface_startsize[0])

                new_surf = pygame.transform.smoothscale(self.selected_surface_copy, (new_width, self.selected_surface_startsize[1]))
                new_pos = (self.selected_surface_startpos[0] + (self.selected_surface_startsize[0] - new_width) // 2, self.selected_surface_startpos[1])

                self.rendered_surfaces[self.span] = [new_surf, new_pos[0], new_pos[1], self.rendered_surfaces[self.span][3]]

            else:

                fullp = 1.0 - (2* percentage - 1.0)

                new_width = int((1.0 - fullp) * self.selected_surface_startsize[0])

                new_surf = pygame.transform.smoothscale(self.back_surface_rendered, (new_width, self.selected_surface_startsize[1]))
                new_pos = (self.selected_surface_startpos[0] + (self.selected_surface_startsize[0] - new_width) // 2, self.selected_surface_startpos[1])

                self.rendered_surfaces[self.span] = [new_surf, new_pos[0], new_pos[1], self.rendered_surfaces[self.span][3]]

            self.raise_prerender_flag()

    def render_flipping_all_animation(self) -> None:
        """
        Renders the flipping all animation.
        """

        percentage = self.flipping_animation_clock.elapsed() / self.flip_duration

        if percentage >= 1.0:
            self.state = Slider.NOT_SLIDING
            self.push_event(
                                Slider.FlippingAnimationEndedEvent(self.get_selected_index(), True)
                            )
            #changing images
            save = self.surfaces
            save2 = self.selected_surfaces
            self.surfaces = self.back_surfaces
            self.selected_surfaces = self.selected_back_surfaces
            self.back_surfaces = save
            self.selected_back_surfaces = save2
            self.rerender_images()

        else:

            if percentage <= 0.5:

                fullp = 2 * percentage

                #new_img = pygame.transform.smoothscale(self.selected_image_copy, (new_width, self.selected_surface_startsize[1]))
                #new_pos = (self.selected_image_startpos[0] + (self.selected_surface_startsize[0] - new_width) // 2, self.selected_image_startpos[1])

                new_widths = [int((1.0 - fullp) * img_size[0]) for img_size in self.saved_sizes]

                new_imgs = [pygame.transform.smoothscale(self.saved_surface_copies[i], (new_widths[i], self.saved_sizes[i][1])) for i in range(len(self.saved_surface_copies))]
                new_pos = [(self.saved_positions[i][0] + (self.saved_sizes[i][0] - new_widths[i]) // 2, self.saved_positions[i][1]) for i in range(len(self.saved_surface_copies))]

                for i in range(len(self.saved_surface_copies)):
                    self.rendered_surfaces[i] = [new_imgs[i], new_pos[i][0], new_pos[i][1], self.rendered_surfaces[i][3]]
            else:

                fullp = 1.0 - (2* percentage - 1.0)

                new_widths = [int((1.0 - fullp) * img_size[0]) for img_size in self.saved_sizes]

                new_imgs = [pygame.transform.smoothscale(self.back_surfaces_rendered[i], (new_widths[i], self.saved_sizes[i][1])) for i in range(len(self.saved_surface_copies))]
                new_pos = [(self.saved_positions[i][0] + (self.saved_sizes[i][0] - new_widths[i]) // 2, self.saved_positions[i][1]) for i in range(len(self.saved_surface_copies))]

                for i in range(len(self.saved_surface_copies)):
                    self.rendered_surfaces[i] = [new_imgs[i], new_pos[i][0], new_pos[i][1], self.rendered_surfaces[i][3]]

            self.raise_prerender_flag()

    @override
    def tick(self) -> Frame:
        """
        Slider tick method.
        """
        if self.state == Slider.SLIDING_LEFT:

            if self.sliding_clock.elapsed() >= self.sliding_duration:
                self.finalize_slide_left()
            else:
                self.render_slide_left()

        elif self.state == Slider.SLIDING_RIGHT:
            if self.sliding_clock.elapsed() >= self.sliding_duration:
                self.finalize_slide_right()

            else:
                self.render_slide_right()

        elif self.state == Slider.SELECT_ANIMATION_PLAYING:
            self.render_select_animation()

        elif self.state == Slider.FLIPPING_ANIMATION_PLAYING:
            self.render_flipping_animation()

        elif self.state == Slider.FLIPPING_ALL_ANIMATION_PLAYING:
            self.render_flipping_all_animation()

        elif self.state == Slider.NOT_SLIDING:

            if self.slides != 0:
                if self.slides > 0:

                    self.state = Slider.SLIDING_RIGHT
                    self.initialize_slide_right()

                else:

                    self.state = Slider.SLIDING_LEFT
                    self.initialize_slide_left()

            elif self.slides == 0 and self.flipping_all_animation_queued:

                self.flipping_all_animation_queued = False
                self.state = Slider.FLIPPING_ALL_ANIMATION_PLAYING

                self.saved_sizes = [x[0].get_size() for x in self.rendered_surfaces]
                self.saved_positions = [(x[1], x[2]) for x in self.rendered_surfaces]
                self.saved_surface_copies = [x[0].copy() for x in self.rendered_surfaces]
                self.back_surfaces_rendered = [self.back_surfaces[index].copy() for index in self.indices]
                self.flipping_animation_clock.start()

            elif self.slides == 0 and self.flipping_animation_queued:

                self.flipping_animation_queued = False
                self.state = Slider.FLIPPING_ANIMATION_PLAYING
                self.selected_surface_startsize = self.rendered_surfaces[self.span][0].get_size()
                self.selected_surface_startpos = (self.rendered_surfaces[self.span][1], self.rendered_surfaces[self.span][2])
                self.selected_surface_copy = self.rendered_surfaces[self.span][0].copy()
                self.back_surface_rendered = self.back_surfaces[self.surface_index].copy()
                self.flipping_animation_clock.start()

            elif self.slides == 0 and self.select_animation_queued:

                self.select_animation_queued = False
                self.state = Slider.SELECT_ANIMATION_PLAYING
                self.selected_surface_startsize = self.rendered_surfaces[self.span][0].get_size()
                self.selected_surface_startpos = (self.rendered_surfaces[self.span][1], self.rendered_surfaces[self.span][2])
                self.selected_surface_copy = self.rendered_surfaces[self.span][0].copy()
                self.select_animation_clock.start()

        if (self.state != Slider.NOT_SLIDING):
            self.raise_prerender_flag()

        if self.prerender_flag_raised():
            self.prerender()
            self.reset_prerender_flag()

        return self
