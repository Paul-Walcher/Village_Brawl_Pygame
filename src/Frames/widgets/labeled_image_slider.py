from __future__ import annotations
from typing import Type, Any, Callable, override

import pygame

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

import graphics
from graphics import page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t
from clock import Clock
from event_queue_manager import Event
from enum import Enum, auto

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.image_slider import ImageSlider
from Frames.widgets.text_slider import TextSlider
from Frames.widgets.multi_slider import MultiSlider

class LabeledImageSlider(MultiSlider):
    """
    Combines ImageSlider with TextSlider.
    """

    #location enums for the text location
    LEFT: id_t = R_ID()
    RIGHT: id_t = R_ID()
    TOP: id_t = R_ID()
    BOTTOM: id_t = R_ID()
    #events

    #overriding standard events


    def __init__(
                    self,
                    frame_dim: pygame.Rect,
                    #necessary slider variables
                    images: list[str],
                    text_pages: list[colored_page_t],
                    #image slider variables
                    selected_images: list[str] = None,
                    back_images: list[str] = None,
                    selected_back_images: list[str] = None,
                    #text slider variables
                    selected_text_pages: list[colored_page_t] = None,
                    back_text_pages: list[colored_page_t] = None,
                    selected_back_text_pages: list[colored_page_t] = None,
                    font: pygame.font.Font = Fonts.STANDARD_FONT,
                    line_margin_percentage: float = 0.05,
                    text_color: color_t = Colors.STANDARD_TEXT_COLOR,
                    #LabeledSlider variables
                    image_to_text_distribution: float = 0.8,
                    image_text_distance_percentage: float = 0.1,
                    text_location: int = None,
                    #traditional slider variables
                    alphas: list[int] = None,
                    span: int = 1,
                    background_color: color_t = Colors.TRANSPARENT,
                    size_decrease_scale: float = 0.5,
                    horizontal: bool = True,
                    start_index: int = 0,
                    cutoff: bool = False,
                    max_slides: int = 10,
                    sliding_duration: float = 500,  # ms
                    select_animation_duration: float = 400,#ms
                    flipping_animation_duration: float = 400#ms
                ):

        #setting the variables for self.rerender
        #image slider variables
        self.images: list[str] = images
        """
        Images for ImageSlider.
        """
        self.selected_images: list[str] = selected_images
        """
        Selected images for ImageSlider.
        """
        self.back_images: list[str] = back_images
        """
        Back images for ImageSlider.
        """
        self.selected_back_images: list[str] = selected_back_images
        """
        Selected back images for the ImageSlider
        """

        #TextSlider variables

        self.text_pages: list[colored_page_t] = text_pages
        """
        Text pages for the TextSlider.
        """
        self.selected_text_pages: list[colored_page_t] = selected_text_pages
        """
        Selected text pages for the TextSlider.
        """
        self.back_text_pages: list[colored_page_t] = back_text_pages
        """
        Back text pages for the TextSlider.
        """
        self.selected_back_text_pages: list[colored_page_t] = selected_back_text_pages
        """
        The selected back text pages for the TextSlider.
        """
        self.font: pygame.font.Font = font
        """
        Font for the text slider.
        """
        self.text_color: color_t = text_color
        """
        Text color for the text slider.
        """
        self.line_margin_percentage: float = line_margin_percentage
        """
        Line margin percentage for the text slider.
        """

        #variables for LabeledImageSlider

        self.image_to_text_distribution: float = image_to_text_distribution
        """
        The percentage of area reserved for the image slider.
        """
        self.image_text_distance_percentage: float = image_text_distance_percentage
        """
        The area reserved as space between the ImageSlider and TextSlider.
        """
        self.text_location: int = (text_location if text_location is not None else LabeledImageSlider.BOTTOM)
        """
        The text location.
        """
        self.image_slider: ImageSlider = None
        """
        The own image slider reference.
        """
        self.text_slider: TextSlider = None
        """
        The own text slider reference.
        """
        #checking the length of the given sliders
        self._check_surface_variables_length()
        #checking the text text_location
        if horizontal and text_location not in [LabeledImageSlider.BOTTOM, LabeledImageSlider.TOP]:
            raise RuntimeError("Text Location not appropriate")

        if not horizontal and text_location not in [LabeledImageSlider.LEFT, LabeledImageSlider.RIGHT]:
            raise RuntimeError("Text Location not appropriate")

        MultiSlider.__init__(
                                self,
                                frame_dim=frame_dim,

                                sliders=[],
                                slider_percentages=[],

                                sliding_duration=sliding_duration,
                                select_animation_duration=select_animation_duration,
                                alphas=alphas,
                                span=span,
                                background_color=background_color,
                                size_decrease_scale=size_decrease_scale,
                                horizontal=horizontal,
                                start_index=start_index,
                                cutoff=cutoff,
                                max_slides=max_slides,
                                flip_duration=flipping_animation_duration
                            )

        #rerender is called here

        #setting the frame enum
        self.frame_enum = FrameEnums.LABELED_IMAGE_SLIDER_WIDGET


    def _check_surface_variables_length(self) -> None:
        """
        Checks if the surface variables are valid.
        """

        surface_variables_list: list[list] =    [
                                                    self.images,
                                                    self.text_pages,
                                                ]

        if self.selected_images is not None:
            surface_variables_list.append(self.selected_images)
        if self.back_images is not None:
            surface_variables_list.append(self.back_images)
        if self.selected_back_images is not None:
            surface_variables_list.append(self.selected_back_images)

        if self.selected_text_pages is not None:
            surface_variables_list.append(self.selected_text_pages)
        if self.back_text_pages is not None:
            surface_variables_list.append(self.back_text_pages)
        if self.selected_back_text_pages is not None:
            surface_variables_list.append(self.selected_back_text_pages)

        #getting a list of lengths
        len_list: list[int] = list(map(len, surface_variables_list))
        comp_len: int = len_list[0]

        #checking lengths
        if not all([x == comp_len for x in len_list]):
            #error
            raise RuntimeError("The given surface variables have to be of the same length.")


    #============================================
    #RERENDERING
    #============================================

    @override
    def rerender(self):
        """
        Rerendering, creating self.image_slider and self.text_slider.
        """

        self.images_width: int = 0 #actual width of the image slider
        self.images_height: int = 0 #actual height of the image slider
        self.text_width: int = 0 #actual width of the text slider
        self.text_height: int = 0 #actual height of the text slider

        self.true_width: int = 0 #actual width of the slider area
        self.true_height: int = 0 #actual height of the slider area

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

        #frame rects for self.image_slider and self.text_slider
        irect = pygame.Rect(*self.imagepos, self.images_width, self.images_height)
        relative_irect = graphics.position_relative(self.frame_dim, irect)
        trect = pygame.Rect(*self.textpos, self.text_width, self.text_height)
        relative_trect = graphics.position_relative(self.frame_dim, trect)

        #creating the sliders
        self.image_slider = ImageSlider(
                                            frame_dim=relative_irect,
                                            images=self.images,
                                            selected_images=self.selected_images,
                                            back_images=self.back_images,
                                            selected_back_images=self.selected_back_images,

                                            sliding_duration=self.sliding_duration,  # ms
                                            select_animation_duration=self.select_animation_duration,
                                            flip_duration=self.flip_duration,
                                            images_alphas=self.alphas,
                                            images_span=self.span,
                                            background_color=self.background_color,
                                            size_decrease_scale=self.size_decrease_scale,
                                            horizontal=self.horizontal,
                                            start_index=self.surface_index,
                                            cutoff=self.cutoff,
                                            max_slides=self.max_slides
                                        )

        self.text_slider = TextSlider(
                                            frame_dim=relative_trect,
                                            text_pages=self.text_pages,
                                            selected_text_pages=self.selected_text_pages,
                                            back_text_pages=self.back_text_pages,
                                            selected_back_text_pages=self.selected_back_text_pages,
                                            font=self.font,
                                            text_color=self.text_color,
                                            line_margin_percentage=self.line_margin_percentage,

                                            sliding_duration=self.sliding_duration,  # ms
                                            select_animation_duration=self.select_animation_duration,
                                            flip_duration=self.flip_duration,
                                            text_alphas=self.alphas,
                                            text_span=self.span,
                                            background_color=self.background_color,
                                            size_decrease_scale=self.size_decrease_scale,
                                            horizontal=self.horizontal,
                                            start_index=self.surface_index,
                                            cutoff=self.cutoff,
                                            max_slides=self.max_slides
                                        )


        #readying for calling MultiSlider.rerender
        self.sliders = []
        self.slider_percentages = []

        text_distribution: float = (1.0 - self.image_to_text_distribution - self.image_text_distance_percentage)

        percentages_image_text: list[float] = [self.image_to_text_distribution, self.image_text_distance_percentage, text_distribution]
        percentages_text_image: list[float] = [text_distribution, self.image_text_distance_percentage, self.image_to_text_distribution]

        if self.horizontal:

            if self.text_location == LabeledImageSlider.LEFT:
                self.sliders = [self.text_slider, self.image_slider]
                self.slider_percentages = percentages_text_image

            elif self.text_location == LabeledImageSlider.BOTTOM:
                self.sliders = [self.image_slider, self.text_slider]
                self.slider_percentages = percentages_image_text

        else:

            if self.text_location == LabeledImageSlider.TOP:
                self.sliders = [self.text_slider, self.image_slider]
                self.slider_percentages = percentages_text_image

            elif self.text_location == LabeledImageSlider.RIGHT:
                self.sliders = [self.image_slider, self.text_slider]
                self.slider_percentages = percentages_image_text

        #rerendering the MultiSlider
        MultiSlider.rerender(self)
