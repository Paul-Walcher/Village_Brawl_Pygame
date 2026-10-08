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
from enum import Enum, auto
import graphics
from clock import Clock
from modules import Modules
import constants


class ImageSlider:

    class Event:

        SELECT_ANIMATION_ENDED = 0

        def __init__(self, type, data):
            self.type = type
            self.data = data


    SLIDING_LEFT = 0
    SLIDING_RIGHT = 1
    NOT_SLIDING = 2
    SELECT_ANIMATION_PLAYING = 3

    MIN_SCALE = 0.001

    def __init__(
        self,
        images,
        width,
        height,
        sliding_duration=500,  # ms
        select_animation_duration=800,#ms
        images_alphas=None,
        images_span=1,
        background_color=Colors.TRANSPARENT,
        size_distribution=0.6,
        size_decrease_scale=0.5,
        horizontal=True,
        start_index=0,
        cutoff=False,
        max_slides=10
    ):

        if len(images) < (1 + 2 * images_span):
            raise RuntimeError(
                "You need more images for this image span."
            )

        self.images = images
        self.image_index = start_index
        self.cutoff = cutoff
        self.max_slides = max_slides

        self.width = width
        self.height = height

        self.sliding_duration = sliding_duration
        self.select_animation_duration = select_animation_duration
        self.images_span = images_span

        self.images_alphas = images_alphas
        self.select_animation_queued = False

        self.event_queue = []

        if self.images_alphas is None:

            self.images_alphas = [255]

            aval = 255

            for _ in range(self.images_span):

                aval >>= 1

                self.images_alphas.insert(
                    0,
                    aval
                )

                self.images_alphas.append(
                    aval
                )

        if len(self.images_alphas) != 1 + 2 * self.images_span:
            raise ValueError(
                "images_alphas must contain exactly "
                f"{1 + 2 * self.images_span} values."
            )

        # Scale multiplier of each visible slot.
        #
        # Example with images_span = 1:
        #
        # [0.5, 1.0, 0.5]
        #
        self.scale_mults = [1.0]

        last_scale = 1.0

        for _ in range(self.images_span):

            last_scale *= size_decrease_scale

            self.scale_mults.insert(
                0,
                last_scale
            )

            self.scale_mults.append(
                last_scale
            )

        # Base scale factor for the currently rendered images.
        self.scale_factors = []

        self.background_color = background_color
        self.size_distribution = size_distribution
        self.size_decrease_scale = size_decrease_scale
        self.horizontal = horizontal

        # -1 = left
        # +1 = right
        self.slides = 0

        self.rendered_images = []
        self.extra_image = None

        self.top_surface = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA
        )

        self.bottom_surface = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA
        )

        self.state = ImageSlider.NOT_SLIDING

        self.fixed_image_positions = (
            self.get_fixed_image_positions()
        )

        self.rerender_images()

        self.sliding_clock = Clock()
        self.select_animation_clock = Clock()

    # =============================================================
    # General
    # =============================================================

    def get_selected_index(self):
        return self.image_index - self.slides

    def set_background_color(self, color):

        self.background_color = color
        self.render()

    def get_focus_index(self):
        return self.image_index

    def get_focus_image(self):
        return self.images[self.image_index]

    def slide_left(self):

        if self.cutoff and (
            self.image_index - self.slides
            >= len(self.images) - 1
        ):
            return

        if self.slides > -self.max_slides and not self.select_animation_queued:
            self.slides -= 1

    def slide_right(self):

        if self.cutoff and (
            self.image_index - self.slides <= 0
        ):
            return

        if self.slides < self.max_slides and not self.select_animation_queued:
            self.slides += 1

    def reset_slides(self):

        if self.state == ImageSlider.SLIDING_LEFT:
            self.slides = -1

        elif self.state == ImageSlider.SLIDING_RIGHT:
            self.slides = 1

        elif self.state == ImageSlider.NOT_SLIDING:
            self.slides = 0

    def get_surfaces(self):
        return [
            self.bottom_surface,
            self.top_surface
        ]

    # =============================================================
    # Rendering / scaling helpers
    # =============================================================

    def get_scale_fraction(self, img, rect):

        iw, ih = img.get_size()

        width_scale = rect.width / iw
        height_scale = rect.height / ih

        return min(width_scale, height_scale)

    def get_absolute_scale(self, img, rect, slot_index):

        return (
            self.get_scale_fraction(
                img,
                rect
            )
            * self.scale_mults[slot_index]
        )

    def is_rendered(self, original_index):

        return not (
            self.cutoff
            and (
                original_index < 0
                or original_index >= len(self.images)
            )
        )

    # =============================================================
    # Initial rendering
    # =============================================================

    def play_select_animation(self):
        if not self.state == ImageSlider.SELECT_ANIMATION_PLAYING:
            self.select_animation_queued = True
            return True
        else:
            return False

    def rerender_images(self):


        self.rendered_images = []
        self.rects = []
        self.scale_factors = []

        indices = (
            [
                (
                    self.image_index - i - 1
                ) % len(self.images)
                for i in range(self.images_span)
            ]
            + [self.image_index]
            + [
                (
                    self.image_index + i + 1
                ) % len(self.images)
                for i in range(self.images_span)
            ]
        )

        self.indices = indices

        self.original_indices = (
            [
                self.image_index - i - 1
                for i in range(self.images_span)
            ]
            + [self.image_index]
            + [
                self.image_index + i + 1
                for i in range(self.images_span)
            ]
        )

        for i in range(
            1 + 2 * self.images_span
        ):

            pixel_pos = self.fixed_image_positions[i]

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

            img = graphics.render_image(
                self.images[self.indices[i]]
            )

            # Base scale needed to fit this particular image
            # into this particular slot.
            base_scale = (
                self.get_scale_fraction(
                    img,
                    rect
                )
            )

            self.scale_factors.append(
                base_scale
            )

            # Apply the slot's visual size multiplier.
            scale = (
                base_scale
                * self.scale_mults[i]
            )

            img = graphics.scale_image(
                img,
                scale
            )

            img.set_alpha(
                int(self.images_alphas[i])
            )

            img_pos = (
                graphics.get_center_with_surface(
                    img,
                    rect
                )
            )

            rendered = self.is_rendered(
                self.original_indices[i]
            )

            self.rendered_images.append(
                [
                    img,
                    img_pos[0],
                    img_pos[1],
                    rendered
                ]
            )

            self.rects.append(rect)

        self.render()

    # =============================================================
    # Layout
    # =============================================================

    def get_fixed_image_positions(self):

        dpixels = (
            self.width
            if self.horizontal
            else self.height
        )

        dspaces = []

        if self.images_span <= 0:

            dspaces.append(
                dpixels
            )

        else:

            frontspace = int(
                self.size_distribution * dpixels
            )

            frontstart = (
                dpixels - frontspace
            ) // 2

            dspaces.append(
                (
                    frontstart,
                    frontspace
                )
            )

            dpixels = frontstart
            midspace_occupied = frontspace

            for _ in range(
                self.images_span - 1
            ):

                space = int(
                    self.size_distribution * dpixels
                )

                dspaces.insert(
                    0,
                    (
                        dpixels - space,
                        space
                    )
                )

                dspaces.append(
                    (
                        dpixels + midspace_occupied,
                        space
                    )
                )

                dpixels -= space

                midspace_occupied += (
                    2 * space
                )

            dspaces.insert(
                0,
                (
                    0,
                    dpixels
                )
            )

            dspaces.append(
                (
                    dpixels + midspace_occupied,
                    dpixels
                )
            )

        return dspaces

    # =============================================================
    # Rendering
    # =============================================================

    def render(self):

        self.bottom_surface.fill(
            self.background_color
        )

        self.top_surface.fill(
            Colors.TRANSPARENT
        )

        mid_img = self.rendered_images[self.images_span]

        for (
            img,
            x,
            y,
            rendered
        ) in self.rendered_images:

            if rendered and img is not mid_img:

                self.top_surface.blit(
                    img,
                    (x, y)
                )

        img, x, y, rendered = self.rendered_images[self.images_span]

        if rendered:

            self.top_surface.blit(img, (x, y))

    # =============================================================
    # LEFT SLIDE
    # =============================================================

    def initialize_slide_left(self):

        visible_count = (
            1 + 2 * self.images_span
        )

        # ---------------------------------------------------------
        # Add the new image entering from the right.
        # ---------------------------------------------------------

        img_index = (
            self.indices[-1] + 1
        ) % len(self.images)

        self.extra_image = graphics.render_image(
            self.images[img_index]
        )

        self.indices.append(
            img_index
        )

        self.original_indices.append(
            self.original_indices[-1] + 1
        )

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

        self.start_alphas = (
            self.images_alphas[:]
            + [0]
        )

        self.target_alphas = (
            [0]
            + self.images_alphas[:]
        )

        self.start_positions = []
        self.target_positions = []

        # ---------------------------------------------------------
        # First image disappearing.
        # ---------------------------------------------------------

        self.start_scales.append(
            self.scale_factors[0]
            * self.scale_mults[0]
        )

        self.target_scales.append(
            self.MIN_SCALE
        )

        x = self.rendered_images[0][1]
        y = self.rendered_images[0][2]

        cx, cy = graphics.get_center(
            self.rects[0]
        )

        self.start_positions.append(
            [x, y]
        )

        self.target_positions.append(
            [cx, cy]
        )

        # ---------------------------------------------------------
        # Existing images move one slot to the left.
        # ---------------------------------------------------------

        for old_index in range(
            1,
            visible_count
        ):

            new_slot = old_index - 1

            # ALWAYS render the original image again.
            #
            # Do not use self.rendered_images[old_index][0]
            # for scale calculations, because that surface is
            # already scaled.
            img = graphics.render_image(
                self.images[self.indices[old_index]]
            )

            start_scale = (
                self.scale_factors[old_index]
                * self.scale_mults[old_index]
            )

            target_base_scale = (
                self.get_scale_fraction(
                    img,
                    self.rects[new_slot]
                )
            )

            target_scale = (
                target_base_scale
                * self.scale_mults[new_slot]
            )

            self.start_scales.append(
                start_scale
            )

            self.target_scales.append(
                target_scale
            )

            x = self.rendered_images[old_index][1]
            y = self.rendered_images[old_index][2]

            target_img = graphics.scale_image(
                img,
                target_scale
            )

            nx, ny = (
                graphics.get_center_with_surface(
                    target_img,
                    self.rects[new_slot]
                )
            )

            self.start_positions.append(
                [x, y]
            )

            self.target_positions.append(
                [nx, ny]
            )

        # ---------------------------------------------------------
        # New image entering from the right.
        # ---------------------------------------------------------

        last_slot = visible_count - 1

        target_base_scale = (
            self.get_scale_fraction(
                self.extra_image,
                self.rects[last_slot]
            )
        )

        target_scale = (
            target_base_scale
            * self.scale_mults[last_slot]
        )

        self.start_scales.append(
            self.MIN_SCALE
        )

        self.target_scales.append(
            target_scale
        )

        target_img = graphics.scale_image(
            self.extra_image,
            target_scale
        )

        nx, ny = (
            graphics.get_center_with_surface(
                target_img,
                self.rects[last_slot]
            )
        )

        self.start_positions.append(
            [nx, ny]
        )

        self.target_positions.append(
            [nx, ny]
        )

        self.sliding_clock.start()

    def render_slide_left(self):

        progress = (
            self.sliding_clock.elapsed()
            / self.sliding_duration
        )

        progress = min(
            1.0,
            progress
        )

        rimages = []

        for i in range(
            len(self.indices)
        ):

            img = graphics.render_image(
                self.images[self.indices[i]]
            )

            # Interpolate the COMPLETE scale.
            scale = (
                self.start_scales[i]
                + (
                    self.target_scales[i]
                    - self.start_scales[i]
                ) * progress
            )

            alpha = (
                self.start_alphas[i]
                + (
                    self.target_alphas[i]
                    - self.start_alphas[i]
                ) * progress
            )

            x = (
                self.start_positions[i][0]
                + (
                    self.target_positions[i][0]
                    - self.start_positions[i][0]
                ) * progress
            )

            y = (
                self.start_positions[i][1]
                + (
                    self.target_positions[i][1]
                    - self.start_positions[i][1]
                ) * progress
            )

            img = graphics.scale_image(
                img,
                max(
                    scale,
                    self.MIN_SCALE
                )
            )

            img.set_alpha(
                int(alpha)
            )

            rendered = self.is_rendered(
                self.original_indices[i]
            )

            rimages.append(
                [
                    img,
                    int(x),
                    int(y),
                    rendered
                ]
            )

        self.rendered_images = rimages

        self.render()

    def finalize_slide_left(self):

        # Moving left means moving to the next image.
        self.image_index = (
            self.image_index + 1
        ) % len(self.images)

        self.slides += 1

        self.state = (
            ImageSlider.NOT_SLIDING
        )

        # Rebuild everything from the actual logical state.
        self.rerender_images()

    # =============================================================
    # RIGHT SLIDE
    # =============================================================

    def initialize_slide_right(self):

        visible_count = (
            1 + 2 * self.images_span
        )

        # ---------------------------------------------------------
        # Add the new image entering from the left.
        # ---------------------------------------------------------

        img_index = (
            self.indices[0] - 1
        ) % len(self.images)

        self.extra_image = graphics.render_image(
            self.images[img_index]
        )

        self.indices.insert(
            0,
            img_index
        )

        self.original_indices.insert(
            0,
            self.original_indices[0] - 1
        )

        # ---------------------------------------------------------
        # New image -> slot 0
        # old[0]    -> slot 1
        # old[1]    -> slot 2
        # ...
        # old[-1]   -> disappears
        # ---------------------------------------------------------

        self.start_scales = []
        self.target_scales = []

        self.start_alphas = (
            [0]
            + self.images_alphas[:]
        )

        self.target_alphas = (
            self.images_alphas[:]
            + [0]
        )

        self.start_positions = []
        self.target_positions = []

        # ---------------------------------------------------------
        # Extra image entering from the left.
        # ---------------------------------------------------------

        target_base_scale = (
            self.get_scale_fraction(
                self.extra_image,
                self.rects[0]
            )
        )

        target_scale = (
            target_base_scale
            * self.scale_mults[0]
        )

        self.start_scales.append(
            self.MIN_SCALE
        )

        self.target_scales.append(
            target_scale
        )

        target_img = graphics.scale_image(
            self.extra_image,
            target_scale
        )

        nx, ny = (
            graphics.get_center_with_surface(
                target_img,
                self.rects[0]
            )
        )

        self.start_positions.append(
            [nx, ny]
        )

        self.target_positions.append(
            [nx, ny]
        )

        # ---------------------------------------------------------
        # Existing images move one slot to the right.
        # ---------------------------------------------------------

        for old_index in range(
            visible_count - 1
        ):

            old_list_index = old_index + 1
            new_slot = old_index + 1

            # Again, render the original image instead of using
            # the already-scaled rendered surface.
            img = graphics.render_image(
                self.images[
                    self.indices[old_list_index]
                ]
            )

            start_scale = (
                self.scale_factors[old_index]
                * self.scale_mults[old_index]
            )

            target_base_scale = (
                self.get_scale_fraction(
                    img,
                    self.rects[new_slot]
                )
            )

            target_scale = (
                target_base_scale
                * self.scale_mults[new_slot]
            )

            self.start_scales.append(
                start_scale
            )

            self.target_scales.append(
                target_scale
            )

            x = self.rendered_images[
                old_index
            ][1]

            y = self.rendered_images[
                old_index
            ][2]

            target_img = graphics.scale_image(
                img,
                target_scale
            )

            nx, ny = (
                graphics.get_center_with_surface(
                    target_img,
                    self.rects[new_slot]
                )
            )

            self.start_positions.append(
                [x, y]
            )

            self.target_positions.append(
                [nx, ny]
            )

        # ---------------------------------------------------------
        # Rightmost image disappears.
        # ---------------------------------------------------------

        disappearing_index = (
            visible_count - 1
        )

        start_scale = (
            self.scale_factors[-1]
            * self.scale_mults[-1]
        )

        self.start_scales.append(
            start_scale
        )

        self.target_scales.append(
            self.MIN_SCALE
        )

        x = self.rendered_images[
            disappearing_index
        ][1]

        y = self.rendered_images[
            disappearing_index
        ][2]

        cx, cy = graphics.get_center(
            self.rects[-1]
        )

        self.start_positions.append(
            [x, y]
        )

        self.target_positions.append(
            [cx, cy]
        )

        self.sliding_clock.start()

    def render_slide_right(self):

        progress = (
            self.sliding_clock.elapsed()
            / self.sliding_duration
        )

        progress = min(
            1.0,
            progress
        )

        rimages = []

        for i in range(
            len(self.indices)
        ):

            img = graphics.render_image(
                self.images[self.indices[i]]
            )

            # Interpolate the COMPLETE scale.
            scale = (
                self.start_scales[i]
                + (
                    self.target_scales[i]
                    - self.start_scales[i]
                ) * progress
            )

            alpha = (
                self.start_alphas[i]
                + (
                    self.target_alphas[i]
                    - self.start_alphas[i]
                ) * progress
            )

            x = (
                self.start_positions[i][0]
                + (
                    self.target_positions[i][0]
                    - self.start_positions[i][0]
                ) * progress
            )

            y = (
                self.start_positions[i][1]
                + (
                    self.target_positions[i][1]
                    - self.start_positions[i][1]
                ) * progress
            )

            img = graphics.scale_image(
                img,
                max(
                    scale,
                    self.MIN_SCALE
                )
            )

            img.set_alpha(
                int(alpha)
            )

            rendered = self.is_rendered(
                self.original_indices[i]
            )

            rimages.append(
                [
                    img,
                    int(x),
                    int(y),
                    rendered
                ]
            )

        self.rendered_images = rimages

        self.render()

    def finalize_slide_right(self):

        # Moving right means moving to the previous image.
        self.image_index = (
            self.image_index - 1
        ) % len(self.images)

        self.slides -= 1

        self.state = (
            ImageSlider.NOT_SLIDING
        )

        # Rebuild everything from the actual logical state.
        self.rerender_images()

    # =============================================================
    # Tick
    # =============================================================
    def render_select_animation(self):

        percentage = self.select_animation_clock.elapsed() / self.select_animation_duration

        scale_increase = 0.5

        halfsize = (int(self.selected_image_startsize[0] * scale_increase) // 2, int(self.selected_image_startsize[1] * scale_increase) // 2)

        if percentage >= 1.0:
            self.state = ImageSlider.NOT_SLIDING
            self.event_queue.append(ImageSlider.Event(ImageSlider.Event.SELECT_ANIMATION_ENDED, None))
            self.rerender_images()
        else:

            npos = None
            nscale = None

            if percentage <= 0.5:

                nscale = (int(self.selected_image_startsize[0] * (1.0 -  scale_increase * 2 * percentage)),
                            int(self.selected_image_startsize[1] * (1.0 -  scale_increase * 2 *  percentage))
                            )
                npos = (int(self.selected_image_startpos[0] + halfsize[0] * 2 * percentage),
                            int(self.selected_image_startpos[1] + halfsize[1] * 2* percentage)
                            )

            else:

                nscale = (int(self.selected_image_startsize[0] * ((1.0 -  scale_increase) + scale_increase * (percentage - 0.5)*2)),
                            int(self.selected_image_startsize[1] * ((1.0 -  scale_increase) + scale_increase * (percentage - 0.5)*2))
                            )
                npos = (int(self.selected_image_startpos[0] + halfsize[0] * (1.0 - 2 * (percentage - 0.5))),
                            int(self.selected_image_startpos[1] + halfsize[1] * (1.0 - 2* (percentage - 0.5)))
                            )


            new_img = pygame.transform.smoothscale(self.selected_image_copy, nscale)


            self.rendered_images[self.images_span][0] = new_img
            self.rendered_images[self.images_span][1], self.rendered_images[self.images_span][2] = npos


            self.render()

    def select_animation_playing(self):

        return self.state == ImageSlider.SELECT_ANIMATION_PLAYING

    def poll_events(self):

        back = self.event_queue
        self.event_queue = []
        return back

    def tick(self):

        if self.state == ImageSlider.SLIDING_LEFT:

            if (
                self.sliding_clock.elapsed()
                >= self.sliding_duration
            ):

                self.finalize_slide_left()

            else:

                self.render_slide_left()

        elif self.state == ImageSlider.SLIDING_RIGHT:

            if (
                self.sliding_clock.elapsed()
                >= self.sliding_duration
            ):

                self.finalize_slide_right()

            else:

                self.render_slide_right()

        elif self.state == ImageSlider.SELECT_ANIMATION_PLAYING:

            self.render_select_animation()

        elif self.state == ImageSlider.NOT_SLIDING:

            if self.slides != 0:

                if self.slides > 0:

                    self.state = (
                        ImageSlider.SLIDING_RIGHT
                    )

                    self.initialize_slide_right()

                else:

                    self.state = (
                        ImageSlider.SLIDING_LEFT
                    )

                    self.initialize_slide_left()

            elif self.slides == 0 and self.select_animation_queued:

                self.select_animation_queued = False
                self.state = ImageSlider.SELECT_ANIMATION_PLAYING
                self.selected_image_startsize = self.rendered_images[self.images_span][0].get_size()
                self.selected_image_startpos = (self.rendered_images[self.images_span][1], self.rendered_images[self.images_span][2])
                self.selected_image_copy = self.rendered_images[self.images_span][0].copy()
                self.select_animation_clock.start()
