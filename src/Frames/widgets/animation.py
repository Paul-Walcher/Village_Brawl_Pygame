from __future__ import annotations
from typing import Type, Any, Callable, override

import pygame

from clock import Clock
from enum import Enum, auto
from event_queue_manager import Event

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums


class Animation(Frame):
    """
    Animation class.
    Provides a functional animation.
    """

    LOOP_INFINITE: int = -1 #variable for infinite looping
    DEFAULT_BLIT_DURATION: float = 500#ms, default blit duration

    class EventTypes(Enum):
        """
        The events of the animation.
        """
        ANIMATION_STARTED = auto()
        ANIMATION_RESTARTED = auto()
        ANIMATION_ENDED = auto()
        ANIMATION_PAUSED = auto()
        ANIMATION_LOOPED = auto()

    class AnimationStartedEvent(Event):
        """
        Animation started event is called when a new animation is started from ground up.
        """
        def __init__(self, animation_ref: Animation) -> None:

            Event.__init__(self, etype=Animation.EventTypes.ANIMATION_STARTED, data=None)
            self.animation_ref: Animation = animation_ref

        @override
        def copy(self) -> Animation.AnimationStartedEvent:
            return Animation.AnimationStartedEvent(animation_ref=self.animation_ref)


    class AnimationRestartedEvent(Event):
        """
        Animation restarted event is called when the animation is unpaused.
        """
        def __init__(self, animation_ref: Animation) -> None:

            Event.__init__(self, etype=Animation.EventTypes.ANIMATION_RESTARTED, data=None)
            self.animation_ref: Animation = animation_ref

        @override
        def copy(self) -> Animation.AnimationRestartedEvent:
            return Animation.AnimationRestartedEvent(animation_ref=self.animation_ref)

    class AnimationEndedEvent(Event):
        """
        Animation ended event gets pushed if the animation and all loops ended.
        """
        def __init__(self, animation_ref: Animation) -> None:

            Event.__init__(self, etype=Animation.EventTypes.ANIMATION_ENDED, data=None)
            self.animation_ref: Animation = animation_ref

        @override
        def copy(self) -> Animation.AnimationEndedEvent:
            return Animation.AnimationEndedEvent(animation_ref=self.animation_ref)

    class AnimationPausedEvent(Event):
        """
        Animation paused event is created when the animation is paused.
        """
        def __init__(self, animation_ref: Animation) -> None:

            Event.__init__(self, etype=Animation.EventTypes.ANIMATION_PAUSED, data=None)
            self.animation_ref: Animation = animation_ref

        @override
        def copy(self) -> Animation.AnimationPausedEvent:
            return Animation.AnimationPausedEvent(animation_ref=self.animation_ref)

    class AnimationLoopedEvent(Event):
        """
        Animation looped event is called when one loop is finished
        """
        def __init__(self, animation_ref: Animation) -> None:

            Event.__init__(self, etype=Animation.EventTypes.ANIMATION_LOOPED, data=None)
            self.animation_ref: Animation = animation_ref

        @override
        def copy(self) -> Animation.AnimationLoopedEvent:
            return Animation.AnimationLoopedEvent(animation_ref=self.animation_ref)

    def __init__(
                    self,
                    frame_dim: pygame.Rect,
                    surfaces: list[pygame.Surface], #the list of surfaces.
                    surface_blit_durations: list[float] = None, #list of durations each surface will be shown.
                    parent_frame: Frame = None,
                    scale_function: Callable[[pygame.Surface, tuple[int, int]], pygame.Surface] = pygame.transform.smoothscale
                    ):

        Frame.__init__(
                        self,
                        frame_enum=FrameEnums.ANIMATION_WIDGET,
                        data=None,
                        frame_dim=frame_dim,
                        parent_frame=parent_frame,
                        focus_group=None
                        )

        #storing the surfaces and surface blit durations
        self.surfaces: list[pygame.Surface] = surfaces
        """
        The given surfaces.
        """
        self.surface_blit_durations: list[float] = surface_blit_durations
        """
        The durations each surface is blit.
        self.surfaces[i] will be shown for self.surface_blit_durations[i] ms.
        """
        self.surface_blit_durations_accumulated: list[float] = None
        """
        The surface blit durations accumulated, for the clock.
        """
        self.scale_function: Callable[[pygame.Surface, tuple[int, int]], pygame.Surface] = scale_function
        """
        Function to scale up the surfaces self.frame_dim.
        """
        self.surface_index: int = 0
        """
        The index of the current surface shown.
        """
        self.animation_clock: Clock = Clock()
        """
        The clock used for animation.
        """
        self.looping_index: int = 0
        """
        How many times the animation has looped.
        """
        self.n_loops: int = 0
        """
        How many times the animation should loop.
        """
        self.shift: int = 0
        """
        If the animation is shifted by x, it starts at surface x and ends at len(self.surfaces) + x
        """
        self.elapsed_time: float = 0
        """
        How much time elapsed in the animation when pausing.
        """
        self.is_paused: bool = True
        """
        If the animation is paused or not.
        """
        self.animation_finished: bool = False
        """
        If the animation finished, it needs to be started anew
        """
        #checking if the surface blit durations have enough

        if self.surface_blit_durations is None:
            self.surface_blit_durations = [Animation.DEFAULT_BLIT_DURATION for i in range(len(self.surfaces))]

        self._check_surface_blit_durations()

    def _check_surface_blit_durations(self) -> None:
        """
        Checks if the surface blit durations are appropriate.
        """
        if len(self.surfaces) != len(self.surface_blit_durations):
            raise RuntimeError("The surfaces have to be the same length as the surface_blit_durations!")

    def _initialize_animation(
                                self,
                                starting_index: int = 0, #index of the surface to start
                                shift: int = 0, #shift of the animation
                                n_loops: int = 1, #how many times the animation loops
                                new_surface_blit_durations: list[float] = None #the new surface_blit_durations
                                ) -> None:
        """
        Initializes all variables before an animation.
        """
        self.surface_index = starting_index + shift
        self.shift = shift
        self.n_loops = n_loops
        self.elapsed_time = 0

        self.looping_index = 0

        if new_surface_blit_durations is not None:
            self.surface_blit_durations = new_surface_blit_durations
            self._check_surface_blit_durations()

        #calculating the accumulated blit durations
        self.surface_blit_durations_accumulated = [self.surface_blit_durations[shift]]
        for i in range(shift+1, len(self.surface_blit_durations) + shift):
            self.surface_blit_durations_accumulated.append(self.surface_blit_durations_accumulated[(i-1) % len(self.surface_blit_durations)]\
                                                            + self.surface_blit_durations[i % len(self.surface_blit_durations)])
        #now scaling the surfaces
        for i in range(len(self.surfaces)):

            surf: pygame.Surface = self.surfaces[i]

            if (surf.get_width() != self.width or surf.get_height() != self.height):
                surf = self.scale_function(surf, (self.width, self.height))
                self.surfaces[i] = surf

        self.animation_finished = False


    def start_animation(
                        self,
                        starting_index: int = -1,
                        shift: int = -1,
                        n_loops: int = -1,
                        new_surface_blit_durations: list[float] = None
                        ) -> None:
        """
        Starts the animation back up if it was paused.
        If any of the parameters is not a default parameter, a new animation will be started
        """
        if (starting_index != -1\
            or shift != -1\
            or n_loops != -1\
            or new_surface_blit_durations is not None
            ):

            starting_index = (starting_index if starting_index != -1 else 0)
            shift = (shift if shift != -1 else 0)
            n_loops = (n_loops if n_loops != -1 else 1)

            self._initialize_animation(
                                        starting_index=starting_index,
                                        shift=shift,
                                        n_loops=n_loops,
                                        new_surface_blit_durations=new_surface_blit_durations
                                        )

            self.push_event(Animation.AnimationStartedEvent(self))

        else:

            self.push_event(Animation.AnimationRestartedEvent(self))

        self.is_paused = False
        self.animation_clock.start()

    def reset_animation(self) -> None:
        """
        Resets and pauses the animation.
        """
        self.is_paused = True
        self.elapsed_time = 0
        self.looping_index = 0
        self.surface_index = self.shift
        self.animation_finished = False
        #creates a pause event
        self.push_event(Animation.AnimationPausedEvent(self))

    def pause_animation(self) -> None:
        """
        Pauses the animation.
        """
        self.is_paused = True
        self.elapsed_time = self.animation_clock.elapsed()
        self.push_event(Animation.AnimationPausedEvent(self))

    def is_paused(self) -> bool:
        """
        Returns if the animation is paused or not.
        """
        return self.is_paused

    def time_elapsed(self) -> float:
        """
        Returns the elapsed time since the last animation was started.
        """
        return (self.elapsed_time + self.looping_index * sum(self.surface_blit_durations))

    def get_loops(self) -> tuple[int, int]:
        """
        Returns a tuple of (self.looping_index, self.n_loops),
        if this animation is active or paused, else None
        """
        if self.animation_finished:
            return None
        else:
            return (self.looping_index, self.n_loops)

    def get_surface_blit_durations(self) -> list[float]:
        """
        Returns a copy of the surface blit durations.
        """
        return self.surface_blit_durations.copy()

    def get_surface_copies(self) -> list[pygame.Surface]:
        """
        Returns a list of surface copies.
        """
        return [surf.copy() for surf in self.surfaces]

    def get_surfaces(self) -> list[pygame.Surface]:
        """
        Returns a reference to the surface list for this animation.
        """
        return self.surfaces

    @override
    def tick(self) -> None:
        """
        The tick function.
        """

        #renders the tick function
        if not self.is_paused and not self.animation_finished:

            #rendering
            self.elapsed_time = self.animation_clock.elapsed()

            if self.elapsed_time >= self.surface_blit_durations_accumulated[self.surface_index]:
                #next surface is the target
                self.surface_index += 1
                self.surface_index %= len(self.surfaces)

                if self.surface_index == self.shift:
                    #new animation, or stopping

                    if self.looping_index < (self.n_loops-1):
                        self.looping_index += 1
                        self.elapsed_time = 0
                        self.push_event(Animation.AnimationLoopedEvent(self))
                        self.animation_clock.start()
                    else:
                        #stop the animation
                        self.is_paused = True
                        self.animation_finished = True
                        self.push_event(Animation.AnimationEndedEvent(self))

    @override
    def render(self, screen: pygame.Surface) -> None:
        """
        Rendering.
        """
        screen.blit(self.surfaces[self.surface_index], (self.x, self.y))
