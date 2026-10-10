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
from widgets.widget import Widget
from event_queue_manager import Event

class LabeledImageSlider(Widget):

    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3

    class EventTypes:

        SELECT_ANIMATION_ENDED = 0
        FLIPPING_ANIMATION_ENDED = 1
        SLIDING_ANIMATION_ENDED = 2

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
        text_color=Colors.BLACK,
        back_images = None,
        flipping_animation_duration = 500#ms
    ):

        super().__init__(frame_dim)
        self.images = images
        self.back_images = (back_images if back_images is not None else self.images.copy())
        self.text = text
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
        self.flipping_animation_duration = flipping_animation_duration

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

    @Widget.frame_dim.setter
    def frame_dim(self, oframe):

        self.is_sliding = False

        Widget.frame_dim.fset(self, oframe)

        self.image_slider.dim_frame = oframe
        self.text_slider.dim_frame = oframe

        self.rerender()

    def play_select_animation(self):
        self.select_animation_queued = True

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

        self.image_slider = ImageSlider(
                                        self.images,
                                        irect,
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
                                        self.max_slides,
                                        self.back_images,
                                        self.flipping_animation_duration
                                        )
        self.text_slider = TextSlider(
                                        self.text,
                                        trect,
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

        self.background_surface = pygame.Surface((self.frame_dim.width , self.frame_dim.height), pygame.SRCALPHA)
        self.background_surface.fill(self.background_color)




    def get_image_surfaces(self):
        return self.image_slider.get_surfaces()

    def get_text_surfaces(self):
        return self.text_slider.get_surfaces()

    def get_surfaces(self):
        ims = self.image_slider.get_surfaces()
        ims.extend(self.text_slider.get_surfaces()).extend([self.background_surface])
        return ims

    def get_surfaces_with_position(self):

        #returns a list of [(surface, (x, y))]
        back = [(self.background_surface, (self.x, self.y))]
        ix, iy = self.imagepos
        tx, ty = self.textpos
        back.append((self.image_slider.top_surface, self.imagepos))
        back.append((self.text_slider.top_surface, self.textpos))

        return back

    def render(self):
        pass

    def tick(self):

        if self.queued_slides != 0 and not self.is_sliding and not self.image_slider.select_animation_playing() and not self.image_slider.flipping_animation_playing():
            self.is_sliding = True
            self.isliding_finished = False
            self.tsliding_finished = False
            if self.queued_slides < 0:
                self.image_slider.slide_left()
                self.text_slider.slide_left()
                self.queued_slides += 1
            else:
                self.image_slider.slide_right()
                self.text_slider.slide_right()
                self.queued_slides -= 1

        if not self.is_sliding and self.select_animation_queued and not self.cardflip_queued and not self.cardflips_queued:
            self.select_animation_queued = False
            self.image_slider.play_select_animation()
        elif not self.is_sliding and self.cardflips_queued:
            self.cardflips_queued = False
            self.image_slider.flip_all_cards()
        elif not self.is_sliding and self.cardflip_queued:
            self.cardflip_queued = False
            self.image_slider.flip_card()

        if self.is_sliding and self.isliding_finished and self.tsliding_finished:
            self.is_sliding = False
            self.isliding_finished = False
            self.tsliding_finished = False

        ievents = self.image_slider.poll_events()
        tevents = self.text_slider.poll_events()

        for event in ievents:
            if event.type == ImageSlider.EventTypes.SLIDING_ANIMATION_ENDED:
                self.isliding_finished = True
                self.event_queue.append(Event(LabeledImageSlider.EventTypes.SLIDING_ANIMATION_ENDED, None))
            elif event.type == ImageSlider.EventTypes.SELECT_ANIMATION_ENDED:
                self.event_queue.append(Event(LabeledImageSlider.EventTypes.SELECT_ANIMATION_ENDED, None))
            elif event.type == ImageSlider.EventTypes.FLIPPING_ANIMATION_ENDED:
                self.event_queue.append(Event(LabeledImageSlider.EventTypes.FLIPPING_ANIMATION_ENDED, None))

        for event in tevents:
            if event.type == TextSlider.EventTypes.SLIDING_ANIMATION_ENDED:
                self.tsliding_finished = True


        self.image_slider.tick()
        self.text_slider.tick()

    def flip_card(self):
        self.cardflip_queued = True

    def flip_all_cards(self):

        self.cardflips_queued = True

    def slide_left(self):

        self.queued_slides -= 1

    def slide_right(self):

        self.queued_slides += 1

    def reset_slides(self):

        self.image_slider-reset_slides()
        self.text_slider.reset_slides()
        self.queued_slides = 0


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
