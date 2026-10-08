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

from widgets.image_slider import ImageSlider
from widgets.text_slider import TextSlider

class LabeledImageSlider:

    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3

    def __init__(
        self,
        images,
        text,
        frame,
        font=Fonts.MINECRAFT,
        text_location=None,
        sliding_duration=500,  # ms
        select_animation_duration=800,#ms
        alphas=None,
        span=1,
        background_color=Colors.TRANSPARENT,
        size_distribution=0.6,
        size_decrease_scale=0.5,
        image_to_text_distribution=0.8,
        image_text_distance_percentage=0.1,
        horizontal=True,
        start_index=0,
        cutoff=False,
        max_slides=10,
        font_startsize=30,
        line_margin_percentage=0.05,
        text_color=Colors.BLACK
    ):

        self.frame = frame
        self.images = images
        self.text = text
        self.width = frame.width
        self.height = frame.height
        self.x = frame.x
        self.y = frame.y
        self.font = font
        self.text_location = (text_location if text_location is not None else LabeledImageSlider.BOTTOM)
        self.sliding_duration = sliding_duration
        self.select_animation_duration = select_animation_duration
        self.alphas = alphas
        self.span = span
        self.background_color = background_color
        self.size_distribution = size_distribution
        self.size_decrease_scale = size_decrease_scale
        self.horizontal = horizontal
        self.start_index = start_index
        self.cutoff = cutoff
        self.max_slides = max_slides
        self.font_startsize = font_startsize
        self.line_margin_percentage = line_margin_percentage
        self.text_color = text_color
        self.image_to_text_distribution = image_to_text_distribution
        self.image_text_distance_percentage = image_text_distance_percentage

        if self.horizontal and self.text_location not in [LabeledImageSlider.BOTTOM, LabeledImageSlider.TOP]:
            raise RuntimeError("Text Location not appropriate")

        if not self.horizontal and self.text_location not in [LabeledImageSlider.LEFT, LabeledImageSlider.RIGHT]:
            raise RuntimeError("Text Location not appropriate")

        self.image_slider = None
        self.text_slider = None

        self.rerender()

    def poll_events(self):

        return self.image_slider.poll_events().extend(self.text_slider.poll_events())

    def play_select_animation(self):
        self.image_slider.play_select_animation()

    def select_animation_playing(self):
        return self.image_slider.select_animation_playing()

    def rerender(self):

        self.images_width = 0
        self.images_height = 0
        self.text_width = 0
        self.text_height = 0

        self.true_width = 0
        self.true_height = 0


        if self.horizontal:

            self.true_width = self.width
            self.true_height = int((1.0 - self.image_text_distance_percentage) * self.height)
            self.image_text_distance = self.height - self.true_height

            self.images_width = self.width
            self.images_height = int(self.image_to_text_distribution * self.true_height)

            self.text_width = self.width
            self.text_height = int((1.0 - self.image_to_text_distribution) * self.true_height)

            if self.text_location == LabeledImageSlider.TOP:
                self.textpos = (self.x, self.y)
                self.imagepos = (self.x, self.y + self.text_height + self.image_text_distance)

            if self.text_location == LabeledImageSlider.BOTTOM:
                self.imagepos = (self.x, self.y)
                self.textpos = (self.x, self.y + self.images_height + self.image_text_distance)


        else:

            self.true_width = int((1.0 - self.image_text_distance_percentage) * self.width)
            self.true_height = self.height
            self.image_text_distance = self.width - self.true_width

            self.images_width = int(self.image_to_text_distribution * self.true_width)
            self.images_height = self.height

            self.text_width = int((1.0 - self.image_to_text_distribution) * self.true_width)
            self.text_height = self.height

            if self.text_location == LabeledImageSlider.LEFT:
                self.textpos = (self.x, self.y)
                self.imagepos = (self.x + self.text_width + self.image_text_distance, self.y)

            if self.text_location == LabeledImageSlider.RIGHT:
                self.imagepos = (self.x, self.y)
                self.textpos = (self.x + self.images_width + self.image_text_distance, self.y)


        self.image_slider = ImageSlider(
                                        self.images,
                                        self.images_width,
                                        self.images_height,
                                        self.sliding_duration,  # ms
                                        self.select_animation_duration,
                                        self.alphas,
                                        self.span,
                                        self.background_color,
                                        self.size_distribution,
                                        self.size_decrease_scale,
                                        self.horizontal,
                                        self.start_index,
                                        self.cutoff,
                                        self.max_slides
                                        )
        self.text_slider = TextSlider(
                                        self.text,
                                        self.text_width,
                                        self.text_height,
                                        self.font,
                                        self.sliding_duration,  # ms
                                        self.alphas,
                                        self.span,
                                        self.background_color,
                                        self.size_distribution,
                                        self.size_decrease_scale,
                                        self.horizontal,
                                        self.start_index,
                                        self.cutoff,
                                        self.max_slides,
                                        self.font_startsize,
                                        self.line_margin_percentage,
                                        self.text_color
                                        )

        self.background_surface = pygame.Surface((self.get_frame().width , self.get_frame().height), pygame.SRCALPHA)
        self.background_surface.fill(self.background_color)



    def get_frame(self):

        return self.frame.copy()

    def set_frame(self, frame):


        self.x = frame.x
        self.y = frame.y
        self.width = frame.width
        self.height = frame.height

        self.frame = frame.copy()

        self.rerender()


    def get_image_surfaces(self):
        return self.image_slider.get_surfaces()

    def get_text_surfaces(self):
        return self.text_slider.get_surfaces()

    def get_surfaces(self):
        return self.image_slider.get_surfaces().extend(self.text_slider.get_surfaces()).extend([self.background_surface])

    def get_surfaces_with_position(self):

        #returns a list of [(surface, (x, y))]
        back = [(self.background_surface, (self.x, self.y))]
        ix, iy = self.imagepos
        tx, ty = self.textpos
        back.append((self.image_slider.top_surface, self.imagepos))
        back.append((self.text_slider.top_surface, self.textpos))

        return back

    def tick(self):

        self.image_slider.tick()
        self.text_slider.tick()

    def slide_left(self):

        self.image_slider.slide_left()
        self.text_slider.slide_left()

    def slide_right(self):

        self.image_slider.slide_right()
        self.text_slider.slide_right()

    def reset_slides(self):

        self.image_slider-reset_slides()
        self.text_slider.reset_slides()


    def get_selected_index(self):
        self.image_slider.get_selected_index()


    def set_background_color(self, color):
        self.image_slider.set_background_color(color)
        self.text_slider.set_background_color(color)
        self.background_surface.fill(color)

    def get_focus_index(self):
        return self.image_slider.get_focus_index()

    def get_focus_image(self):
        return [self.image_slider.get_focus_image(), self.text_slider.get_focus_image()]
