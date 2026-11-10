from __future__ import annotations
from typing import Type, Callable, Any, override

import pygame

import graphics
import calculations
from constants import Colors, Alpha, Fonts, Fontsizes, KeyAlternatives, point_t, R_ID, as_point, color_t, Mouse
from clock import Clock
from event_queue_manager import Event
from enum import Enum, auto
from templates.renderable_cardinfo import Renderable_CardInfo

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.textbox import Textbox
from Frames.widgets.text_input import TextInput

from context_data import ContextData


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
                cardinfo: Renderable_CardInfo,
                frame_dim: pygame.Rect,
                data: Any = None,
                parent_frame: Frame = None,
                focus_group: str = "",
                has_focus: bool = True,
                info_width_percentage: float = 0.5,
                shown_side=None,
                font: pygame.font.Font = Fonts.STANDARD_FONT,
                alpha: int = 170, #the alpha value
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
        self.shown_side: bool = (shown_side if shown_side is not None else CardinfoFrame.RIGHT_SIDE)
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
        self.intro_delay_clock: Clock = Clock()
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
        """
        The state of this frame.
        """
        self.textbox_outline_size_p: float = 0.05
        """
        Outline for the textbox
        """
        self.textbox_outline_size: int = None
        """
        The textbox outline size, relative to self.inner_frame
        """
        self.textbox_outline_color: color_t = Colors.WHITE
        """
        The textbox outline color
        """


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

        #creating the info page surface
        self.info_page_surface = pygame.Surface((self.info_frame_dim.width, self.info_frame_dim.height), pygame.SRCALPHA)

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

        self.textbox_outline_size = int(min(self.info_frame_dim.width, self.info_frame_dim.height) * self.textbox_outline_size_p)
        self.description_textbox.set_outline_size(0)
        self.description_textbox.set_outline_color(self.textbox_outline_color)

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
        #since this is relative x, y changes do not matter
        self.relative_inner_frame_dim = graphics.position_relative(anchor_rect=self.info_frame_dim, make_relative_rect=self.inner_frame_dim)

    @override
    def bind_events(self):

        if self.is_focused():

            for key in [pygame.K_RIGHT, KeyAlternatives.RIGHT_ALTERNATIVE]:
                cb = self.add_pygame_key_callback(key, None,  False, self.right_pressed)

            for key in [pygame.K_LEFT, KeyAlternatives.LEFT_ALTERNATIVE]:
                cb = self.add_pygame_key_callback(key, None,  False, self.left_pressed)

            self.add_pygame_key_callback(key=pygame.K_ESCAPE, data=None, putback=False, func=self.esc_pressed)
            self.add_pygame_key_callback(key=KeyAlternatives.BACK_KEY, data=None, putback=False, func=self.esc_pressed)

            cb_kd = self.add_pygame_event_callback(pygame.KEYDOWN, None, False, self.keydown)
            cb_ku = self.add_pygame_event_callback(pygame.KEYUP, None, False, self.keyup)

            if type(self.data) == ContextData:
                if self.data.mouse_enabled:

                    self.add_pygame_event_callback(etype=pygame.MOUSEMOTION, data=None, putback=False, func=self.mouse_motion)
                    self.add_pygame_event_callback(etype=pygame.MOUSEBUTTONDOWN, data=None, putback=False, func=self.mouse_button_down)
                    self.add_pygame_event_callback(etype=pygame.MOUSEWHEEL, data=None, putback=False, func=self.mouse_wheel)
                    self.add_pygame_event_callback(etype=pygame.MOUSEBUTTONUP, data=None, putback=False, func=self.mouse_button_up)


    def mouse_motion(self, event: pygame.event.Event, data: Any) -> None:
        """
        Focuses on the textbox if hovering.
        """
        if self.state in [CardinfoFrame.SLIDING_IN, CardinfoFrame.SLIDING_OUT]:
            return

        mpos: point_t = graphics.position_relative_point(anchor_point=as_point(self.inner_frame_dim), make_relative_point=event.pos)

        if self.state == CardinfoFrame.NOTHING_FOCUSED:

            if calculations.point_collides(mpos, self.description_textbox.frame_dim):

                self.state = CardinfoFrame.TEXTBOX_FOCUSED
                self.description_textbox.set_outline_size(self.textbox_outline_size_p)

        elif self.state == CardinfoFrame.TEXTBOX_FOCUSED:

            if not calculations.point_collides(mpos, self.description_textbox.frame_dim):

                self.state = CardinfoFrame.NOTHING_FOCUSED
                self.description_textbox.set_outline_size(0)

    def mouse_button_down(self, event: pygame.event.Event, data: Any) -> None:
        """
        On mouse button down.
        """

        if self.state in [CardinfoFrame.SLIDING_IN, CardinfoFrame.SLIDING_OUT]:
            return

        left_tbox: pygame.Rect = None
        right_tbox: pygame.Rect = None

        left_tbox, right_tbox = graphics.split_rect_horizontally(rect=self.description_textbox.frame_dim, percentages=[0.5, 0.5])

        mpos: point_t = graphics.position_relative_point(anchor_point=as_point(self.inner_frame_dim), make_relative_point=event.pos)

        if event.button == Mouse.LEFT_BUTTON:

            if calculations.point_collides(mpos, left_tbox):

                self.description_textbox.prev_page()
                self.raise_prerender_flag()

            elif calculations.point_collides(mpos, right_tbox):

                self.description_textbox.next_page()
                self.raise_prerender_flag()

        elif event.button == Mouse.WHEEL:

            self.full_image_shown = True
            self.raise_prerender_flag()

        elif event.button == Mouse.RIGHT_BUTTON:

            if self._next_frame is None:
                self._next_frame = self.parent_frame

            self.raise_exit_flag()

    def mouse_button_up(self, event: pygame.event.Event, data: Any) -> None:
        """
        Mouse button up.
        """
        if self.state in [CardinfoFrame.SLIDING_IN, CardinfoFrame.SLIDING_OUT]:
            return

        if event.button == Mouse.WHEEL:

            self.full_image_shown = False
            self.raise_prerender_flag()


    def mouse_wheel(self, event: pygame.event.Event, data: Any) -> None:
        """
        Can turn pages from anywhere.
        """
        if self.state in [CardinfoFrame.SLIDING_IN, CardinfoFrame.SLIDING_OUT]:
            return

        if event.precise_y < -0.5:

            self.description_textbox.next_page()
            self.raise_prerender_flag()
            self.intro_delay_clock.start()

        elif event.precise_y > 0.5:

            self.description_textbox.prev_page()
            self.raise_prerender_flag()
            self.intro_delay_clock.start()

    def right_pressed(self, event, data):
        """
        Shows the next page.
        """

        if self.state == CardinfoFrame.TEXTBOX_FOCUSED:
            self.description_textbox.next_page()
            self.raise_prerender_flag()
        elif self.state == CardinfoFrame.NOTHING_FOCUSED:
            self.state = CardinfoFrame.TEXTBOX_FOCUSED
            self.description_textbox.set_outline_size(self.textbox_outline_size_p)
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
            self.description_textbox.set_outline_size(self.textbox_outline_size_p)
            self.raise_prerender_flag()

    def keydown(self, event, data):
        """
        Shows the full image.
        """

        if event.key == KeyAlternatives.SHOW_IMAGE_KEY:

            if not self.full_image_shown:
                self.raise_prerender_flag()

            self.full_image_shown = True

    def keyup(self, event, data):
        """
        Stops showing the full image.
        """

        if event.key == KeyAlternatives.SHOW_IMAGE_KEY:

            if self.full_image_shown:
                self.raise_prerender_flag()

            self.full_image_shown = False

    def esc_pressed(self, event, data):
        """
        Exits the frame, or the textbox.
        """
        if self.state == CardinfoFrame.TEXTBOX_FOCUSED:
            self.description_textbox.set_outline_size(0)
            self.state = CardinfoFrame.NOTHING_FOCUSED
        elif self.state == CardinfoFrame.NOTHING_FOCUSED:
            self._next_frame = self.parent_frame #might be none
            self.raise_exit_flag()


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
        self.intro_delay_clock.start()

        return True

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
            self.raise_prerender_flag()

    def finalize_sliding_in(self) -> None:
        """
        Ends the sliding in animation.
        """

        self.state = CardinfoFrame.NOTHING_FOCUSED

        self.x = self.slide_endpos[0]
        self.y = self.slide_endpos[1]

        self.recalculate_inner_frame_dims()

        self.push_event(CardinfoFrame.SlidingInFinishedEvent(self, self.slide_startpos, self.slide_endpos))

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
        self.intro_delay_clock.start()

        return True

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

            self.raise_prerender_flag()

    def finalize_sliding_out(self) -> None:
        """
        Ends the sliding out animation.
        """

        self.state = CardinfoFrame.NOTHING_FOCUSED

        self.x = self.slide_endpos[0]
        self.y = self.slide_endpos[1]

        self.recalculate_inner_frame_dims()

        self.push_event(CardinfoFrame.SlidingOutFinishedEvent(self, self.slide_endpos, self.slide_startpos))

        self.raise_prerender_flag()
        self.intro_delay_clock.start()

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
            self.reset_prerender_flag()

        return self
