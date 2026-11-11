from __future__ import annotations
from typing import Type, Any, Callable, override

import pygame

import graphics
from graphics import page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t
from constants import(
                        Colors,
                        color_t,
                        point_t,
                        R_ID,
                        fequal,
                        id_t
                        )
import calculations
from calculations import Weightlist
from event_queue_manager import Event
from collections.abc import Sequence

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.slider import Slider



class MultiSlider(Slider):
    """
    Takes n sliders to manage them.
    """

    #additional state
    SLIDING: id_t = R_ID()

    #==========================================
    # EVENTS
    #==========================================

    class SelectAnimationEndedEvent(Event):

        def __init__(
                        self,
                        sliders_active: list[Slider],
                        sliders_active_indices: list[int],
                        selected_indices: list[int]
                    ):

            Event.__init__(self, etype=MultiSlider.EventTypes.SELECT_ANIMATION_ENDED, data=None)

            self.sliders_active: list[Slider] = sliders_active
            """
            Reference to the sliders that were active in the selection process.
            """
            self.sliders_active_indices: list[int] = sliders_active_indices
            """
            Indices for the sliders that were active in the selection process.
            """
            self.selected_indices: list[int] = selected_indices
            """
            All of the sliders selected indices.
            """

        @override
        def copy(self) -> MultiSlider.SelectAnimationEndedEvent:
            return MultiSlider.SelectAnimationEndedEvent(
                                                            sliders_active=self.sliders_active.copy(),
                                                            sliders_active_indices=self.sliders_active_indices.copy(),
                                                            selected_indices=self.selected_indices.copy()
                                                        )


    class FlippingAnimationEndedEvent(Event):

        def __init__(
                        self,
                        sliders_active: list[Slider],
                        sliders_active_indices: list[int],
                        sliders_flipped_all: list[bool],
                        selected_indices: list[int]
                        ):

            Event.__init__(self, etype=MultiSlider.EventTypes.FLIPPING_ANIMATION_ENDED, data=None)

            self.sliders_active: list[Slider] = sliders_active
            """
            Reference to the sliders that were active in the selection process.
            """
            self.sliders_active_indices: list[int] = sliders_active_indices
            """
            Indices for the sliders that were active in the selection process.
            """
            self.sliders_flipped_all: list[bool] = sliders_flipped_all
            """
            If self.sliders_flipped_all[i] == True, it means self.sliders[i] flipped all cards.
            else False means only one was flipped. None means this slider was not active.
            """
            self.selected_indices: list[int] = selected_indices
            """
            All of the sliders selected indices.
            """

        @override
        def copy(self) -> MultiSlider.FlippingAnimationEndedEvent:
            return MultiSlider.FlippingAnimationEndedEvent(
                                                            sliders_active=self.sliders_active.copy(),
                                                            sliders_active_indices=self.sliders_active_indices.copy(),
                                                            sliders_flipped_all=self.sliders_flipped_all.copy(),
                                                            selected_indices=self.selected_indices.copy()
                                                            )

    class SlidingAnimationEndedEvent(Event):

        def __init__(
                        self,
                        sliders_active: list[Slider],
                        sliders_active_indices: list[int],
                        slide_directions: list[bool],
                        selected_indices: list[int]
                    ):

            Event.__init__(self, etype=MultiSlider.EventTypes.SLIDING_ANIMATION_ENDED, data=None)

            self.sliders_active: list[Slider] = sliders_active
            """
            Reference to the sliders that were active in the selection process.
            """
            self.sliders_active_indices: list[int] = sliders_active_indices
            """
            Indices for the sliders that were active in the selection process.
            """
            self.slide_directions: list[bool] = slide_directions
            """
            The slide directions. if self.slide_directions[i] == True,
            sliders_active[i] slided right, if it is False the slider slided left.
            """
            self.selected_indices: list[int] = selected_indices
            """
            All of the sliders selected indices.
            """

        @override
        def copy(self) -> MultiSlider.SlidingAnimationEndedEvent:
            return MultiSlider.SlidingAnimationEndedEvent(
                                                            sliders_active=self.sliders_active.copy(),
                                                            sliders_active_indices=self.sliders_active_indices.copy(),
                                                            slide_directions=self.slide_directions.copy(),
                                                            selected_indices=self.selected_indices.copy()
                                                            )


    def __init__(
                    self,
                    frame_dim: pygame.Rect,
                    #multi slider variables
                    sliders: list[Slider], #the sliders, in order
                    slider_percentages: list[float], #the percentages of space occupied by the sliders.
                    #slider variables
                    sliding_duration: float = 500,  # ms
                    select_animation_duration: float = 400,#ms
                    alphas: list[int] = None,
                    span: int = 1,
                    background_color: color_t = Colors.TRANSPARENT,
                    size_decrease_scale: float = 0.5,
                    horizontal: bool= True,
                    start_index: int = 0,
                    cutoff: bool = False,
                    max_slides: int = 2,
                    flip_duration: float = 400,#ms
                    slide_input_delay: float = 250#ms
                ):

        self.sliders: list[Slider] = sliders
        """
        The list of sliders.
        The sliders will be lined up from left to right
        according to the list order if self.horizontal == True,
        otherwise they will be lined up top down in list order.
        """
        self.slider_percentages: list[float] = slider_percentages
        """
        self.slider_percentages[i] defines self.width (if self.horizontal else self.height)
        of the self.sliders[i] relative to self.width (if self.horizontal else self.height).

        The slider percentage length should be len(self.sliders) + (len(self.sliders)-1),
        a divider after each percentage.
        """
        self._awaiting_list: list[bool] = None
        """
        The awaiting list is a list with length of self.sliders.
        If index i is False, it means we need to wait on slider i
        with the current action to stop.
        """
        self._assembled_events: Event = []
        """
        The list events currently being assembled.
        The leftmost element is pushed out when the time comes,
        events are added from the right.
        """

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

        #setting the enum
        self.frame_enum = FrameEnums.MULTI_SLIDER_WIDGET

        self._reset_awaiting_list()

    #==========================================
    # VALIDITY CHECK
    #==========================================

    def _validity_check(self) -> None:
        """
        Performs validity checks.
        """
        if len(self.slider_percentages) != len(self.sliders) * 2 - 1:
            raise RuntimeError("Slider Percentages list and Slider list have to be of equal length.")

        if not fequal(sum(self.slider_percentages), 1.0):
            raise RuntimeError("The Slider Percentages have to sum up to one.")

    #==========================================
    # OVERRIDING ABSTRACT METHODS
    #==========================================

    @override
    def create_surfaces(self) -> None:
        """
        Does nothing, the sliders will handle
        their surfaces by their own.
        """
        pass

    @override
    def create_back_surfaces(self) -> None:
        """
        Does nothing, the sliders will handle
        their back surfaces by their own.
        """
        pass

    #==========================================
    # RENDERING
    #==========================================

    @override
    def rerender(self) -> None:
        """
        Rerendering.
        Calculates the slider positions.
        """

        #validity check
        self._validity_check()
        #calculating dimensions
        relative_dimension: pygame.Rect = pygame.Rect(0, 0, self.width, self.height)
        #finding slider dimensions.
        slider_frame_dims: list[pygame.Rect] = None

        if self.horizontal:
            slider_frame_dims = graphics.split_rect_vertically(rect=relative_dimension, percentages=self.slider_percentages)
        else:
            slider_frame_dims = graphics.split_rect_horizontally(rect=relative_dimension, percentages=self.slider_percentages)

        #slider frame dims contains the dividing frames

        #assigning frame_dims, triggering rerendering
        for i in range(len(self.sliders)):
            self.sliders[i].frame_dim = slider_frame_dims[i*2] #skip dividing frames

        self.raise_prerender_flag()


    @override
    def prerender(self) -> None:
        """
        Prerendering.
        """
        self.surface.fill(self.background_color)
        #rendering the sliders
        for slider in self.sliders:
            slider.render(self.surface)

    #==========================================
    # GENERAL FUNCTIONS
    #==========================================

    def _reset_awaiting_list(self, indices: Sequence[int] = None):
        """
        Resets the awaiting list.
        Indices marks the indices of the sliders that need to be awaited.
        """

        if indices is None:
            indices = []

        self._awaiting_list = [True for i in range(len(self.sliders))]

        for index in indices:
            self._awaiting_list[index] = False

    def _awaiting_finished(self) -> bool:
        """
        If this is true, all sliders finished their actions.
        """
        return all(self._awaiting_list)

    #select, flip_card, flip_all_cards, slide_left and slide_right are assumed to apply to all sliders
    @override
    def select(self) -> bool:
        """
        Selects all slides.
        """
        return self.select_specific([i for i in range(len(self.sliders))])

    def select_specific(self, indices: list[int]) -> bool:
        """
        Selects specific sliders.
        Selects sliders[i] for i in indices.
        """
        if self.state == MultiSlider.SELECT_ANIMATION_PLAYING or self.select_animation_queued:
            return False
        else:
            #event
            assembled_event = MultiSlider.SelectAnimationEndedEvent(
                                                                    sliders_active=[self.sliders[i] for i in indices],
                                                                    sliders_active_indices=indices.copy(),
                                                                    selected_indices=[] #will be calculated just before pushing
                                                                    )
            self._assembled_events.append(assembled_event)

            self.select_animation_queued = True

            return True

    @override
    def flip_card(self) -> bool:
        """
        Selects all slides.
        """
        return self.flip_cards_specific(
                                            indices=[i for i in range(len(self.sliders))],
                                            flip_all=[False for i in range(len(self.sliders))]
                                        )

    @override
    def flip_all_cards(self) -> bool:
        """
        Selects all slides.
        """
        return self.flip_cards_specific(
                                            indices=[i for i in range(len(self.sliders))],
                                            flip_all=[True for i in range(len(self.sliders))]
                                        )

    def flip_cards_specific(
                                self,
                                indices: list[int],
                                flip_all: list[bool] = None
                            ) -> bool:
        """
        Selects specific sliders.
        Selects sliders[i] for i in indices.
        """
        if self.state == MultiSlider.FLIPPING_ANIMATION_PLAYING or self.flipping_animation_queued:
            return False
        else:
            #flip all
            if flip_all is None:
                flip_all = [False for i in range(len(indices))]

            flip_all_saved = [None for i in range(len(self.sliders))]
            for i in range(len(indices)):
                flip_all_saved[indices[i]] = flip_all[i]

            #event
            assembled_event = MultiSlider.FlippingAnimationEndedEvent(
                                                                        sliders_active=[self.sliders[i] for i in indices],
                                                                        sliders_active_indices=indices.copy(),
                                                                        sliders_flipped_all=flip_all_saved.copy(),
                                                                        selected_indices=[] #will be calculated just before pushing
                                                                        )
            self._assembled_events.push_event(assembled_event)

            self.flipping_animation_queued = True

            return True

    @override
    def slide_right(self) -> bool:
        """
        Slides all sliders right.
        """
        return self.slide_specific(
                                    indices=[i for i in range(len(self.sliders))],
                                    slide_directions=[True for i in range(len(self.sliders))]
                                    )

    @override
    def slide_left(self) -> bool:
        """
        Slides all sliders right.
        """
        return self.slide_specific(
                                    indices=[i for i in range(len(self.sliders))],
                                    slide_directions=[False for i in range(len(self.sliders))]
                                    )

    def slide_specific(
                        self,
                        indices: list[int],
                        slide_directions: list[bool]
                        ) -> bool:
        """
        Selects specific sliders.
        Selects sliders[i] for i in indices.
        """
        if self.state == MultiSlider.SLIDING or self.slides >= self.max_slides:
            return False
        else:
            #slide directions
            slide_directions_saved = [None for i in range(len(self.sliders))]

            for i in range(len(indices)):
                slide_directions_saved[indices[i]] = slide_directions[i]
            #event
            assembled_event = MultiSlider.SlidingAnimationEndedEvent(
                                                                        sliders_active=[self.sliders[i] for i in indices],
                                                                        sliders_active_indices=indices.copy(),
                                                                        slide_directions=slide_directions_saved.copy(),
                                                                        selected_indices=[] #will be calculated just before pushing
                                                                        )
            self._assembled_events.append(assembled_event)
            #self.slides takes on a different role.
            # > 0 -> slides queued
            # 0 -> no slides queued.
            self.slides += 1

            return True

    @override
    def get_selected_index(self) -> list[int]:
        """
        Returns a list of selected indices, where
        list[i] == self.sliders[i].get_selected_index()
        """
        return [slider.get_selected_index() for slider in self.sliders]

    @override
    def get_focus_index(self) -> list[int]:
        """
        Returns a list of selected indices, where
        list[i] == self.sliders[i].get_focus_index()
        """
        return [slider.get_focus_index() for slider in self.sliders]

    @override
    def set_background_color(self, color: color_t) -> None:
        """
        Sets the background uniformly
        """
        self.background_color = color

        for slider in self.sliders:
            slider.set_background_color(self.background_color)

        self.raise_prerender_flag()

    @override
    def is_rendered(self) -> bool:
        """
        No surfaces, returns False.
        """
        return False

    @override
    def initialize_slide_left(self) -> None:
        """
        Does nothing.
        """
        pass

    @override
    def render_slide_left(self) -> None:
        """
        Does nothing.
        """
        pass

    @override
    def finalize_slide_left(self) -> None:
        """
        Does nothing.
        """
        pass

    @override
    def initialize_slide_right(self) -> None:
        """
        Does nothing.
        """
        pass

    @override
    def render_slide_right(self) -> None:
        """
        Does nothing.
        """
        pass

    @override
    def finalize_slide_right(self) -> None:
        """
        Does nothing.
        """
        pass

    @override
    def render_select_animation(self) -> None:
        """
        Does nothing.
        """
        pass

    @override
    def render_flipping_animation(self) -> None:
        """
        Does nothing.
        """
        pass

    @override
    def render_flipping_all_animation(self) -> None:
        """
        Does nothing.
        """
        pass

    #==========================================
    # STATE FUNCTIONS
    #==========================================

    @override
    def sliding_animation_playing(self) -> bool:
        """
        Returns true if any sliding animation is playing
        """
        return (self.state == MultiSlider.SLIDING)


    #==========================================
    # TICK
    #==========================================

    @override
    def tick(self) -> Frame:
        """
        Slider tick method.
        """

        for slider in self.sliders:
            slider.tick()

        if self.state == MultiSlider.NOT_SLIDING:

            #check for events
            if len(self._assembled_events) > 0:
                #start new animation
                event_ref: Event = self._assembled_events[0]

                if event_ref.type == MultiSlider.EventTypes.SELECT_ANIMATION_ENDED:

                    #resetting await flags
                    self._reset_awaiting_list(indices=event_ref.sliders_active_indices)
                    #starting the select animation
                    for slider in event_ref.sliders_active:
                        slider.select()

                    self.state = MultiSlider.SELECT_ANIMATION_PLAYING

                    self.select_animation_queued = False

                elif event_ref.type == MultiSlider.EventTypes.FLIPPING_ANIMATION_ENDED:

                    #resetting await flags
                    self._reset_awaiting_list(indices=event_ref.sliders_active_indices)

                    for i in range(len(event_ref.sliders_flipped_all)):

                        flip_flag: bool = event_ref.sliders_flipped_all[i]

                        if flip_flag is not None:
                            if flip_flag:
                                self.sliders[i].flip_all_cards()
                            else:
                                self.sliders[i].flip_card()


                    self.state = MultiSlider.FLIPPING_ANIMATION_PLAYING

                    self.flipping_animation_queued = False

                elif event_ref.type == MultiSlider.EventTypes.SLIDING_ANIMATION_ENDED:

                    #resetting await flags
                    self._reset_awaiting_list(indices=event_ref.sliders_active_indices)

                    for i in range(len(event_ref.slide_directions)):

                        slide_dir: bool = event_ref.slide_directions[i]

                        if slide_dir is not None:
                            if slide_dir:
                                self.sliders[i].slide_right()
                            else:
                                self.sliders[i].slide_left()


                    self.state = MultiSlider.SLIDING

                    self.slides -= 1

        elif self.state == MultiSlider.SELECT_ANIMATION_PLAYING:

            if self._awaiting_finished():
                #select animation ended
                event_ref: MultiSlider.SelectAnimationEndedEvent = self._assembled_events[0]
                event_ref.selected_indices = self.get_selected_index()

                self.push_event(event_ref)
                self._assembled_events.pop(0)

                self.state = MultiSlider.NOT_SLIDING

        elif self.state == MultiSlider.FLIPPING_ANIMATION_PLAYING:

            if self._awaiting_finished():
                #flipping animation ended
                event_ref: MultiSlider.FlippingAnimationEndedEvent = self._assembled_events[0]
                event_ref.selected_indices = self.get_selected_index()

                self.push_event(event_ref)
                self._assembled_events.pop(0)

                self.state = MultiSlider.NOT_SLIDING

        elif self.state == MultiSlider.SLIDING:

            if self._awaiting_finished():
                #flipping animation ended
                event_ref: MultiSlider.SlidingAnimationEndedEvent = self._assembled_events[0]
                event_ref.selected_indices = self.get_selected_index()

                self.push_event(event_ref)
                self._assembled_events.pop(0)

                self.state = MultiSlider.NOT_SLIDING

        #polling events
        for i in range(len(self.sliders)):

            slider: Slider = self.sliders[i]

            for event in slider.poll_events():

                if event.type == Slider.EventTypes.SELECT_ANIMATION_ENDED:
                    #register the animation ended
                    self._awaiting_list[i] = True

                elif event.type == Slider.EventTypes.FLIPPING_ANIMATION_ENDED:
                    #register the animation ended
                    self._awaiting_list[i] = True

                elif event.type == Slider.EventTypes.SLIDING_ANIMATION_ENDED:
                    #register the animation ended
                    self._awaiting_list[i] = True

        if (self.state != MultiSlider.NOT_SLIDING):
            self.raise_prerender_flag()

        if self.prerender_flag_raised():
            self.prerender()
            self.reset_prerender_flag()

        return self
