"""
Base class for sliders
"""
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
    R_ID
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

    class EventTypes:

        SELECT_ANIMATION_ENDED = R_ID()
        FLIPPING_ANIMATION_ENDED = R_ID()
        SLIDING_ANIMATION_ENDED = R_ID()


    SLIDING_LEFT = R_ID()
    SLIDING_RIGHT = R_ID()
    NOT_SLIDING = R_ID()
    SELECT_ANIMATION_PLAYING = R_ID()
    FLIPPING_ANIMATION_PLAYING = R_ID()
    FLIPPING_ALL_ANIMATION_PLAYING = R_ID()

    MIN_SCALE = 0.001

    def __init__(
        self,
        frame_dim,
        sliding_duration=500,  # ms
        select_animation_duration=800,#ms
        alphas=None,
        span=1,
        background_color=Colors.TRANSPARENT,
        size_decrease_scale=0.5,
        horizontal=True,
        start_index=0,
        cutoff=False,
        max_slides=2,
        back_surfaces=None,
        flip_duration=400,#ms
        slide_input_delay=250#ms
    ):

        super().__init__(FrameEnums.SLIDER_WIDGET, None, frame_dim, focus_group=None)

        self.surfaces = []
        self.back_surfaces = []
        self.flip_duration = flip_duration
        self.flipping_animation_queued = False
        self.flipping_all_animation_queued = False
        self.surface_index = start_index
        self.cutoff = cutoff
        self.max_slides = max_slides

        self.sliding_duration = sliding_duration
        self.select_animation_duration = select_animation_duration
        self.span = span

        self.alphas = alphas
        self.select_animation_queued = False

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

        # Base scale factor for the currently rendered images to prevent distorted rendering
        self.scale_factors = []

        self.background_color = background_color
        self.size_decrease_scale = size_decrease_scale
        self.horizontal = horizontal

        # -1 = left
        # +1 = right
        self.slides = 0
        self.extra_surface = None
        self.state = Slider.NOT_SLIDING

        #extra variables

        #surfaces that are already rendered
        self.rendered_surfaces = []
        #frames containing the shown surfaces
        self.rects = []
        #factors for the surfaces, so that they dont get distorted
        self.scale_factors = []
        #indices referencing self.surfaces
        self.indices = []
        #indices without modulo. invalid indices included
        self.original_indices = []

        self.fixed_image_positions = self.get_fixed_image_positions()

        self.sliding_clock = Clock()
        self.select_animation_clock = Clock()
        self.flipping_animation_clock = Clock()

        self.slide_input_delay_clock = Clock()
        self.slide_input_delay = slide_input_delay
        self.slide_input_delay_clock.start()

        self.rerender_images()

    # =============================================================
    # General
    # =============================================================

    def get_selected_index(self):
        return self.surface_index - self.slides

    def set_background_color(self, color):

        self.background_color = color
        self.prerender()

    def get_focus_index(self):
        return self.surface_index

    def get_focus_surface(self):
        return self.surfaces[self.surface_index]

    def slide_left(self):

        if self.slide_input_delay_clock.elapsed() < self.slide_input_delay:
            return

        if self.cutoff and (self.surface_index - self.slides >= len(self.surfaces) - 1):
            return

        if self.slides > -self.max_slides:
            self.slides -= 1

        self.slide_input_delay_clock.start()

    def slide_right(self):

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
    def slide_up(self):
        self.slide_left()

    def slide_down(self):
        self.slide_right()


    def reset_slides(self):

        if self.state == Slider.SLIDING_LEFT:
            self.slides = -1

        elif self.state == Slider.SLIDING_RIGHT:
            self.slides = 1

        elif self.state == Slider.NOT_SLIDING:
            self.slides = 0

    # =============================================================
    # Rendering / scaling helpers
    # =============================================================

    def get_scale_fraction(self, img, rect):

        iw, ih = img.get_size()

        width_scale = rect.width / iw
        height_scale = rect.height / ih

        return min(width_scale, height_scale)

    def get_absolute_scale(self, img, rect, slot_index):

        return (self.get_scale_fraction(
                                        img,
                                        rect
                                    ) * self.scale_mults[slot_index]
                                )

    def is_rendered(self, original_index):

        return not (self.cutoff and (
                                        original_index < 0
                                        or original_index >= len(self.surfaces)
                                    )
                                )

    # =============================================================
    # Initial rendering
    # =============================================================

    def play_select_animation(self):
        if not self.state == Slider.SELECT_ANIMATION_PLAYING:
            self.select_animation_queued = True
            return True
        else:
            return False

    def flip_card(self):
        if not self.flipping_animation_playing():
            self.flipping_animation_queued = True
            return True
        else:
            return False

    @abstractmethod
    def create_surfaces(self):
        pass

    @abstractmethod
    def create_back_surfaces(self):
        pass

    def rerender_images(self):

        self.top_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.bottom_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.create_surfaces() #creates the surfaces for self.surfaces
        self.create_back_surfaces()
        self.rendered_surfaces = []
        self.rects = []
        self.scale_factors = []

        #indices referencing the surfaces
        self.indices =   ([(self.surface_index - i - 1) % len(self.surfaces) for i in range(self.span)]
                    + [self.surface_index]
                    + [(self.surface_index + i + 1) % len(self.surfaces) for i in range(self.span)]
                    )

        self.original_indices = ([self.surface_index - i - 1 for i in range(self.span)]
                                + [self.surface_index]
                                + [self.surface_index + i + 1 for i in range(self.span)])



        for i in range(1 + 2 * self.span):

            pixel_pos = self.fixed_image_positions[i]
            rect = None

            if self.horizontal:
                rect = pygame.Rect(
                                    pixel_pos[0],
                                    0,
                                    pixel_pos[1],
                                    self.height
                                    )

            else:

                rect = pygame.Rect(
                                    0,
                                    pixel_pos[0],
                                    self.width,
                                    pixel_pos[1]
                                )

            surf = self.surfaces[self.indices[i]]

            # Base scale needed to fit this particular image
            # into this particular slot.
            base_scale = (self.get_scale_fraction(surf, rect))

            self.scale_factors.append(base_scale)

            # Apply the slot's visual size multiplier.
            scale = (base_scale * self.scale_mults[i])

            surf = graphics.scale_surface(surf, scale)

            surf.set_alpha(int(self.alphas[i]))

            surf_pos = (graphics.get_center_with_surface(surf, rect))

            rendered = self.is_rendered(self.original_indices[i])

            self.rendered_surfaces.append([
                                            surf,
                                            surf_pos[0],
                                            surf_pos[1],
                                            rendered
                                        ])

            self.rects.append(rect)

        self.prerender()

    # =============================================================
    # Layout
    # =============================================================

    def get_fixed_image_positions(self):

        dpixels = (self.width if self.horizontal else self.height)

        dspaces = []

        if self.span <= 0:
            dspaces.append((0, dpixels))

        elif self.size_decrease_scale == Slider.NO_SIZE_DECREASE:

            inc = dpixels // (1 + self.span * 2)

            lp = 0

            for i in range(1 + self.span * 2):

                dspaces.append((lp, nic))
                inc += lp

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
    # Rendering
    # =============================================================

    def prerender(self):

        self.bottom_surface.fill(self.background_color)
        self.top_surface.fill(Colors.TRANSPARENT)

        mid_surf = self.rendered_surfaces[self.span]
        for (surf, x, y, rendered) in self.rendered_surfaces:

            if rendered and surf is not mid_surf:
                self.top_surface.blit(surf, (x, y))

        surf, x, y, rendered = self.rendered_surfaces[self.span]
        if rendered:
            self.top_surface.blit(surf, (x, y))

    # =============================================================
    # LEFT SLIDE
    # =============================================================

    def initialize_slide_left(self):

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

    def render_slide_left(self):

        progress = self.sliding_clock.elapsed() / self.sliding_duration
        progress = min(1.0, progress)

        rimages = []

        for i in range(len(self.indices)):

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

        self.prerender()

    def finalize_slide_left(self):

        # Moving left means moving to the next image.
        self.surface_index = (self.surface_index + 1) % len(self.surfaces)

        self.slides += 1
        self.state = Slider.NOT_SLIDING
        self.push_event(Event(Slider.EventTypes.SLIDING_ANIMATION_ENDED, None))

        # Rebuild everything from the actual logical state.
        self.rerender_images()

    # =============================================================
    # RIGHT SLIDE
    # =============================================================
    def rerender(self):
        self.rerender_images()

    def initialize_slide_right(self):

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
            surf = self.surfaces[self.indices[old_list_index]]

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

    def render_slide_right(self):

        progress = self.sliding_clock.elapsed() / self.sliding_duration
        progress = min(1.0, progress)

        rimages = []

        for i in range(len(self.indices)):

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

        self.prerender()

    def finalize_slide_right(self):

        # Moving right means moving to the previous image.
        self.surface_index = (self.surface_index - 1) % len(self.surfaces)

        self.slides -= 1

        self.state = Slider.NOT_SLIDING

        self.push_event(Event(Slider.EventTypes.SLIDING_ANIMATION_ENDED, None))

        # Rebuild everything from the actual logical state.
        self.rerender_images()

    # =============================================================
    # Tick
    # =============================================================
    def render_select_animation(self):

        percentage = self.select_animation_clock.elapsed() / self.select_animation_duration

        scale_increase = 0.5

        halfsize = (int(self.selected_surface_startsize[0] * scale_increase) // 2, int(self.selected_surface_startsize[1] * scale_increase) // 2)

        if percentage >= 1.0:
            self.state = Slider.NOT_SLIDING
            self.push_event(Event(Slider.EventTypes.SELECT_ANIMATION_ENDED, None))
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

            self.prerender()

    def render_flipping_animation(self):

        percentage = self.flipping_animation_clock.elapsed() / self.flip_duration

        if percentage >= 1.0:
            self.state = Slider.NOT_SLIDING
            self.push_event(Event(Slider.EventTypes.FLIPPING_ANIMATION_ENDED, None))
            #changing images
            save = self.surfaces[self.surface_index]
            self.surfaces[self.surface_index] = self.back_surfaces[self.surface_index]
            self.back_surfaces[self.surface_index] = save
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

            self.prerender()

    def render_flipping_all_animation(self):

        percentage = self.flipping_animation_clock.elapsed() / self.flip_duration

        if percentage >= 1.0:
            self.state = Slider.NOT_SLIDING
            self.push_event(Event(Slider.EventTypes.FLIPPING_ANIMATION_ENDED, None))
            #changing images
            save = self.surfaces
            self.surfaces = self.back_surfaces
            self.back_surfaces = save
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

            self.prerender()





    def flip_all_cards(self):

        if not self.flipping_animation_playing():
            self.flipping_all_animation_queued = True
            return True
        else:
            return False

    def select_animation_playing(self):
        return self.state == Slider.SELECT_ANIMATION_PLAYING

    def flipping_animation_playing(self):
        return (self.state == Slider.FLIPPING_ANIMATION_PLAYING or self.state == Slider.FLIPPING_ALL_ANIMATION_PLAYING)

    def any_animation_playing(self):
        return (self.select_animation_playing() or self.flipping_animation_playing())

    def render(self, screen):

        self.prerender()
        screen.blit(self.bottom_surface, (self.x, self.y))
        screen.blit(self.top_surface, (self.x, self.y))


    def tick(self):

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
