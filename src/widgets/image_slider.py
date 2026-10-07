import os
import pygame
import threading

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, FrameDataID
import graphics
from clock import Clock
from modules import Modules
import constants

class ImageSlider:

    SLIDING_LEFT = 0
    SLIDING_RIGHT = 1
    NOT_SLIDING = 2

    def __init__(self,  images, width, height,
                        sliding_duration=500,#ms
                        images_alphas=None,
                        images_span=1, #1 preview image on each side
                        background_color=Colors.TRANSPARENT,
                        size_distribution=0.6,#means the image in focus will occupy the middle 60 percent of space,
                        size_decrease_scale=0.5,#means every image to the left or right will decrease by this size
                        horizontal=True,#if it is sliding horizontally or vertically
                        start_index=0,
                        cutoff=False, #if cutoff == False, it loops around
                        max_slides=10
                ):

        if len(images) < (1 + 2*images_span):
            raise RuntimeError("You need more images for this image span.")

        self.images = images
        self.image_index = start_index
        self.cutoff = cutoff
        self.max_slides = max_slides
        self.width, self.height = width, height
        self.sliding_duration = sliding_duration
        self.images_span = images_span
        self.images_alphas = images_alphas

        if self.images_alphas is None:
            self.images_alphas = [255]
            aval = 255
            for i in range(self.images_span):
                aval >>= 1
                self.images_alphas.insert(0, aval)
                self.images_alphas.append(aval)

        self.scale_factors = []
        self.scale_mults = [1.0]
        last_scale = 1.0

        for i in range(self.images_span):
            last_scale *= size_decrease_scale
            self.scale_mults.insert(0, last_scale)
            self.scale_mults.append(last_scale)

        self.background_color = background_color
        self.size_distribution = size_distribution
        self.size_decrease_scale = size_decrease_scale
        self.horizontal = horizontal
        self.slides = 0#-x, x slides to the left, +x x slides to the right

        self.rendered_images = [] #lists like: [image, x, y]
        self.extra_image = None

        self.top_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.bottom_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.state = ImageSlider.NOT_SLIDING

        self.fixed_image_positions = self.get_fixed_image_positions()
        self.rerender_images()

        self.sliding_clock = Clock()


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
        if self.cutoff and (self.image_index - self.slides) >= (len(self.images)-1):
            return
        if self.slides > - self.max_slides:
            self.slides -= 1

    def slide_right(self):
        if self.cutoff and (self.image_index - self.slides) <= 0:
            return
        if self.slides < self.max_slides:
            self.slides += 1

    def reset_slides(self):

        if self.state == ImageSlider.SLIDING_LEFT:
            self.slides = -1
        elif self.state == ImageSlider.SLIDING_RIGHT:
            self.slides = 1
        elif self.state == ImageSlider.NOT_SLIDING:
            self.slides = 0

    def get_surfaces(self):
        return [self.bottom_surface, self.top_surface]

    def rerender_images(self):

        self.rendered_images = []
        self.rendered_texts = []
        self.rects = []

        indices = [(self.image_index - i - 1)%len(self.images) for i in range(self.images_span)] +\
                    [self.image_index] + [(self.image_index + i + 1)%len(self.images) for i in range(self.images_span)]

        self.original_indices = [(self.image_index - i - 1) for i in range(self.images_span)] +\
                                [self.image_index] + [(self.image_index + i + 1) for i in range(self.images_span)]

        self.indices = indices

        for i in range(1 + 2*self.images_span):

            pixel_pos = self.fixed_image_positions[i]
            rect = (pygame.Rect(pixel_pos[0], 0, pixel_pos[1], self.height) if self.horizontal else pygame.Rect(0, pixel_pos[0], self.width, pixel_pos[1]))

            img = graphics.render_image(self.images[indices[i]])
            #rescaling
            iw, ih = img.get_size()
            scale_factor = 1
            if iw > ih:
                scale_factor = (pixel_pos[1] / iw if self.horizontal else self.width / iw)
            else:
                scale_factor = (pixel_pos[1] / ih if not self.horizontal else self.height / ih)

            self.scale_factors.append(scale_factor)
            scale_factor *= self.scale_mults[i]

            img = pygame.transform.scale(img, (int(img.get_width()*scale_factor), int(img.get_height() * scale_factor)))
            img.set_alpha(self.images_alphas[i])

            img_pos = graphics.get_center_with_surface(img, rect)

            rendered = (False if self.cutoff and (self.original_indices[i] < 0 or self.original_indices[i] >= len(self.images)) else True)

            self.rendered_images.append([img, img_pos[0], img_pos[1], rendered])


            self.rects.append(rect)

        self.render()




    def get_fixed_image_positions(self):

        #dividing the spaces
        dpixels = (self.width if self.horizontal else self.height)
        #each space is a tuple (startpixel, length)
        dspaces = []

        if self.images_span <= 0:
            dspaces.append(dpixels)
        else:

            frontspace = int(self.size_distribution * dpixels)
            frontstart = (dpixels - frontspace)//2
            dspaces.append((frontstart, frontspace))

            dpixels = frontstart
            midspace_occupied = frontspace

            for i in range(self.images_span - 1):

                space = int(self.size_distribution * dpixels)

                dspaces.insert(0, (dpixels - space, space))
                dspaces.append((dpixels + midspace_occupied, space))

                dpixels -= space
                midspace_occupied += 2*space

            dspaces.insert(0, (0, dpixels))
            dspaces.append((dpixels + midspace_occupied, dpixels))

        return dspaces


    def render(self):

        self.bottom_surface.fill(self.background_color)
        self.top_surface.fill(Colors.TRANSPARENT)

        for img, x, y, rendered in self.rendered_images:

            if rendered:
                self.top_surface.blit(img, (x, y))


    def get_scale_fraction(self, img, rect):
        #rescaling
        iw, ih = img.get_size()
        scale_factor = 1
        if iw > ih:
            scale_factor = (rect.width / iw if self.horizontal else self.width / iw)
        else:
            scale_factor = (rect.height / ih if not self.horizontal else self.height / ih)

        return scale_factor

    def initialize_slide_left(self):

        img_index = (self.indices[-1]+1) % (len(self.images))
        self.original_indices.append(self.indices[-1]+1)
        self.extra_image = graphics.render_image(self.images[img_index])

        pixel_pos = self.fixed_image_positions[-1]

        iw, ih = self.extra_image.get_size()
        scale_factor = 1
        if iw > ih:
            scale_factor = (pixel_pos[1] / iw if self.horizontal else self.width / iw)
        else:
            scale_factor = (pixel_pos[1] / ih if not self.horizontal else self.height / ih)

        self.extra_scale_factor = scale_factor
        self.scale_factors.append(scale_factor)
        self.extra_target_scale_factor = scale_factor * self.scale_mults[-1]
        self.extra_alpha = 0
        self.extra_target_alpha = self.images_alphas[-1]

        self.indices.append(img_index)
        #setting targets
        self.target_scale_mults_diff = [self.scale_mults[0]] + [self.scale_mults[i+1] - self.scale_mults[i] for i in range(2*self.images_span)] + [-self.scale_mults[-1]]
        self.target_scale_mults = [0] + self.scale_mults[:]
        self.target_alphas_diff = [self.images_alphas[0]] + [self.images_alphas[i+1] - self.images_alphas[i] for i in range(2*self.images_span)] + [-self.images_alphas[-1]]
        self.target_alphas = [0] + self.images_alphas[:]

        self.target_positions = []
        self.target_position_diffs = []

        self.scale_factors = [self.scale_factors[0]]

        cx, cy = graphics.get_center(self.rects[0])
        self.target_positions.append([cx, cy])
        self.target_position_diffs.append([self.rendered_images[0][1] - cx, self.rendered_images[0][2] - cy])

        for i in range(1, 1 + 2*self.images_span):

            img, x, y = self.rendered_images[i][0], self.rendered_images[i][1], self.rendered_images[i][2]

            rimg = graphics.render_image(self.images[self.indices[i]])

            w, h = rimg.get_size()

            self.scale_factors.append(self.get_scale_fraction(rimg, self.rects[i-1]))
            rimg = graphics.scale_image(rimg, self.scale_factors[i] * self.target_scale_mults[i])

            nx, ny = graphics.get_center_with_surface(rimg, self.rects[i-1])
            self.target_positions.append([nx, ny])
            self.target_position_diffs.append([x - nx, y - ny])

        sf = self.get_scale_fraction(self.extra_image, self.rects[-1])
        self.scale_factors.append(sf)
        extra_scaled = graphics.scale_image(self.extra_image, sf * self.target_scale_mults[-1])
        nx, ny = graphics.get_center_with_surface(extra_scaled, self.rects[-1])
        self.target_positions.append([nx, ny])
        dscale = graphics.scale_image(self.extra_image, 0.001)
        ew, eh = dscale.get_size()
        sx, sy = graphics.get_center_with_surface(dscale, self.rects[-1])
        self.target_position_diffs.append([sx - nx, sy - ny])



        #getting target positions

        self.sliding_clock.start()

    def render_slide_left(self):

        slide_percentage = self.sliding_clock.elapsed() / self.sliding_duration

        slide_percentage = min(1.0, slide_percentage)

        rimages = []

        for i in range(2 + 2*self.images_span):

            img = graphics.render_image(self.images[self.indices[i]])

            new_mult = self.target_scale_mults[i] + (1.0 - slide_percentage) * self.target_scale_mults_diff[i]
            new_alpha = self.target_alphas[i] + (1.0 - slide_percentage) * self.target_alphas_diff[i]
            new_x = self.target_positions[i][0] + int((1.0 - slide_percentage) * self.target_position_diffs[i][0])
            new_y = self.target_positions[i][1] + int((1.0 - slide_percentage) * self.target_position_diffs[i][1])

            img = graphics.scale_image(img, self.scale_factors[i]*new_mult)
            img.set_alpha(new_alpha)

            rendered = (False if self.cutoff and (self.original_indices[i] < 0 or self.original_indices[i] >= len(self.images)) else True)

            rimages.append([img, new_x, new_y, rendered])


        self.rendered_images = rimages
        self.render()

    def finalize_slide_left(self):

        rimages = []
        self.scale_factors = self.scale_factors[1:]
        self.indices = self.indices[1:]
        self.scale_mults = self.target_scale_mults[1:]
        self.target_positions = self.target_positions[1:]
        self.alphas = self.target_alphas[1:]
        self.original_indices = self.original_indices[1:]

        for i in range(1 + 2*self.images_span):

            img = graphics.render_image(self.images[self.indices[i]])
            img = graphics.scale_image(img, self.scale_factors[i] * self.scale_mults[i])
            img.set_alpha(self.alphas[i])

            rendered = (False if self.cutoff and (self.original_indices[i] < 0 or self.original_indices[i] >= len(self.images)) else True)

            rimages.append([img, self.target_positions[i][0], self.target_positions[i][1], rendered])

        self.image_index = self.indices[self.images_span]

        self.state = ImageSlider.NOT_SLIDING
        self.slides += 1

        self.rendered_images = rimages
        self.render()

    def initialize_slide_right(self):

        img_index = (self.indices[0]-1) % (len(self.images))
        self.original_indices.insert(0, self.indices[0]-1)
        self.extra_image = graphics.render_image(self.images[img_index])

        self.indices.insert(0, img_index)
        #setting targets
        self.target_scale_mults_diff = [-self.scale_mults[0]] + [self.scale_mults[i] - self.scale_mults[i + 1] for i in range(2*self.images_span)] + [self.scale_mults[-1]]
        self.target_scale_mults = self.scale_mults[:] + [0]
        self.target_alphas_diff = [-self.images_alphas[0]] + [self.images_alphas[i] - self.images_alphas[i + 1] for i in range(2*self.images_span)] + [self.images_alphas[-1]]
        self.target_alphas = self.images_alphas[:] + [0]

        self.target_positions = []
        self.target_position_diffs = []

        scale_save = self.scale_factors[-1]
        self.scale_factors = []

        sf = self.get_scale_fraction(self.extra_image, self.rects[0])
        self.scale_factors.append(sf)
        extra_scaled = graphics.scale_image(self.extra_image, sf * self.target_scale_mults[0])
        nx, ny = graphics.get_center_with_surface(extra_scaled, self.rects[0])
        self.target_positions.append([nx, ny])
        dscale = graphics.scale_image(self.extra_image, 0.001)
        ew, eh = dscale.get_size()
        sx, sy = graphics.get_center_with_surface(dscale, self.rects[0])
        self.target_position_diffs.append([sx - nx, sy - ny])

        for i in range(2*self.images_span):

            img, x, y = self.rendered_images[i][0], self.rendered_images[i][1], self.rendered_images[i][2]

            rimg = graphics.render_image(self.images[self.indices[i+1]])

            w, h = rimg.get_size()

            self.scale_factors.append(self.get_scale_fraction(rimg, self.rects[i+1]))
            rimg = graphics.scale_image(rimg, self.scale_factors[-1] * self.target_scale_mults[i+1])

            nx, ny = graphics.get_center_with_surface(rimg, self.rects[i+1])
            self.target_positions.append([nx, ny])
            self.target_position_diffs.append([x - nx, y - ny])

        cx, cy = graphics.get_center(self.rects[-1])
        self.target_positions.append([cx, cy])
        self.target_position_diffs.append([self.rendered_images[-1][1] - cx, self.rendered_images[-1][2] - cy])
        self.scale_factors.append(scale_save)
        #getting target positions

        self.sliding_clock.start()

    def render_slide_right(self):

        slide_percentage = self.sliding_clock.elapsed() / self.sliding_duration

        slide_percentage = min(1.0, slide_percentage)

        rimages = []

        for i in range(2 + 2*self.images_span):

            img = graphics.render_image(self.images[self.indices[i]])

            new_mult = self.target_scale_mults[i] + (1.0 - slide_percentage) * self.target_scale_mults_diff[i]
            new_alpha = self.target_alphas[i] + (1.0 - slide_percentage) * self.target_alphas_diff[i]
            new_x = self.target_positions[i][0] + int((1.0 - slide_percentage) * self.target_position_diffs[i][0])
            new_y = self.target_positions[i][1] + int((1.0 - slide_percentage) * self.target_position_diffs[i][1])

            img = graphics.scale_image(img, self.scale_factors[i]*new_mult)
            img.set_alpha(new_alpha)

            rendered = (False if self.cutoff and (self.original_indices[i] < 0 or self.original_indices[i] >= len(self.images)) else True)

            rimages.append([img, new_x, new_y, rendered])


        self.rendered_images = rimages
        self.render()

    def finalize_slide_right(self):

        rimages = []
        self.scale_factors = self.scale_factors[:-1]
        self.indices = self.indices[:-1]
        self.scale_mults = self.target_scale_mults[:-1]
        self.target_positions = self.target_positions[:-1]
        self.alphas = self.target_alphas[:-1]
        self.original_indices = self.original_indices[:-1]

        for i in range(1 + 2*self.images_span):

            img = graphics.render_image(self.images[self.indices[i]])
            img = graphics.scale_image(img, self.scale_factors[i] * self.scale_mults[i])
            img.set_alpha(self.alphas[i])

            rendered = (False if self.cutoff and (self.original_indices[i] < 0 or self.original_indices[i] >= len(self.images)) else True)

            rimages.append([img, self.target_positions[i][0], self.target_positions[i][1], rendered])

        self.image_index = self.indices[self.images_span]

        self.state = ImageSlider.NOT_SLIDING
        self.slides -= 1

        self.rendered_images = rimages
        self.render()

    def tick(self):

        if self.state == ImageSlider.SLIDING_LEFT:
            if self.sliding_clock.elapsed() >= self.sliding_duration:
                self.finalize_slide_left()
            else:
                self.render_slide_left()
        elif self.state == ImageSlider.SLIDING_RIGHT:
            if self.sliding_clock.elapsed() >= self.sliding_duration:
                self.finalize_slide_right()
            else:
                self.render_slide_right()

        if self.state == ImageSlider.NOT_SLIDING:
            if self.slides != 0:
                if self.slides > 0:
                    self.state = ImageSlider.SLIDING_RIGHT
                    self.initialize_slide_right()
                else:
                    self.state = ImageSlider.SLIDING_LEFT
                    self.initialize_slide_left()
