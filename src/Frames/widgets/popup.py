"""
Notification Widget.
"""
from __future__ import annotations
from typing import Any, Callable, Type, override

import pygame

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums

import graphics
from graphics import (
                        page_t,
                        colored_page_t,
                        surface_with_position_t,
                        rendered_surface_position_tuples_t,
                        EMPTY_COLORED_PAGE
                        )

import constants
from constants import (
                        fequal,
                        Colors,
                        Fonts,
                        KeyAlternatives,
                        color_t,
                        point_t,
                        id_t,
                        R_ID,
                        FULLSCREEN
                        )

from clock import Clock
from event_queue_manager import Event

class Popup(Frame):
    """
    This class provides a popup widget.
    There can be a notification, or
    there can be option to choose from.
    """

    class Option:
        """
        Option class, contains
        all variables necessary for the options.
        """
        def __init__(
                        self,
                        option_text: colored_page_t = None,
                        highlighted_option_text: colored_page_t = None,

                        background_color: color_t = Colors.BLACK,
                        highlighted_background_color: color_t = Colors.CYAN,

                        option_hmargin: float = 0.1,
                        option_vmargin: float = 0.05,

                        highlighted_option_hmargin: float = 0.05,
                        highlighted_option_vmargin: float = 0.025,

                        outline_size_p: float = 0.05,
                        outline_color: color_t = Colors.WHITE

                    ):

            self.option_text: colored_page_t = option_text
            """
            The option text.
            """

            if self.option_text is None:
                self.option_text = EMPTY_COLORED_PAGE()

            self.highlighted_option_text: colored_page_t = highlighted_option_text
            """
            The highlighted option text
            """

            if self.highlighted_option_text is None:
                self.highlighted_option_text = graphics.copy_colored_page(option_text)

            self.background_color: color_t = background_color
            """
            The background color for the unhighlighted state.
            """
            self.highlighted_background_color: color_t = highlighted_background_color
            """
            The background for the highlighted state.
            """

            self.option_hmargin: float = option_hmargin
            """
            Horizontal margin of the unselected state.
            """
            self.option_vmargin: float = option_vmargin
            """
            Vertical margin of the unselected state.
            """
            self.highlighted_option_hmargin: float = highlighted_option_hmargin
            """
            Horizontal margin of the highlighted state.
            """
            self.highlighted_option_vmargin: float = highlighted_option_vmargin
            """
            Vertical margin of the highlighted state.
            """

            self.outline_size_p: float = outline_size_p
            """
            The outline size relative to min(width, height) of this option.
            """
            self.outline_color: color_t = outline_color
            """
            The color of the outline.
            """

    #events
    class EventTypes:

        NEW_OPTION_FOCUSED: id_t = R_ID() #when the option that is focused changes
        OPTION_SELECTED: id_t = R_ID() #when a option was finally entered.

    class NewOptionFocusedEvent(Event):

        def __init__(self, option_index: int):

            Event.__init__(self, etype=Popup.EventTypes.NEW_OPTION_FOCUSED, data=None)

            self.option_index: int = option_index
            """
            The index of the selected option.
            Options are indexed from left to right in the given option list.
            """

        @override
        def copy(self) -> Popup.NewOptionFocusedEvent:
            return Popup.NewOptionFocusedEvent(option_index=self.option_index)

    class OptionSelectedEvent(Event):

        def __init__(self, option_index: int):

            Event.__init__(self, etype=Popup.EventTypes.OPTION_SELECTED, data=None)

            self.option_index: int = option_index
            """
            The index of the selected option.
            Options are indexed from left to right in the given option list.
            """

        @override
        def copy(self) -> Popup.OptionSelectedEvent:
            return Popup.OptionSelectedEvent(option_index=self.option_index)

    #===========================
    # STATES
    #===========================

    ACTIVE: id_t = R_ID()
    SELECT_ANIMATION_PLAYING: id_t = R_ID()

    def __init__(
                    self,
                    frame_dim: pygame.Rect,

                    data: Any = None,
                    parent_frame: Frame = None,
                    focus_group: str = "",
                    has_focus: bool = True,

                    font: pygame.font.Font = Fonts.STANDARD_FONT,

                    #popup vaiables
                    text: colored_page_t = None, #the text shown
                    background_color: color_t = Colors.BLACK, #background color for the whole widget

                    options: list[Popup.Option] = None, #the options
                    focused_option_index: int = 0, #the index of the focused option at the start

                    hmargin: float = 0.1, #the horizontal margin
                    vmargin: float = 0.05, #the vertical margin

                    text_hmargin: float = 0.2, #margin for the text
                    text_vmargin: float = 0.1, #margin for the text

                    inner_option_hmargin: float = 0.2, #inner hmargin for an option
                    inner_option_vmargin: float = 0.1, #inner vmargin for an option.

                    text_to_options_height_p: float = 0.65, #the percentage of height the text gets vs the options.
                    options_free_space_p: float = 0.2, #the percentage of free space divided between the options

                    #if a dividing line is shown
                    dividing_space_p: float = 0.1, #percentage of self.height used to divide the options from the text
                    dividing_line_shown: bool = True,
                    dividing_line_width_p: float = 1.0, #width of the dividing line relative to self.width
                    dividing_line_height_p: float = 0.1, #height of the dividing line relative to dividing_space_p
                    dividing_line_color: color_t = Colors.WHITE,

                    #outline
                    outline_size_p: float = 0.02, #The size of the outline relative to min(self.width, self.height)
                    outline_color: color_t = Colors.WHITE,

                    select_animation_duration: float = 400,#ms
                    selected_animation_size_decrease_percentage: float = 0.5
                    ):

        self._option_index: int = focused_option_index
        """
        The index of the selected option.
        """

        #now saving all variables

        self.font: pygame.font.Font = font
        """
        Font for the text and the options.
        """
        self.text: colored_page_t = text
        """
        The text shown as the info text.
        """
        self.background_color: color_t = background_color
        """
        The background color of the popup.
        """
        self.options: list[Popup.Option] = options
        """
        The list of options.
        Can be empty or None.
        """
        self.hmargin: float = hmargin
        """
        Overall horizontal margin.
        """
        self.vmargin: float = vmargin
        """
        Overall vertical margin.
        """

        self.text_to_options_height_p: float = text_to_options_height_p
        """
        The percentage of height the text gets vs the options.
        """
        self.options_free_space_p: float = 0.2
        """
        The percentage of free space divided between the options
        """

        self.dividing_space_p: float = dividing_space_p
        """
        Percentage of self.height used to divide the options from the text
        """
        self.dividing_line_shown: bool = dividing_line_shown
        """
        If the line dividing the text from the options is shown.
        """
        self.dividing_line_width_p: float = dividing_line_width_p
        """
        Width of the dividing line relative to self.width
        """
        self.dividing_line_height_p: float = dividing_line_height_p
        """
        Height of the dividing line relative to dividing_space_p
        """
        self.dividing_line_color: color_t = dividing_line_color
        """
        Color of the dividing line.
        """
        self.dividing_line_rect: pygame.Rect = None
        """
        The dividing line rectangle.
        Relative to self.frame_dim.
        """
        #outline
        self.outline_size_p: float = outline_size_p
        """
        The size of the outline relative to min(self.width, self.height)
        """
        self.outline_size: int = None
        """
        The actual outline size.
        """
        self.outline_color: color_t = outline_color
        """
        The color of the outline.
        """
        self.select_animation_duration: float = select_animation_duration
        """
        Duration of the select animation.
        """
        self.selected_animation_size_decrease_percentage: float = selected_animation_size_decrease_percentage
        """
        The maximum size decrease percentage.
        0.5 -> size decreases by half at halftime.
        """
        self.select_animation_clock: Clock = Clock()
        """
        The select animation clock.
        """
        self.highlighted_option_page_copy: rendered_surface_position_tuples_t = None
        """
        The copy of the currently highlighted option page
        for animation purposes.
        """

        #the rendered objects

        self.inner_frame_dim: pygame.Rect = None
        """
        The frame dim after applying the margins.
        """
        self.relative_inner_frame_dim: pygame.Rect = None
        """
        The relative inner frame dim for rendering.
        """
        self.text_frame_dim: pygame.Rect = None
        """
        The frame_dim for the popup text.
        """
        self.text_hmargin: float = text_hmargin
        """
        Horizontal margin for the text frame dim.
        """
        self.text_vmargin: float = text_vmargin
        """
        Vertical margin for the text frame dim.
        """
        self.divide_frame_dim: pygame.Rect = None
        """
        The frame dim for dividing the text from the options.
        """
        self.option_frame_dim: pygame.Rect = None
        """
        The frame dim for the options.
        """
        self.option_frame_hmargin: float = 0.2
        """
        Hmargin for the options.
        """
        self.option_frame_vmargin: float = 0.1
        """
        Vmargin for the options.
        """
        self.option_text_hmargin: float = inner_option_hmargin
        """
        The horizontal margin for the text
        frame inside an option.
        """
        self.option_text_vmargin: float = inner_option_vmargin
        """
        The vertical margin for the text
        frame inside an option.
        """
        self.options_free_space: float = None
        """
        The actual amount of space dividing the options.
        """
        self.all_options_frame_dims: list[pygame.Rect] = None
        """
        Rects for all options.
        """
        self.options_frame_dim_margins: list[pygame.Rect] = None
        """
        The option frames after applying the standard margins.
        """
        self.highlighted_options_frame_dim_margins: list[pygame.Rect] = None
        """
        The option frames after applying the highlighted margins.
        """
        self.rendered_text: rendered_surface_position_tuples_t = None
        """
        The rendered text, relative to self.frame_dim.
        """
        self.rendered_options: list[rendered_surface_position_tuples_t] = None
        """
        The rendered options.
        """
        self.rendered_highlighted_options: list[rendered_surface_position_tuples_t] = None
        """
        The rendered highlighted options.
        """

        #inner variables
        self.intro_delay: float = 100#ms"
        """
        Intro delay.
        """
        self.intro_delay_clock: Clock = Clock()
        """
        The intro delay clock
        """
        self.state: id_t = Popup.ACTIVE
        """
        Current State.
        """

        #cleanup
        if self.options is not None and len(self.options) == 0:
            self.options = None

        Frame.__init__(
                        self,
                        frame_enum=FrameEnums.POPUP_WIDGET,
                        frame_dim=frame_dim,
                        data=data,
                        parent_frame=parent_frame,
                        focus_group=focus_group,
                        has_focus=has_focus
                        )
        self.rerender()

    @property
    def option_index(self) -> int:
        return self._option_index

    @option_index.setter
    def option_index(self, new_index: int) -> None:
        """
        Sets the new index, whilst also pushing
        a new option selected event if the new index is
        different to the current one.
        """
        if new_index != self._option_index:

            self._option_index = new_index
            self._push_new_option_focused_event()

    @override
    def rerender(self) -> None:
        """
        @override rerender
        """

        frame_dim_no_outline: pygame.Rect = self.frame_dim.copy()
        #outline
        if not fequal(self.outline_size_p, 0):
            self.outline_size = int(min(self.width, self.height) * self.outline_size_p)
            #applying the outline
            frame_dim_no_outline = pygame.Rect(
                                                    self.x + self.outline_size,
                                                    self.y + self.outline_size,
                                                    self.width - 2*self.outline_size,
                                                    self.height - 2*self.outline_size
                                                )
        else:
            self.outline_size = None
        #creating the frame dims
        self.inner_frame_dim = graphics.apply_margins(frame_dim_no_outline, self.hmargin, self.vmargin)
        #relative
        self.relative_inner_frame_dim = graphics.position_relative(anchor_rect=self.frame_dim, make_relative_rect=self.inner_frame_dim)
        #getting the dividing percentages
        percentages: list[float] = [
                                        self.text_to_options_height_p,
                                        self.dividing_space_p,
                                        (1.0 - (self.text_to_options_height_p + self.dividing_space_p))
                                    ]

        self.text_frame_dim,\
        self.divide_frame_dim,\
        self.option_frame_dim = graphics.split_rect_vertically(self.relative_inner_frame_dim, percentages)

        self.text_frame_dim = graphics.apply_margins(self.text_frame_dim, self.text_hmargin, self.text_vmargin)
        self.option_frame_dim = graphics.apply_margins(self.option_frame_dim, self.option_frame_hmargin, self.option_frame_vmargin)

        self.options_free_space = int(self.option_frame_dim.width * self.options_free_space_p)

        #now, we get the option frames by distributing this free space among the options
        if self.options is not None or len(self.options) > 0:

            #distribute into 1 + (len(self.options) - 1) brackets, then split one
            #bracket in half for the distance from the edges
            bracket_w: int = self.options_free_space // len(self.options)

            #now, we create the frame dims for the options
            option_space: float = self.option_frame_dim.width - self.options_free_space
            #getting the width for each option
            option_w: int = option_space // len(self.options)

            cx: int = bracket_w // 2 + self.option_frame_dim.x

            self.all_options_frame_dims = []
            for i in range(len(self.options)):

                self.all_options_frame_dims.append(
                                                        pygame.Rect(
                                                                        cx,
                                                                        self.option_frame_dim.y,
                                                                        option_w,
                                                                        self.option_frame_dim.height

                                                                    )
                                                    )

                cx += option_w
                cx += bracket_w

            self.rendered_options = []
            self.rendered_highlighted_options = []
            self.options_frame_dim_margins = []
            self.highlighted_options_frame_dim_margins = []

            for i in range(len(self.options)):

                opt: Popup.Option = self.options[i]

                opt_frame: pygame.Rect = graphics.apply_margins(
                                                                    self.all_options_frame_dims[i],
                                                                    opt.option_hmargin,
                                                                    opt.option_vmargin
                                                                )

                highlighted_opt_frame: pygame.Rect = graphics.apply_margins(
                                                                                self.all_options_frame_dims[i],
                                                                                opt.highlighted_option_hmargin,
                                                                                opt.highlighted_option_vmargin
                                                                            )

                self.options_frame_dim_margins.append(opt_frame)
                self.highlighted_options_frame_dim_margins.append(highlighted_opt_frame)


                if opt.option_text != graphics.EMPTY_COLORED_PAGE():

                    opt_text_frame: pygame.Rect = graphics.apply_margins(opt_frame, self.option_text_hmargin, self.option_text_vmargin)

                    self.rendered_options.append(
                                                    graphics.render_page_from_chars_color(
                                                                                            font=self.font,
                                                                                            page=opt.option_text,
                                                                                            frame=opt_text_frame,
                                                                                            centered=True,
                                                                                            vertical_centered=True,
                                                                                            line_margin_as_percentage=0.05
                                                                                            )
                                                )
                else:
                    self.rendered_options.append(None)

                if opt.highlighted_option_text != graphics.EMPTY_COLORED_PAGE():

                    opt_text_frame: pygame.Rect = graphics.apply_margins(highlighted_opt_frame, self.option_text_hmargin, self.option_text_vmargin)

                    self.rendered_highlighted_options.append(
                                                                graphics.render_page_from_chars_color(
                                                                                                        font=self.font,
                                                                                                        page=opt.highlighted_option_text,
                                                                                                        frame=opt_text_frame,
                                                                                                        centered=True,
                                                                                                        vertical_centered=True,
                                                                                                        line_margin_as_percentage=0.05
                                                                                                        )
                                                            )
                else:
                    self.rendered_highlighted_options.append(None)

        else:
            self.rendered_options = None
            self.rendered_highlighted_options = None
            self.options_frame_dim_margins = None
            self.highlighted_options_frame_dim_margins = None

        #creating the rendered text

        if self.text is not None:
            self.rendered_text = graphics.render_page_from_chars_color(
                                                                        font=self.font,
                                                                        page=self.text,
                                                                        frame=self.text_frame_dim,
                                                                        centered=True,
                                                                        vertical_centered=True,
                                                                        line_margin_as_percentage=0.05
                                                                        )
        else:

            self.rendered_text = None

        #getting the dividing line rectangle

        dividing_line_width: int = int(self.divide_frame_dim.width * self.dividing_line_width_p)
        dividing_line_height: int = int(self.divide_frame_dim.height * self.dividing_line_height_p)

        divide_x: int = self.divide_frame_dim.x + (self.divide_frame_dim.width - dividing_line_width) // 2
        divide_y: int = self.divide_frame_dim.y + (self.divide_frame_dim.height - dividing_line_height) // 2

        self.dividing_line_rect = pygame.Rect(
                                                divide_x,
                                                divide_y,
                                                dividing_line_width,
                                                dividing_line_height
                                                )

        self.raise_prerender_flag()
        self.intro_delay_clock.start()

    @override
    def prerender(self) -> None:
        """
        @override prerender
        """

        self.surface.fill(self.background_color)

        #filling the options
        if self.options is not None and len(self.options) > 0:

            for i in range(len(self.options)):

                opt: Popup.Option = self.options[i]

                opt_frame: pygame.Rect = self.options_frame_dim_margins[i]
                highlighted_opt_frame: pygame.Rect = self.highlighted_options_frame_dim_margins[i]

                r_opt_text = self.rendered_options[i]
                r_highlighted_option_text = self.rendered_highlighted_options[i]

                if i == self.option_index:
                    #highlighted
                    self.surface.fill(opt.highlighted_background_color, rect=highlighted_opt_frame)
                    if r_highlighted_option_text is not None:
                        graphics.render_rendered_surface_position_tuples(screen=self.surface, rspt=r_highlighted_option_text)

                else:
                    #not highlighted
                    self.surface.fill(opt.background_color, rect=opt_frame)
                    if r_opt_text is not None:
                        graphics.render_rendered_surface_position_tuples(screen=self.surface, rspt=r_opt_text)

        #drawing the text
        if self.text is not None:
            graphics.render_rendered_surface_position_tuples(screen=self.surface, rspt=self.rendered_text)

        #drawing the dividing line
        if self.dividing_line_shown:
            pygame.draw.rect(self.surface, self.dividing_line_color, self.dividing_line_rect)

        #outline
        if not fequal(self.outline_size_p, 0.0):
            #drawing the outline
            pygame.draw.rect(self.surface, self.outline_color, pygame.Rect(0, 0, self.width, self.height), width=self.outline_size)

    @override
    def on_focus_lost(self, gained_focus_frame: Frame) -> None:
        """
        Sets the option index to -1, so no option will be highlighted.
        """
        self.option_index = -1

    @override
    def on_focus_gained(self, lost_focus_frame: Frame) -> None:
        """
        Sets the option index to 0 upon reentry.
        """
        self.option_index = 0

    def _push_new_option_focused_event(self) -> None:
        """
        Pushes a new option focused event into the event queue,
        taking into account all internal variables.
        """
        self.push_event(
                        Popup.NewOptionFocusedEvent(
                                                    option_index=self.option_index
                                                    )
                        )

    def _push_option_selected_event(self) -> None:
        """
        Pushes a option selected event into the event queue,
        taking into account all internal variables.
        """
        self.push_event(
                        Popup.OptionSelectedEvent(
                                                    option_index=self.option_index
                                                    )
                        )

    #===========================
    # EVENT BINDING
    #===========================

    @override
    def bind_events(self) -> None:
        """
        @override bind_events
        """

        if self.is_focused():

            #adding key bindings
            self.add_pygame_key_callback(key=pygame.K_LEFT, data=None, putback=False, func=self.left_pressed)
            self.add_pygame_key_callback(key=KeyAlternatives.LEFT_ALTERNATIVE, data=None, putback=False, func=self.left_pressed)

            self.add_pygame_key_callback(key=pygame.K_RIGHT, data=None, putback=False, func=self.right_pressed)
            self.add_pygame_key_callback(key=KeyAlternatives.RIGHT_ALTERNATIVE, data=None, putback=False, func=self.right_pressed)

            self.add_pygame_key_callback(key=pygame.K_RETURN, data=None, putback=False, func=self.enter_pressed)
            self.add_pygame_key_callback(key=KeyAlternatives.ENTER_ALTERNATIVE, data=None, putback=False, func=self.enter_pressed)

            self.add_pygame_key_callback(key=pygame.K_ESCAPE, data=None, putback=False, func=self.escape_pressed)
            self.add_pygame_key_callback(key=KeyAlternatives.BACK_KEY, data=None, putback=False, func=self.escape_pressed)

    def left_pressed(self, event: pygame.event.Event, data: Any) -> None:
        """
        If left is pressed, the selected option changes
        """

        if self.options is not None and len(self.options) > 0 and self.option_index > -1:

            new_idx = self.option_index
            new_idx -= 1
            new_idx %= len(self.options)
            self.option_index = new_idx

            self.raise_prerender_flag()

    def right_pressed(self, event: pygame.event.Event, data: Any) -> None:
        """
        If left is pressed, the selected option changes
        """

        if self.options is not None and len(self.options) > 0 and self.option_index < len(self.options)-1:

            new_idx = self.option_index
            new_idx += 1
            new_idx %= len(self.options)
            self.option_index = new_idx

            self.raise_prerender_flag()

    def enter_pressed(self, event: pygame.event.Event, data: Any) -> None:
        """
        If enter is pressed and the option index is valid,
        the selection animation starts.
        """

        if  self.options is not None and len(self.options) > 0\
            and self.option_index > -1 and self.option_index < len(self.options):

            self.initialize_selection_animation()

    def escape_pressed(self, event: pygame.event.Event, data: Any) -> None:
        """
        On escape pressed.
        """
        return Frame.EventCallback.EXIT

    #======================
    # SELECTION ANIMATION
    #======================

    def initialize_selection_animation(self) -> None:
        """
        Initializes the selection animation.
        """

        self.highlighted_option_page_copy = graphics.copy_rendered_surface_position_tuples(
                                                                                            self.rendered_highlighted_options[self.option_index]
                                                                                            )
        self.state = Popup.SELECT_ANIMATION_PLAYING
        self.select_animation_clock.start()

    def render_select_animation(self) -> None:
        """
        Renders the select animation.
        """

        percentage: float = self.select_animation_clock.elapsed() / self.select_animation_duration

        if percentage >= 1.0:

            self.finalize_select_animation()
            return

        if percentage <= 0.5:

            #shrink the frame, then render the text
            P: float = 2 * percentage
            margin: float = P * self.selected_animation_size_decrease_percentage

            shrunken_frame: pygame.Rect = graphics.apply_margins(
                                                                    self.options_frame_dim_margins[self.option_index],
                                                                    margin,
                                                                    margin
                                                                    )
            new_rendered_page: rendered_surface_position_tuples_t = graphics.render_page_from_chars_color(
                                                                                                    font=self.font,
                                                                                                    page=self.options[self.option_index].highlighted_option_text,
                                                                                                    frame=shrunken_frame,
                                                                                                    centered=True,
                                                                                                    vertical_centered=True,
                                                                                                    line_margin_as_percentage=0.05
                                                                                                    )
            #replacing the highlighted rendered option
            self.rendered_highlighted_options[self.option_index] = new_rendered_page

        else:

            #shrink the frame, then render the text
            P: float = (2 * percentage - 1.0)
            margin: float = (1.0 - P) * self.selected_animation_size_decrease_percentage

            shrunken_frame: pygame.Rect = graphics.apply_margins(
                                                                    self.options_frame_dim_margins[self.option_index],
                                                                    margin,
                                                                    margin
                                                                    )
            new_rendered_page: rendered_surface_position_tuples_t = graphics.render_page_from_chars_color(
                                                                                                    font=self.font,
                                                                                                    page=self.options[self.option_index].highlighted_option_text,
                                                                                                    frame=shrunken_frame,
                                                                                                    centered=True,
                                                                                                    vertical_centered=True,
                                                                                                    line_margin_as_percentage=0.05
                                                                                                    )
            #replacing the highlighted rendered option
            self.rendered_highlighted_options[self.option_index] = new_rendered_page
            self.raise_prerender_flag()

    def finalize_select_animation(self) -> None:
        """
        Finalizes the select animation.
        """

        self.rendered_highlighted_options[self.option_index] = self.highlighted_option_page_copy
        self.highlighted_option_page_copy = None

        self.state = Popup.ACTIVE

        self._push_option_selected_event()
        self.raise_prerender_flag()

    @override
    def tick(self) -> None:
        """
        @override tick
        """

        if self.intro_delay_clock.elapsed() > self.intro_delay:
            self.manage_pygame_events()

        if self.exit_flag_raised():
            return self._next_frame

        if self.state == Popup.SELECT_ANIMATION_PLAYING:
            self.render_select_animation()
            self.raise_prerender_flag()

        if self.prerender_flag_raised():
            self.prerender()
            self.reset_prerender_flag()

        return self
