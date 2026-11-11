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
from Frames.widgets.slider import Slider

class LabeledImageSlider(Slider):
    """
    Combines ImageSlider with TextSlider.
    """

    #location enums for the text location
    LEFT: id_t = R_ID()
    RIGHT: id_t = R_ID()
    TOP: id_t = R_ID()
    BOTTOM: id_t = R_ID()

    #STATES
    FLIPPING_ONLY_IMAGE_SLIDER_ANIMATION_PLAYING: id_t = R_ID()
    FLIPPING_ONLY_TEXT_SLIDER_ANIMATION_PLAYING: id_t = R_ID()
    FLIPPING_ALL_CARDS_ONLY_IMAGE_SLIDER_ANIMATION_PLAYING: id_t = R_ID()
    FLIPPING_ALL_CARDS_ONLY_TEXT_SLIDER_ANIMATION_PLAYING: id_t = R_ID()

    AWAITING_IMAGE_SLIDER_FLIP: id_t = R_ID()
    AWAITING_TEXT_SLIDER_FLIP: id_t = R_ID()
    #
    SLIDING_LEFT_ONLY_IMAGE_SLIDER: id_t = R_ID()
    SLIDING_RIGHT_ONLY_IMAGE_SLIDER: id_t = R_ID()

    SLIDING_LEFT_ONLY_TEXT_SLIDER: id_t = R_ID()
    SLIDING_RIGHT_ONLY_TEXT_SLIDER: id_t = R_ID()

    AWAITING_IMAGE_SLIDER_SLIDE: id_t = R_ID()
    AWAITING_TEXT_SLIDER_SLIDE: id_t = R_ID()
    #
    ONLY_IMAGE_SLIDER_SELECT_ANIMATION_PLAYING: id_t = R_ID()
    ONLY_TEXT_SLIDER_SELECT_ANIMATION_PLAYING: id_t = R_ID()

    AWAITING_IMAGE_SLIDER_SELECT: id_t = R_ID()
    AWAITING_TEXT_SLIDER_SELECT: id_t = R_ID()

    #extending event types

    class EventTypes(Slider.EventTypes):

        ONLY_IMAGE_SLIDER_FLIPPING_ANIMATION_FINISHED: id_t = R_ID()
        ONLY_TEXT_SLIDER_FLIPPING_ANIMATION_FINISHED: id_t = R_ID()

        ONLY_IMAGE_SLIDER_SLIDING_ANIMATION_ENDED: id_t = R_ID()
        ONLY_TEXT_SLIDER_SLIDING_ANIMATION_ENDED: id_t = R_ID()

        ONLY_IMAGE_SLIDER_SELECT_ANIMATION_ENDED: id_t = R_ID()
        ONLY_TEXT_SLIDER_SELECT_ANIMATION_ENDED: id_t = R_ID()

    #events

    #overriding standard events.
    class SelectAnimationEndedEvent(Event):

        def __init__(self, image_slider_index: int, text_slider_index: int):

            Event.__init__(
                            self,
                            etype=LabeledImageSlider.EventTypes.SELECT_ANIMATION_ENDED,
                            data=None
                            )

            self.image_slider_index: int = image_slider_index
            """
            The index of the image slider
            """
            self.text_slider_index: int = text_slider_index
            """
            The index of the text slider.
            """

        @override
        def copy(self) -> LabeledImageSlider.SelectAnimationEndedEvent:
            return LabeledImageSlider.SelectAnimationEndedEvent(self.image_slider_index, self.text_slider_index)

    class FlippingAnimationEndedEvent(Event):

        def __init__(self, image_slider_index: int, text_slider_index: int, all_flipped: bool):

            Event.__init__(
                            self,
                            etype=LabeledImageSlider.EventTypes.FLIPPING_ANIMATION_ENDED,
                            data=None
                            )

            self.image_slider_index: int = image_slider_index
            """
            The index of the image slider
            """
            self.text_slider_index: int = text_slider_index
            """
            The index of the text slider.
            """
            self.all_flipped: bool = all_flipped
            """
            If all cards were flipped or not.
            """

        @override
        def copy(self) -> LabeledImageSlider.FlippingAnimationEndedEvent:
            return LabeledImageSlider.FlippingAnimationEndedEvent(self.image_slider_index, self.text_slider_index, self.all_flipped)

    class SlidingAnimationEndedEvent(Event):

        def __init__(self, image_slider_index: int, text_slider_index: int):

            Event.__init__(
                            self,
                            etype=LabeledImageSlider.EventTypes.SLIDING_ANIMATION_ENDED,
                            data=None
                            )

            self.image_slider_index: int = image_slider_index
            """
            The index of the image slider
            """
            self.text_slider_index: int = text_slider_index
            """
            The index of the text slider.
            """

        @override
        def copy(self) -> LabeledImageSlider.SlidingAnimationEndedEvent:
            return LabeledImageSlider.SlidingAnimationEndedEvent(self.image_slider_index, self.text_slider_index)

    #own events
    class OnlyImageSliderFlippingAnimationEndedEvent(Slider.FlippingAnimationEndedEvent):

        def __init__(self, selected_index: int, all_flipped: bool):

            Slider.FlippingAnimationEndedEvent.__init__(
                                                        self,
                                                        selected_index,
                                                        all_flipped
                                                        )
            #setting correct type
            self.type = LabeledImageSlider.EventTypes.ONLY_IMAGE_SLIDER_FLIPPING_ANIMATION_FINISHED

        @override
        def copy(self) -> LabeledImageSlider.OnlyImageSliderFlippingAnimationEndedEvent:
            return LabeledImageSlider.OnlyImageSliderFlippingAnimationEndedEvent(self.selected_index, self.all_flipped)

    class OnlyTextSliderFlippingAnimationEndedEvent(Slider.FlippingAnimationEndedEvent):

        def __init__(self, selected_index: int, all_flipped: bool):

            Slider.FlippingAnimationEndedEvent.__init__(self,
                                                        selected_index,
                                                        all_flipped
                                                        )
            #setting correct type
            self.type = LabeledImageSlider.EventTypes.ONLY_TEXT_SLIDER_FLIPPING_ANIMATION_FINISHED

        @override
        def copy(self) -> LabeledImageSlider.OnlyTextSliderFlippingAnimationEndedEvent:
            return LabeledImageSlider.OnlyTextSliderFlippingAnimationEndedEvent(self.selected_index, self.all_flipped)

    class OnlyImageSliderSlidingAnimationEndedEvent(Slider.SlidingAnimationEndedEvent):

        def __init__(self, selected_index: int):

            Slider.SlidingAnimationEndedEvent.__init__(
                                                        self,
                                                        selected_index
                                                        )
            #setting correct type
            self.type = LabeledImageSlider.EventTypes.ONLY_IMAGE_SLIDER_SLIDING_ANIMATION_ENDED

        @override
        def copy(self) -> LabeledImageSlider.OnlyImageSliderSlidingAnimationEndedEvent:
            return LabeledImageSlider.OnlyImageSliderSlidingAnimationEndedEvent(self.selected_index)

    class OnlyTextSliderSlidingAnimationEndedEvent(Slider.SlidingAnimationEndedEvent):

        def __init__(self, selected_index: int):

            Slider.SlidingAnimationEndedEvent.__init__(
                                                        self,
                                                        selected_index
                                                        )
            #setting correct type
            self.type = LabeledImageSlider.EventTypes.ONLY_TEXT_SLIDER_SLIDING_ANIMATION_ENDED

        @override
        def copy(self) -> LabeledImageSlider.OnlyTextSliderSlidingAnimationEndedEvent:
            return LabeledImageSlider.OnlyTextSliderSlidingAnimationEndedEvent(self.selected_index)

    class OnlyImageSliderSelectAnimationEndedEvent(Slider.SelectAnimationEndedEvent):

        def __init__(self, selected_index: int):

            Slider.SelectAnimationEndedEvent.__init__(
                                                        self,
                                                        selected_index
                                                        )
            #setting correct type
            self.type = LabeledImageSlider.EventTypes.ONLY_IMAGE_SLIDER_SELECT_ANIMATION_ENDED

        @override
        def copy(self) -> LabeledImageSlider.OnlyImageSliderSelectAnimationEndedEvent:
            return LabeledImageSlider.OnlyImageSliderSelectAnimationEndedEvent(self.selected_index)

    class OnlyTextSliderSelectAnimationEndedEvent(Slider.SelectAnimationEndedEvent):

        def __init__(self, selected_index: int):

            Slider.SelectAnimationEndedEvent.__init__(
                                                        self,
                                                        selected_index
                                                        )
            #setting correct type
            self.type = LabeledImageSlider.EventTypes.ONLY_TEXT_SLIDER_SELECT_ANIMATION_ENDED

        @override
        def copy(self) -> LabeledImageSlider.OnlyTextSliderSelectAnimationEndedEvent:
            return LabeledImageSlider.OnlyTextSliderSelectAnimationEndedEvent(self.selected_index)


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

        #queue variables
        self.flip_image_card_queued: bool = False
        """
        Queue variable for one image card flip.
        """
        self.fill_all_image_cards_queued: bool = False
        """
        Queue variable for flipping all image cards.
        """
        self.flip_text_card_queued: bool = False
        """
        Queue variable for one text card flip.
        """
        self.flip_all_text_cards_queued: bool = False
        """
        Queue variable for flipping all text cards.
        """
        self.only_image_slides: int = 0
        """
        Only the images slides.
        """
        self.only_text_slides: int = 0
        """
        Only the text slides.
        """
        self.select_only_image_card_queued: bool = False
        """
        Flag for if only a image slider selection is queued.
        """
        self.select_only_text_card_queued: bool = False
        """
        Flag for if only an image slider selection is queued.
        """

        #checking the length of the given sliders
        self._check_surface_variables_length()
        #checking the text text_location
        if horizontal and text_location not in [LabeledImageSlider.BOTTOM, LabeledImageSlider.TOP]:
            raise RuntimeError("Text Location not appropriate")

        if not horizontal and text_location not in [LabeledImageSlider.LEFT, LabeledImageSlider.RIGHT]:
            raise RuntimeError("Text Location not appropriate")

        Slider.__init__(
                        self,
                        frame_dim=frame_dim,
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
                        flip_duration=flip_duration
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
    comp_len: int = surface_variables_list[0]

    #checking lengths
    if not all([x == comp_len for x in len_list]):
        #error
        raise RuntimeError("The given surface variables have to be of the same length.")

    #============================================
    #ABSTRACT METHODS
    #============================================

    @override
    def create_surfaces(self) -> None:
        """
        Does nothing. Surface creation happens inside
        self.image_slider and self.text_slider.
        """
        pass

    @override
    def create_back_surfaces(self) -> None:
        """
        Does nothing. Back surface creation happens inside
        self.image_slider and self.text_slider.
        """
        pass

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
                                            flip_duration=self.flipping_animation_duration,
                                            text_alphas=self.alphas,
                                            text_span=self.span,
                                            background_color=self.background_color,
                                            size_decrease_scale=self.size_decrease_scale,
                                            horizontal=self.horizontal,
                                            start_index=self.start_index,
                                            cutoff=self.cutoff,
                                            max_slides=self.max_slides
                                        )


        self.prerender()

    @override
    def prerender(self) -> None:
        """
        Prerendering.
        """

        self.surface.fill(self.background_color)

        self.image_slider.prerender()
        self.text_slider.prerender()

        self.image_slider.render(self.surface)
        self.text_slider.render(self.surface)

    #============================================
    #STANDARD FUNCTIONS
    #============================================

    def flip_only_image_card(self) -> bool:
        """
        Returns true on successful queue, else False.
        """
        if self.flip_only_image_card_animation_playing():
            return False
        else:
            self.flip_image_card_queued = True
            return True

    def flip_only_all_image_cards(self) -> bool:
        """
        Returns true on successful queue, else False.
        """
        if self.flip_only_all_image_cards_animation_playing():
            return False
        else:
            self.flip_all_image_cards_queued = True
            return True

    def flip_only_text_card(self) -> bool:
        """
        Returns true on successful queue, else False.
        """
        if self.flip_only_text_card_animation_playing():
            return False
        else:
            self.flip_text_card_queued = True
            return True

    def flip_only_all_text_cards(self) -> bool:
        """
        Returns true on successful queue, else False.
        """
        if self.flip_only_all_text_cards_animation_playing():
            return False
        else:
            self.flip_all_text_cards_queued = True
            return True

    #sliding
    def slide_left_only_images(self) -> bool:
        """
        Slides only the images left.
        """
        pass

    #============================================
    #STATE CHECK FUNCTIONS
    #============================================

    def flip_only_image_card_animation_playing(self) -> bool:
        """
        Returns true if the flip image card animation is playing.
        """
        return (self.state == LabeledImageSlider.FLIPPING_ONLY_IMAGE_SLIDER_ANIMATION_PLAYING)

    def flip_only_all_image_cards_animation_playing(self) -> bool:
        """
        Returns true if the flip image card animation is playing.
        """
        return (self.state == LabeledImageSlider.FLIPPING_ALL_CARDS_ONLY_IMAGE_SLIDER_ANIMATION_PLAYING)

    def flip_only_text_card_animation_playing(self) -> bool:
        """
        Returns true if the flip image card animation is playing.
        """
        return (self.state == LabeledImageSlider.FLIPPING_ONLY_TEXT_SLIDER_ANIMATION_PLAYING)

    def flip_only_all_text_cards_animation_playing(self) -> bool:
        """
        Returns true if the flip image card animation is playing.
        """
        return (self.state == LabeledImageSlider.FLIPPING_ALL_CARDS_ONLY_TEXT_SLIDER_ANIMATION_PLAYING)

    def any_sliding_animation_playing(self) -> bool:
        """
        Returns if any sliding animation is playing.
        """
        pass

    def any_flipping_animation_playing(self) -> bool:
        """
        Returns if any flipping animation is playing.
        """
        return (
                    self.flip_only_image_card_animation_playing() or\
                    self.flip_only_all_image_cards_animation_playing() or\
                    self.flip_only_text_card_animation_playing() or\
                    self.flip_only_all_text_cards_animation_playing() or\
                    self.flipping_animation_playing()
                )

    def any_select_animation_playing(self) -> bool:
        """
        Returns if any select animation is playing.
        """
        pass


    #============================================
    #TICK
    #============================================


    @override
    def tick(self) -> Frame:
        """
        Slider tick method.
        """

        self.image_slider.tick()
        self.text_slider.tick()

        if self.state == LabeledImageSlider.SLIDING_LEFT:

            self.image_slider.render_slide_left()
            self.text_slider.render_slide_left()

        elif self.state == LabeledImageSlider.SLIDING_RIGHT:

            self.image_slider.render_slide_right()
            self.text_slider.render_slide_right()

        elif self.state == LabeledImageSlider.SELECT_ANIMATION_PLAYING:

            #plays both select animations
            self.image_slider.render_select_animation()
            self.text_slider.render_select_animation()

        elif self.state == Slider.FLIPPING_ANIMATION_PLAYING:

            #flips all surfaces
            self.image_slider.render_flipping_animation()
            self.text_slider.render_flipping_animation()

        elif self.state == Slider.FLIPPING_ALL_ANIMATION_PLAYING:
            self.render_flipping_all_animation()

        elif self.state == Slider.NOT_SLIDING:

            if self.slides != 0:
                if self.slides > 0:

                    self.state = Slider.SLIDING_RIGHT

                    #deferring slide instructions
                    self.image_slider.slide_right()
                    self.text_slider.slide_right()

                else:

                    self.state = Slider.SLIDING_LEFT

                    #deferring slide instructions
                    self.image_slider.slide_left()
                    self.text_slider.slide_left()

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

        #polling events
        image_slider_events: list[Event] = self.image_slider.poll_events()
        text_slider_events: list[Event] = self.text_slider.poll_events()

        for event in image_slider_events:

            if event.type == ImageSlider.EventTypes.SLIDING_ANIMATION_ENDED:
                #pushing own event
                self.push_event(event)

                #we need to increase or decrease the slides counter
                if self.state == LabeledImageSlider.SLIDING_LEFT:
                    self.slides += 1
                elif self.state == LabeledImageSlider.SLIDING_RIGHT:
                    self.slides -= 1

                self.state = LabeledImageSlider.NOT_SLIDING

        if (self.state != Slider.NOT_SLIDING):
            self.raise_prerender_flag()

        if self.prerender_flag_raised():
            self.prerender()
            self.reset_prerender_flag()

        return self
