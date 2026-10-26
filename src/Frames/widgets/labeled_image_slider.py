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
    FrameDataID,
    R_ID
)
import graphics
from clock import Clock
from modules import Modules
import constants

from Frames.widgets.image_slider import ImageSlider
from Frames.widgets.text_slider import TextSlider
from Frames.widgets.slider import Slider
from event_queue_manager import Event

class LabeledImageSlider(Frame):

    LEFT = R_ID()
    RIGHT = R_ID()
    TOP = R_ID()
    BOTTOM = R_ID()

    class EventTypes:

        SELECT_ANIMATION_ENDED = R_ID()
        FLIPPING_ANIMATION_ENDED = R_ID()
        SLIDING_ANIMATION_ENDED = R_ID()

    def __init__(
        self,
        images,
        text,
        frame_dim,
        font=Fonts.MINECRAFT,
        text_location=None,
        sliding_duration=500,  # ms
        select_animation_duration=800,#ms
        alphas=None,
        span=1,
        background_color=Colors.TRANSPARENT,
        size_decrease_scale=0.5,
        image_to_text_distribution=0.8,
        image_text_distance_percentage=0.1,
        horizontal=True,
        start_index=0,
        cutoff=False,
        max_slides=10,
        font_startsize=30,
        line_margin_percentage=0.05,
        text_color=Colors.BLACK,
        text_is_colored=False,
        back_images = None,
        back_text=None,
        text_width_to_height_ratio=7/5,
        flipping_animation_duration = 500#ms
    ):

        super().__init__(FrameEnums.LABELED_IMAGE_SLIDER_WIDGET, None, frame_dim, focus_group=None)
        self.images = images
        self.back_images = back_images
        self.back_text = back_text
        self.text = text
        self.font = font
        self.text_is_colored = text_is_colored
        self.text_location = (text_location if text_location is not None else LabeledImageSlider.BOTTOM)
        self.sliding_duration = sliding_duration
        self.select_animation_duration = select_animation_duration
        self.alphas = alphas
        self.span = span
        self.background_color = background_color
        self.size_decrease_scale = size_decrease_scale
        self.horizontal = horizontal
        self.start_index = start_index
        self.cutoff = cutoff
        self.max_slides = max_slides
        self.line_margin_percentage = line_margin_percentage
        self.text_color = text_color
        self.image_to_text_distribution = image_to_text_distribution
        self.image_text_distance_percentage = image_text_distance_percentage
        self.flipping_animation_duration = flipping_animation_duration
        self.text_width_to_height_ratio = text_width_to_height_ratio

        if self.horizontal and self.text_location not in [LabeledImageSlider.BOTTOM, LabeledImageSlider.TOP]:
            raise RuntimeError("Text Location not appropriate")

        if not self.horizontal and self.text_location not in [LabeledImageSlider.LEFT, LabeledImageSlider.RIGHT]:
            raise RuntimeError("Text Location not appropriate")

        self.image_slider = None
        self.text_slider = None

        self.event_queue = []
        self.queued_slides = 0
        self.is_sliding = False

        self.isliding_finished = False
        self.tsliding_finished = False
        self.select_animation_queued = False

        self.cardflip_queued = False
        self.cardflips_queued = False

        self.rerender()

    def play_select_animation(self):
        self.select_animation_queued = True

    def flip_card(self):
        self.cardflip_queued = True

    def flip_all_cards(self):
        self.cardflips_queued = True

    def select_animation_playing(self):
        return self.image_slider.select_animation_playing()

    def flipping_animation_playing(self):
        self.image_slider.flipping_animation_playing()

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

        irect = pygame.Rect(*self.imagepos, self.images_width, self.images_height)
        trect = pygame.Rect(*self.textpos, self.text_width, self.text_height)

        self.irect = irect
        self.trect = trect

        self.image_slider = ImageSlider(
                                        images=self.images,
                                        frame_dim=irect,
                                        back_images=self.back_images,
                                        sliding_duration=self.sliding_duration,  # ms
                                        select_animation_duration=self.select_animation_duration,
                                        images_alphas=self.alphas,
                                        images_span=self.span,
                                        background_color=self.background_color,
                                        size_decrease_scale=self.size_decrease_scale,
                                        horizontal=self.horizontal,
                                        start_index=self.start_index,
                                        cutoff=self.cutoff,
                                        max_slides=self.max_slides,
                                        flip_duration=self.flipping_animation_duration
                                        )

        self.text_slider = TextSlider(
                                        text=self.text,
                                        frame_dim=trect,
                                        back_text=self.back_text,
                                        font=self.font,
                                        sliding_duration=self.sliding_duration,  # ms
                                        select_animation_duration=self.select_animation_duration,
                                        flip_duration=self.flipping_animation_duration,
                                        images_alphas=self.alphas,
                                        images_span=self.span,
                                        background_color=self.background_color,
                                        size_decrease_scale=self.size_decrease_scale,
                                        horizontal=self.horizontal,
                                        start_index=self.start_index,
                                        cutoff=self.cutoff,
                                        max_slides=self.max_slides,
                                        line_margin_percentage=self.line_margin_percentage,
                                        text_color=self.text_color,
                                        text_is_colored=self.text_is_colored,
                                        text_width_to_height_ratio=self.text_width_to_height_ratio
                                        )

        self.background_surface = pygame.Surface((self.frame_dim.width , self.frame_dim.height), pygame.SRCALPHA)
        self.background_surface.fill(self.background_color)

    def prerender(self):
        pass

    def tick(self):

        ievents = self.image_slider.poll_events()
        tevents = self.text_slider.poll_events()

        for event in ievents:
            if event.type == Slider.EventTypes.SLIDING_ANIMATION_ENDED:
                self.event_queue.append(Event(LabeledImageSlider.EventTypes.SLIDING_ANIMATION_ENDED, None))
            elif event.type == Slider.EventTypes.SELECT_ANIMATION_ENDED:
                self.event_queue.append(Event(LabeledImageSlider.EventTypes.SELECT_ANIMATION_ENDED, None))
            elif event.type == Slider.EventTypes.FLIPPING_ANIMATION_ENDED:
                self.event_queue.append(Event(LabeledImageSlider.EventTypes.FLIPPING_ANIMATION_ENDED, None))



        self.image_slider.tick()
        self.text_slider.tick()

    def render(self, screen):

        self.image_slider.render(screen)
        self.text_slider.render(screen)

    def flip_card(self):
        self.image_slider.flip_card()

    def flip_all_cards(self):
        self.image_slider.flip_all_cards()

    def play_select_animation(self):
        self.image_slider.play_select_animation()

    def slide_left(self):

        self.image_slider.slide_left()
        self.text_slider.slide_left()

    def slide_right(self):

        self.image_slider.slide_right()
        self.text_slider.slide_right()

    def reset_slides(self):

        self.image_slider.reset_slides()
        self.text_slider.reset_slides()


    def get_selected_index(self):
        return self.image_slider.get_selected_index()


    def set_background_color(self, color):
        self.image_slider.set_background_color(color)
        self.text_slider.set_background_color(color)
        self.background_surface.fill(color)

    def get_focus_index(self):
        return self.image_slider.get_focus_index()

    def get_focus_image(self):
        return [self.image_slider.get_focus_image(), self.text_slider.get_focus_image()]
