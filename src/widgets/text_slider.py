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


class TextSlider:

    SLIDING_LEFT = 0
    SLIDING_RIGHT = 1
    NOT_SLIDING = 2

    # pygame.transform.scale() should not receive a zero scale.
    MIN_SCALE = 0.001

    class Event:

        SELECT_ANIMATION_ENDED = 0
        FLIPPING_ANIMATION_ENDED = 1
        SLIDING_ANIMATION_ENDED = 2

        def __init__(self, type, data):
            self.type = type
            self.data = data

    def __init__(
        self,
        text,
        width,
        height,
        font=Fonts.MINECRAFT,
        sliding_duration=500,  # ms
        images_alphas=None,
        images_span=1,
        background_color=Colors.TRANSPARENT,
        size_distribution=0.6,
        size_decrease_scale=0.5,
        horizontal=True,
        start_index=0,
        cutoff=False,
        max_slides=10,
        font_startsize=30,
        line_margin_percentage=0.05,
        text_color=Colors.BLACK
    ):

        if len(text) < (1 + 2 * images_span):
            raise RuntimeError(
                "You need more images for this image span."
            )

        self.text = text
        self.font = font
        self.font_startsize = font_startsize
        self.text_color = text_color

        self.image_index = start_index
        self.line_margin_percentage = line_margin_percentage
        self.line_margin = int(self.line_margin_percentage * height)
        self.cutoff = cutoff
        self.max_slides = max_slides

        self.width = width
        self.height = height
        self.sliding_duration = sliding_duration
        self.images_span = images_span
        self.event_queue = []

        # ---------------------------------------------------------
        # Alpha values
        # ---------------------------------------------------------

        self.images_alphas = images_alphas

        if self.images_alphas is None:

            self.images_alphas = [255]
            aval = 255

            for _ in range(self.images_span):
                aval >>= 1
                self.images_alphas.insert(0, aval)
                self.images_alphas.append(aval)

        if len(self.images_alphas) != 1 + 2 * self.images_span:
            raise ValueError(
                "images_alphas must contain exactly "
                f"{1 + 2 * self.images_span} values."
            )

        # ---------------------------------------------------------
        # Slot scale multipliers
        # ---------------------------------------------------------

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

        self.scale_factors = []

        self.background_color = background_color
        self.size_distribution = size_distribution
        self.size_decrease_scale = size_decrease_scale
        self.horizontal = horizontal

        # -1 = slide left
        # +1 = slide right
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

        self.state = TextSlider.NOT_SLIDING

        self.fixed_image_positions = (
            self.get_fixed_image_positions()
        )

        self.alphas = self.images_alphas[:]

        self.rerender_images()

        self.sliding_clock = Clock()

    # =============================================================
    # General
    # =============================================================

    def poll_events(self):

        back = self.event_queue
        self.event_queue = []
        return back

    def get_selected_index(self):
        return self.image_index - self.slides

    def set_background_color(self, color):
        self.background_color = color
        self.render()

    def get_focus_index(self):
        return self.image_index

    def get_focus_image(self):
        return self.text[self.image_index]

    def slide_left(self):

        if self.cutoff and (
            self.image_index - self.slides
            >= len(self.text) - 1
        ):
            return

        if self.slides > -self.max_slides:
            self.slides -= 1

    def slide_right(self):

        if self.cutoff and (
            self.image_index - self.slides <= 0
        ):
            return

        if self.slides < self.max_slides:
            self.slides += 1

    def reset_slides(self):

        if self.state == TextSlider.SLIDING_LEFT:
            self.slides = -1

        elif self.state == TextSlider.SLIDING_RIGHT:
            self.slides = 1

        elif self.state == TextSlider.NOT_SLIDING:
            self.slides = 0

    def get_surfaces(self):
        return [
            self.bottom_surface,
            self.top_surface
        ]

    # =============================================================
    # Text rendering
    # =============================================================

    def render_text_as_surface(self, text):

        # text is a list of lines

        imgs = []

        for line in text:

            imgs.append(
                graphics.render_text(
                    self.font,
                    self.font_startsize,
                    line,
                    color=self.text_color
                )
            )

        rwidth = max(
            img.get_width()
            for img in imgs
        )

        rheight = (
            sum(
                img.get_height()
                for img in imgs
            )
            + (len(imgs) - 1) * self.line_margin
        )

        img = pygame.Surface(
            (rwidth, rheight),
            pygame.SRCALPHA
        )

        img.fill(
            Colors.TRANSPARENT
        )

        cy = 0

        for surf in imgs:

            img.blit(
                surf,
                (0, cy)
            )

            cy += (
                surf.get_height()
                + self.line_margin
            )

        return img

    # =============================================================
    # Scaling
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

    # =============================================================
    # Initial rendering
    # =============================================================

    def rerender_images(self):

        self.rendered_images = []
        self.rects = []
        self.scale_factors = []

        self.alphas = (
            self.images_alphas[:]
        )

        self.indices = (
            [
                (
                    self.image_index
                    - i
                    - 1
                ) % len(self.text)
                for i in range(self.images_span)
            ]
            + [
                self.image_index
            ]
            + [
                (
                    self.image_index
                    + i
                    + 1
                ) % len(self.text)
                for i in range(self.images_span)
            ]
        )

        self.original_indices = (
            [
                self.image_index - i - 1
                for i in range(self.images_span)
            ]
            + [
                self.image_index
            ]
            + [
                self.image_index + i + 1
                for i in range(self.images_span)
            ]
        )

        for i in range(
            1 + 2 * self.images_span
        ):

            pixel_pos = (
                self.fixed_image_positions[i]
            )

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

            img = self.render_text_as_surface(
                self.text[self.indices[i]]
            )

            base_scale = (
                self.get_scale_fraction(
                    img,
                    rect
                )
            )

            self.scale_factors.append(
                base_scale
            )

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

            rendered = not (
                self.cutoff
                and (
                    self.original_indices[i] < 0
                    or self.original_indices[i]
                    >= len(self.text)
                )
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
                self.size_distribution
                * dpixels
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
                    self.size_distribution
                    * dpixels
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

        for (
            img,
            x,
            y,
            rendered
        ) in self.rendered_images:

            if rendered:

                self.top_surface.blit(
                    img,
                    (x, y)
                )

    # =============================================================
    # LEFT SLIDE
    # =============================================================

    def initialize_slide_left(self):

        visible_count = (
            1 + 2 * self.images_span
        )

        # ---------------------------------------------------------
        # New image entering from the right
        # ---------------------------------------------------------

        img_index = (
            self.indices[-1] + 1
        ) % len(self.text)

        self.extra_image = (
            self.render_text_as_surface(
                self.text[img_index]
            )
        )

        self.indices.append(
            img_index
        )

        self.original_indices.append(
            self.indices[-2] + 1
        )

        # ---------------------------------------------------------
        # Absolute scale at start and end.
        #
        # There are visible_count + 1 images:
        #
        # old[0]   -> disappears
        # old[1]   -> slot 0
        # old[2]   -> slot 1
        # ...
        # extra    -> last slot
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

        self.target_positions = []
        self.start_positions = []

        # ---------------------------------------------------------
        # Old first image disappearing
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
        # Existing images moving left
        # ---------------------------------------------------------

        for old_i in range(
            1,
            visible_count
        ):

            new_slot = old_i - 1

            img = self.render_text_as_surface(
                self.text[self.indices[old_i]]
            )

            # IMPORTANT:
            # Calculate the destination scale using the
            # ORIGINAL unscaled image.
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

            start_scale = (
                self.scale_factors[old_i]
                * self.scale_mults[old_i]
            )

            self.start_scales.append(
                start_scale
            )

            self.target_scales.append(
                target_scale
            )

            x = self.rendered_images[old_i][1]
            y = self.rendered_images[old_i][2]

            start_img = graphics.scale_image(
                img,
                start_scale
            )

            target_img = graphics.scale_image(
                img,
                target_scale
            )

            # start_img isn't strictly necessary for position,
            # because rendered_images already contains its
            # current position, but keeping the calculation
            # conceptually explicit is useful.
            _ = start_img

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
        # Extra image entering from the right
        # ---------------------------------------------------------

        last_slot = (
            visible_count - 1
        )

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

        # Zero-size image is naturally centered at the same point.
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

            img = self.render_text_as_surface(
                self.text[self.indices[i]]
            )

            scale = (
                self.start_scales[i]
                + (
                    self.target_scales[i]
                    - self.start_scales[i]
                )
                * progress
            )

            alpha = (
                self.start_alphas[i]
                + (
                    self.target_alphas[i]
                    - self.start_alphas[i]
                )
                * progress
            )

            x = (
                self.start_positions[i][0]
                + (
                    self.target_positions[i][0]
                    - self.start_positions[i][0]
                )
                * progress
            )

            y = (
                self.start_positions[i][1]
                + (
                    self.target_positions[i][1]
                    - self.start_positions[i][1]
                )
                * progress
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

            rendered = not (
                self.cutoff
                and (
                    self.original_indices[i] < 0
                    or self.original_indices[i]
                    >= len(self.text)
                )
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

        # The second image becomes the new first image,
        # so just update image_index and reconstruct the
        # ordinary state from scratch.
        self.image_index = (self.image_index + 1) % len(self.text)

        self.slides += 1

        self.state = (
            TextSlider.NOT_SLIDING
        )

        self.event_queue.append(TextSlider.Event(TextSlider.Event.SLIDING_ANIMATION_ENDED, None))

        self.rerender_images()

    # =============================================================
    # RIGHT SLIDE
    # =============================================================

    def initialize_slide_right(self):

        visible_count = (
            1 + 2 * self.images_span
        )

        # ---------------------------------------------------------
        # New image entering from the left
        # ---------------------------------------------------------

        img_index = (
            self.indices[0] - 1
        ) % len(self.text)

        self.extra_image = (
            self.render_text_as_surface(
                self.text[img_index]
            )
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
        # New ordering:
        #
        # extra    -> slot 0
        # old[0]   -> slot 1
        # old[1]   -> slot 2
        # ...
        # old[-1]  -> disappears
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
        # Extra image entering from the left
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
        # Existing images moving right
        # ---------------------------------------------------------

        for old_i in range(
            visible_count - 1
        ):

            new_slot = old_i + 1

            img = self.render_text_as_surface(
                self.text[self.indices[old_i + 1]]
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

            # Old image's current absolute scale.
            start_scale = (
                self.scale_factors[old_i]
                * self.scale_mults[old_i]
            )

            self.start_scales.append(
                start_scale
            )

            self.target_scales.append(
                target_scale
            )

            x = self.rendered_images[old_i][1]
            y = self.rendered_images[old_i][2]

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
        # Rightmost old image disappearing
        # ---------------------------------------------------------

        disappearing_old_i = (
            visible_count - 1
        )

        x = self.rendered_images[
            disappearing_old_i
        ][1]

        y = self.rendered_images[
            disappearing_old_i
        ][2]

        self.start_scales.append(
            self.scale_factors[-1]
            * self.scale_mults[-1]
        )

        self.target_scales.append(
            self.MIN_SCALE
        )

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

            img = self.render_text_as_surface(
                self.text[self.indices[i]]
            )

            scale = (
                self.start_scales[i]
                + (
                    self.target_scales[i]
                    - self.start_scales[i]
                )
                * progress
            )

            alpha = (
                self.start_alphas[i]
                + (
                    self.target_alphas[i]
                    - self.start_alphas[i]
                )
                * progress
            )

            x = (
                self.start_positions[i][0]
                + (
                    self.target_positions[i][0]
                    - self.start_positions[i][0]
                )
                * progress
            )

            y = (
                self.start_positions[i][1]
                + (
                    self.target_positions[i][1]
                    - self.start_positions[i][1]
                )
                * progress
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

            rendered = not (
                self.cutoff
                and (
                    self.original_indices[i] < 0
                    or self.original_indices[i]
                    >= len(self.text)
                )
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

        self.image_index = ((self.image_index - 1) % len(self.text))

        self.slides -= 1

        self.state = (
            TextSlider.NOT_SLIDING
        )

        self.event_queue.append(TextSlider.Event(TextSlider.Event.SLIDING_ANIMATION_ENDED, None))

        self.rerender_images()

    # =============================================================
    # Update
    # =============================================================

    def tick(self):

        if self.state == TextSlider.SLIDING_LEFT:

            if (
                self.sliding_clock.elapsed()
                >= self.sliding_duration
            ):

                self.finalize_slide_left()

            else:

                self.render_slide_left()

        elif self.state == TextSlider.SLIDING_RIGHT:

            if (
                self.sliding_clock.elapsed()
                >= self.sliding_duration
            ):

                self.finalize_slide_right()

            else:

                self.render_slide_right()

        if self.state == TextSlider.NOT_SLIDING:

            if self.slides != 0:

                if self.slides > 0:

                    self.state = (
                        TextSlider.SLIDING_RIGHT
                    )

                    self.initialize_slide_right()

                else:

                    self.state = (
                        TextSlider.SLIDING_LEFT
                    )

                    self.initialize_slide_left()
