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
                        horizontal=True#if it is sliding horizontally or vertically
                ):

        if len(images) < (1 + 2*images_span):
            raise RuntimeError("You need more images for this image span.")

        self.images = images
        self.image_index = 0
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

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.state = ImageSlider.NOT_SLIDING

        self.fixed_image_positions = self.get_fixed_image_positions()
        self.rerender_images()

        self.sliding_clock = Clock()


    def slide_left(self):
        self.slides -= 1

    def slide_right(self):
        self.slides += 1

    def reset_slides(self):

        if self.state == ImageSlider.SLIDING_LEFT:
            self.slides = -1
        elif self.state == ImageSlider.SLIDING_RIGHT:
            self.slides = 1
        elif self.state == ImageSlider.NOT_SLIDING:
            self.slides = 0

    def get_surface(self):
        return self.surface

    def rerender_images(self):

        self.rendered_images = []

        indices = [(self.image_index - i - 1)%len(self.images) for i in range(self.images_span)] +\
                    [self.image_index] + [(self.image_index + i + 1)%len(self.images) for i in range(self.images_span)]


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

            scale_factor *= self.scale_mults[i]

            img = pygame.transform.scale(img, (int(img.get_width()*scale_factor), int(img.get_height() * scale_factor)))
            img.set_alpha(self.images_alphas[i])

            img_pos = graphics.get_center_with_surface(img, rect)

            self.rendered_images.append([img, img_pos[0], img_pos[1]])
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

        self.surface.fill(self.background_color)

        for img, x, y in self.rendered_images:
            self.surface.blit(img, (x, y))

    def tick(self):

        if self.state == ImageSlider.NOT_SLIDING:
            if self.slides != 0:
                if self.slides > 0:
                    self.state = ImageSlider.SLIDING_RIGHT
                    self.initialize_slide()
                else:
                    self.state = ImageSlider.SLIDING_LEFT
                    self.initialize_slide()
