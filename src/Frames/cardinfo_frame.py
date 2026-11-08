from __future__ import annotations
from typing import Type, Callable, Any, override

import pygame

import graphics
from constants import Colors, Alpha, Fonts, Fontsizes, KeyAlternatives, point_t, R_ID, as_point
from clock import Clock
from event_queue_manager import Event
from enum import Enum, auto
from templates.renderable_cardinfo import Renderable_CardInfo

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.textbox import Textbox
from Frames.widgets.text_input import TextInput


class CardinfoFrame(Frame):
    """
    General frame to display cardinfo.
    """
    #the states
    SLIDING_IN: int = R_ID()
    SLIDING_OUT: int = R_ID()
    NOTHING_FOCUSED: int = R_ID()
    TEXTBOX_FOCUSED: int = R_ID()

    #constants
    LEFT_SIDE: bool = False
    RIGHT_SIDE: bool = True

    class EventTypes(Enum):

        SLIDING_IN_FINISHED = auto()
        SLIDING_OUT_FINISHED = auto()

    class SlidingInFinishedEvent(Event):

        def __init__(self, frame_ref: Frame, startpos: point_t, endpos: point_t):

            Event.__init__(self, etype=CardinfoFrame.EventTypes.SLIDING_IN_FINISHED, data=None)

            self.frame_ref: Frame = frame_ref
            self.startpos: point_t = startpos #where the slide started
            self.endpos: point_t = endpos #where the slide finished

        @override
        def copy(self) -> CardinfoFrame.SlidingInFinishedEvent:

            return CardinfoFrame.SlidingInFinishedEvent(self.frame_ref, self.startpos, self.endpos)

    class SlidingOutFinishedEvent(Event):

        def __init__(self, frame_ref: Frame, startpos: point_t, endpos: point_t):

            Event.__init__(self, etype=CardinfoFrame.EventTypes.SLIDING_OUT_FINISHED, data=None)

            self.frame_ref: Frame = frame_ref
            self.startpos: point_t = startpos #where the slide started
            self.endpos: point_t = endpos #where the slide finished

        @override
        def copy(self) -> CardinfoFrame.SlidingOutFinishedEvent:

            return CardinfoFrame.SlidingOutFinishedEvent(self.frame_ref, self.startpos, self.endpos)

    def __init__(
                self,
                data: Any = None,
                frame_dim: pygame.Rect = None,
                parent_frame: Frame = None,
                focus_group: str = "",
                has_focus: bool = True,
                cardinfo: Renderable_CardInfo,
                info_width_percentage: float = 0.5,
                shown_side=CardinfoFrame.RIGHT_SIDE,
                font: pygame.font.Font = Fonts.STANDARD_FONT,
                alpha: int = 200, #the alpha value
                hmargin: float = 0.1,
                vmargin: float = 0.1,
                chars_per_line: int = 50,
                lines_per_page: int = 5,
                slide_duration: float = 400,
                start_position: point_t = None,
                end_position: point_t = None
                ):

        Frame.__init__(
                            self,
                            frame_enum=FrameEnums.CARDINFO_FRAME,
                            data=data,
                            frame_dim=frame_dim,
                            parent_frame=parent_frame,
                            focus_group=focus_group,
                            has_focus=has_focus
                            )

        self.slide_endpos: point_t = end_position
        """
        The endpos when sliding in.
        """
        self.slide_startpos: point_t = start_position
        """
        The startpos when sliding in.
        """
        self.slide_duration: float = slide_duration
        """
        Duration of the slide.
        """
        self.cardinfo: Renderable_CardInfo = cardinfo
        """
        The cardinfo given.
        """
        self.info_width_percentage: float = info_width_percentage
        """
        How much of the width if used by the info frame. The rest is transparent.
        """
        self.shown_side: bool = shown_side
        """
        On which side the info will be shown. The rest is transparent.
        """
        self.font: pygame.font.Font = font
        """
        The font for rendering the info.
        """
        self.alpha: int = alpha
        """
        Alpha value of the info page frame.
        """
        self.hmargin: float = hmargin
        """
        Horizontal margin for the whole frame.
        """
        self.vmargin: float = vmargin
        """
        The vertical margin for the whole frame.
        """
        self.chars_per_line: int = chars_per_line
        """
        Chars per line for the textbox.
        """
        self.lines_per_page: int = lines_per_page
        """
        Lines per page for the textbox.
        """
        self.full_image_shown: bool = False
        """
        If the full image is currently shown or not.
        """
        self.slide_duration: float = slide_duration
        """
        The slide duration
        """
        self.slide_clock: Clock = Clock()
        """
        The sliding clock.
        """
        self.intro_delay: float = 100#ms
        """
        The intro delay.
        """
        self.intro_clock: Clock = Clock()
        """
        Clock for enforcing intro delay.
        """
        #Render Parts
        self.page_parts: Renderable_CardInfo.InfoPagePartContainer = None
        """
        Reference to the page parts to render.
        """
        self.description_textbox: Textbox = None
        """
        Reference to the description textbox.
        """
        self.info_frame_dim: pygame.Rect = None
        """
        The actual frame dim of the info page.
        """
        self.inner_frame_dim: pygame.Rect = None
        """
        The frame dimension, after applying the margins.
        """
        self.relative_inner_frame_dim: pygame.Rect = None
        """
        Inner frame dim relative to self.info_frame_dim
        """
        self.info_page_surface: pygame.Surface = None
        """
        The info page surface.
        """
        self.state = CardinfoFrame.NOTHING_FOCUSED


        self.rerender()

    @override
    def rerender(self):
        """
        Rerendering.
        """
        sx: int = -1 #starting x
        sy: int = -1 #starting y

        if self.slide_startpos is not None:

            sx, sy = self.slide_startpos

        else:

            #we calculate the slide startpos
            sx = (self.x-self.width if self.shown_side == CardinfoFrame.LEFT_SIDE else self.x + self.width)
            sy = self.y

            self.slide_startpos = pygame.Rect(sx, sy, self.width, self.height)

        #calculating endpos
        if self.slide_endpos is None:
            #creating the generic end position.
            self.slide_endpos = self.frame_dim.copy()

        #setting position to the starting position
        self.x = sx
        self.y = sy

        #recalculates inner frame dimensions
        self.recalculate_inner_frame_dims()

        #since this is relative x, y changes do not matter
        self.relative_inner_frame_dim = graphics.apply_margins(pygame.Rect(0, 0, self.info_frame_dim.width, self.info_frame_dim.height), self.hmargin, self.vmargin)

        #creating the info page surface
        self.info_page_surface = pygame.Surface((self.info_frame_dim.width, self.info_frame_dim.height))


        self.page_parts = self.cardinfo.get_info_page_parts(
                                                                self.relative_inner_frame_dim,
                                                                font=self.font,
                                                                hmargin=0.0,
                                                                vmargin=0.0,
                                                                chars_per_line=self.chars_per_line,
                                                                lines_per_page=self.lines_per_page
                                                                )
        #setting the reference
        self.description_textbox = self.page_parts.textbox

        self.intro_delay_clock.start()

    @override
    def prerender(self):

        self.surface.fill(Colors.TRANSPARENT)
        self.info_page_surface.fill((*Colors.BLACK, self.alpha))

        self.cardinfo.render_info_page_parts(
                                            self.info_page_surface,
                                            self.page_parts,
                                            full_image_shown=self.full_image_shown
                                            )

        self.surface.blit(self.info_page_surface, (self.info_frame_dim.x, self.info_frame_dim.y))

    def recalculate_inner_frame_dims(self) -> None:
        """
        recalculates the inner frame dims
        """
        #getting the width
        info_page_width: int = int(self.width * self.info_width_percentage)
        #now creating the split and inner frame
        self.info_frame_dim = pygame.Rect(
                                            (self.x if self.shown_side == CardinfoFrame.LEFT_SIDE else self.x + self.width - info_page_width),
                                            self.y,
                                            info_page_width,
                                            self.height
                                            )
        #creating the inner frame dim
        self.inner_frame_dim = graphics.apply_margins(self.info_frame_dim, self.hmargin, self.vmargin)

    @override
    def bind_events(self):

        if self.is_focused():

            for key in [pygame.K_RIGHT, KeyAlternatives.RIGHT_ALTERNATIVE]:
                cb = self.add_pygame_key_callback(key, None,  False, self.right_pressed)

            for key in [pygame.K_LEFT, KeyAlternatives.LEFT_ALTERNATIVE]:
                cb = self.add_pygame_key_callback(key, None,  False, self.left_pressed)

            cb_kd = self.add_pygame_event_callback(pygame.KEYDOWN, None, False, self.alt_down)
            cb_ku = self.add_pygame_event_callback(pygame.KEYUP, None, False, self.alt_up)


    def right_pressed(self, event, data):
        """
        Shows the next page.
        """

        if self.state == CardinfoFrame.TEXTBOX_FOCUSED:
            self.description_textbox.next_page()
            self.raise_prerender_flag()
        elif self.state == CardinfoFrame.NOTHING_FOCUSED:
            self.state = CardinfoFrame.TEXTBOX_FOCUSED
            self.raise_prerender_flag()

    def left_pressed(self, event, data):
        """
        Shows the prev page.
        """
        if self.state == CardinfoFrame.TEXTBOX_FOCUSED:
            self.description_textbox.prev_page()
            self.raise_prerender_flag()
        elif self.state == CardinfoFrame.NOTHING_FOCUSED:
            self.state = CardinfoFrame.TEXTBOX_FOCUSED
            self.raise_prerender_flag()

    def alt_down(self, event, data):
        """
        Shows the full image.
        """

        if event.key != KeyAlternatives.SHOW_IMAGE_KEY:
            return Frame.EventCallback.FAILURE

        if not self.full_image_shown:
            self.raise_prerender_flag()

        self.full_image_shown = True

    def alt_up(self, event, data):
        """
        Stops showing the full image.
        """

        if event.key != KeyAlternatives.SHOW_IMAGE_KEY:
            return Frame.EventCallback.FAILURE

        if self.full_image_shown:
            self.raise_prerender_flag()

        self.full_image_shown = False

    def at_endpos(self) -> bool:
        """
        Returns a boolean that indicates whether this frame is at its endpos (after sliding in).
        """
        return (as_point(self.frame_dim) == self.slide_endpos)

    def at_startpos(self) -> bool:
        """
        Returns a boolean that indicates whether this frame is at its
        startpos (either after initialization or sliding out.)
        """
        return (as_point(self.frame_dim) == self.slide_startpos)

    def is_sliding(self) -> bool:
        """
        Returns whether this frame is sliding or not.
        """
        return (self.state in [CardinfoFrame.SLIDING_IN, CardinfoFrame.SLIDING_OUT])

    def start_sliding_in(self) -> bool:
        """
        Starts sliding in.
        If the frame is already at its endpos, this returns false.
        """

        if self.at_endpos():
            return False

        #otherwise, start sliding
        self.state = CardinfoFrame.SLIDING_IN

        self.raise_prerender_flag()
        self.slide_clock.start()

    def slide_in(self) -> None:
        """
        Calculates the sliding.
        """

        percentage: float = self.slide_clock.elapsed() / self.slide_duration

        if percentage >= 1.0:
            self.finalize_sliding_in()
        else:

            x_inc: int = int((self.slide_endpos[0] - self.slide_startpos[0]) * percentage) #the increase in x
            y_inc: int = int((self.slide_endpos[1] - self.slide_startpos[1]) * percentage) #the increase in y

            self.x = self.slide_startpos[0] + x_inc
            self.y = self.slide_startpos[1] + y_inc

            self.recalculate_inner_frame_dims()

    def finalize_sliding_in(self) -> None:
        """
        Ends the sliding in animation.
        """

        self.state = CardinfoFrame.NOTHING_FOCUSED

        self.x = self.slide_endpos[0]
        self.y = self.slide_endpos[1]

        self.recalculate_inner_frame_dims()

        self.raise_prerender_flag()

    def start_sliding_out(self) -> bool:
        """
        Starts sliding in.
        If the frame is already at its endpos, this returns false.
        """

        if self.at_startpos():
            return False

        #otherwise, start sliding
        self.state = CardinfoFrame.SLIDING_OUT

        self.raise_prerender_flag()
        self.slide_clock.start()

    def slide_out(self) -> None:
        """
        Calculates the sliding.
        """

        percentage: float = self.slide_clock.elapsed() / self.slide_duration

        if percentage >= 1.0:
            self.finalize_sliding_out()
        else:

            x_inc: int = int((self.slide_endpos[0] - self.slide_startpos[0]) * (1.0 - percentage)) #the increase in x
            y_inc: int = int((self.slide_endpos[1] - self.slide_startpos[1]) * (1.0 - percentage)) #the increase in y

            self.x = self.slide_startpos[0] + x_inc
            self.y = self.slide_startpos[1] + y_inc

            self.recalculate_inner_frame_dims()

    def finalize_sliding_out(self) -> None:
        """
        Ends the sliding out animation.
        """

        self.state = CardinfoFrame.NOTHING_FOCUSED

        self.x = self.slide_startpos[0]
        self.y = self.slide_endpos[1]

        self.recalculate_inner_frame_dims()

        self.raise_prerender_flag()

    @override
    def tick(self):

        if self.intro_delay_clock.elapsed() >= self.intro_delay:
            self.manage_pygame_events()

        if self.exit_flag_raised():
            return self._next_frame

        self.description_textbox.tick()

        if self.state == CardinfoFrame.SLIDING_IN:
            self.slide_in()
        elif self.state == CardinfoFrame.SLIDING_OUT:
            self.slide_out()

        if self.prerender_flag_raised():
            self.prerender()

        return self
