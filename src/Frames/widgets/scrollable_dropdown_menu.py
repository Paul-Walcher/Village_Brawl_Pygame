from __future__ import annotations
from typing import Type, Any, Callable, override

import pygame

from collections import deque
from copy import deepcopy
import graphics
from graphics import page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t
from event_queue_manager import Event
from constants import Colors, Fonts, R_ID, IIMAGE, color_t, id_t
from clock import Clock

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.dropdown_menu import DropdownMenu
from Frames.widgets.expandable_dropdown_menu import ExpandableDropdownMenu, DropDownKey, expandable_dropdown_options_t, option_trace_t

type scrollable_tuple_options_t = dict[str | tuple[str, ...], scrollable_tuple_options_t | int | None]
type scrollable_dropdown_options_t = dict[DropDownKey | str, scrollable_dropdown_options_t | int | None]
type scrollable_option_trace_element_t = tuple[DropDownKey, int, int]
type scrollable_option_trace_t = list[scrollable_option_trace_element_t]

class ScrollableDropdownMenu(ExpandableDropdownMenu):
    """
    This class provides a scrollable dropdown menu, that is also expandable.
    """

    #New States
    SCROLLING_UP: id_t = R_ID()
    SCROLLING_DOWN: id_t = R_ID()


    N_OPTIONS_SHOWN_KEY: str = "n_options_shown"

    """
    The key, for which the value defines the number of options shown.
    """
    ARROW_IMG_PATH: str = IIMAGE("Arrow_Icon.png")
    """
    The arrow, shown when scrolling is possible.
    """

    class SelectAnimationEndedEvent(Event):

        def __init__(
                        self,
                        option_keys: list[DropDownKey],
                        scroll_indices: list[int],
                        indices: list[int],
                        selected_option_strings: list[str]
                        ):

            Event.__init__(self, etype=DropdownMenu.EventTypes.SELECT_ANIMATION_ENDED, data=None)

            self.option_keys: list[DropDownKey] = option_keys
            self.scroll_indices: list[int] = scroll_indices
            self.indices: list[int] = indices
            self.selected_option_strings: list[str] = selected_option_strings
            self.selected_option_tuples: list[tuple[str]] = self.recalculate_option_tuples()

        def recalculate_option_tuples(self) -> list[tuple[str]]:
            """
            Calculates self.selected_option_tuples, then returns it.
            """
            return [tuple(strings.split("\n")) for strings in self.selected_option_strings if strings is not None]

        @override
        def copy(self) -> ScrollableDropdownMenu.SelectAnimationEndedEvent:
            return ScrollableDropdownMenu.SelectAnimationEndedEvent(self.option_keys, self.scroll_indices, self.indices, self.selected_option_strings)

    class NewOptionHighlightedEvent(Event):

        def __init__(
                        self,
                        option_keys: list[DropDownKey],
                        scroll_indices: list[int],
                        indices: list[int],
                        selected_option_strings: list[str]
                        ):

            Event.__init__(self, etype=DropdownMenu.EventTypes.NEW_OPTION_HIGHLIGHTED, data=None)

            self.option_keys: list[DropDownKey] = option_keys
            self.scroll_indices: list[int] = scroll_indices
            self.indices: list[int] = indices
            self.selected_option_strings: list[str] = selected_option_strings
            self.selected_option_tuples: list[tuple[str]] = self.recalculate_option_tuples()

        def recalculate_option_tuples(self) -> list[tuple[str]]:
            """
            Calculates self.selected_option_tuples, then returns it.
            """
            return [tuple(strings.split("\n")) for strings in self.selected_option_strings if strings is not None]

        @override
        def copy(self) -> ScrollableDropdownMenu.NewOptionHighlightedEvent:
            return ScrollableDropdownMenu.NewOptionHighlightedEvent(self.option_keys, self.scroll_indices, self.indices, self.selected_option_strings)

    def __init__(
                    self,
                    frame_dim: pygame.Rect,
                    #Options is a dict like:
                    #
                    # {
                    #   (("line1", "line2"), options_shown): {OPTIONS FOR THE NEXT DROPDOWN MENU} //or if there is no Menu its just None
                    #   and one extra key_value pair: "options_shown": n, which
                    #}
                    options: scrollable_dropdown_options_t,

                    arrow_frame_margin: float = 0.2, #amount of height used to show the arrows
                    arrow_to_text_margin: float = 0.7, #amount of occupied space by the arrow, the rest is reserved for the text.
                    arrow_text_color: color_t = Colors.BLACK,

                    precalculated_depth_and_max_length: tuple[int, int] = None,         #depth == how many dropdown menus follow this one,
                                                                                        #max_length == number of options in the dropdown menu with the most options
                                                                                        #only the first dropdown menu needs to calculate this,
                                                                                        #and can pass the information on
                    parent_frame: Frame = None,
                    dropdown_parent: Frame = None, #since this class works recursively, each expandable dropdown menu needs to know which menu it is attached to


                    #for the rest see dropdown_menu.py
                    font: pygame.font.Font = Fonts.STANDARD_FONT,
                    background_color: color_t = Colors.BLACK,
                    highlighted_background_color: color_t = Colors.WHITE,
                    in_option_line_margin_p: float = 0.02,#px
                    line_margin_p: float = 0.02,#px,
                    line_color: color_t = Colors.GRAY,
                    lines_shown: bool = True,
                    outline_size_p: float = 0.05,
                    outline_color: color_t = Colors.BLACK,
                    text_margins_percentage: tuple[int, int] = (0.4, 0.4),
                    highlighted_text_margins_percentage: tuple[int, int] = (0.1, 0.1),
                    initial_selected_index = -1,
                    selected_animation_duration: float = 400,#ms
                    scrolling_animation_duration: float = 300#ms

                ):


        #since we need to reduce the height to show the image arrows,
        #we need to save the full height
        self.arrow_frame_margin: float = arrow_frame_margin
        """
        amount of height used to show the arrows, relative to self.height.
        """
        self.arrow_to_text_margin: float = arrow_to_text_margin
        """
        amount of occupied space by the arrow, the rest is reserved for the text.
        """
        self.with_arrows_frame_dim: pygame.Rect = None
        """
        The frame dim after applying self.arrow_frame_margin to self.height.
        """
        self.arrows_shown: bool = False
        """
        Arrows shown starts out as False.
        """
        self.original_frame_dim: pygame.Rect = frame_dim.copy()
        """
        The original frame dimension received.
        """
        self.arrow_text_color: color_t = arrow_text_color
        """
        Color of the text displayed along the arrows, showing the remaining options
        not shown.
        """
        self.top_arrow_frame: pygame.Rect = None
        """
        Frame for the top arrow image.
        """
        self.top_arrow_surface: pygame.Surface = None
        """
        The surface the top arrow and its text will be rendered onto.
        """
        self.bottom_arrow_frame: pygame.Rect = None
        """
        The frame for the bottom arrow image.
        """
        self.bottom_arrow_surface: pygame.Surface = None
        """
        The surface the bottom arrow and its text will be rendered on.
        """
        self.top_arrow_surface_pos: tuple[int, int] = None
        """
        Position of the top arrow surface
        """
        self.bottom_arrow_surface_pos: tuple[int, int] = None
        """
        Position of the bottom arrow surface.
        """
        self.top_arrow_rendered: pygame.Surface = None
        """
        The rendered image of the top arrow.
        """
        self.top_arrow_pos: tuple[int, int] = None
        """
        Position of the top arrow image
        """
        self.bottom_arrow_rendered: pygame.Surface = None
        """
        The rendered image of the bottom arrow.
        """
        self.bottom_arrow_pos: tuple[int, int] = None
        """
        Position of the bottom arrow image.
        """
        self.top_arrow_text_frame: pygame.Rect = None
        """
        Frame for the top arrow text.
        """
        self.top_arrow_text_rendered: rendered_surface_position_tuples_t = None
        """
        The rendered top arrow text.
        """
        self.bottom_arrow_text_frame: pygame.Rect = None
        """
        Frame for the bottom arrow text.
        """
        self.bottom_arrow_text_rendered: rendered_surface_position_tuples_t = None
        """
        The rendered bottom arrow text.
        """
        self.full_options_dict: expandable_dropdown_options_t = options
        """
        A deep copy of all the options given to this dropdownmenu.
        """
        self.dropdown_options: list[DropDownKey] = None
        """
        The current option pages shown.
        """

        self.n_options_shown: int = -1
        """
        The number of options shown, influenced by N_OPTIONS_SHOWN_KEY
        """

        if ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY in options:
            self.n_options_shown = options[ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY]
        else:
            self.n_options_shown = len(options) #showing all if the n_options_scroll shown is not defined

        if self.n_options_shown <= 0:
            raise RuntimeError("N options shown must be > 0")

        self._scroll_index: int = 0
        """
        How far this dropdown menu is scrolled.
        """
        self.scrolling_animation_duration: float = scrolling_animation_duration
        """
        Duration of the scrolling animation duration.
        """
        self.scrolling_animation_clock: Clock = Clock()
        """
        The clock for the scrolling animation.
        """
        self.boxframes_copy: list[tuple[pygame.Rect, pygame.Rect, pygame.Rect]] = None
        """
        The boxframe copies, for scrolling.
        """
        self.rendered_texts_copy: list[rendered_surface_position_tuples_t] = None
        """
        Copy of the rendered texts, for scrolling.
        """
        self.rendered_highlighted_texts_copy: list[rendered_surface_position_tuples_t] = None
        """
        Copy of the rendered highlighted texts, for scrolling.
        """
        #calculating depth and len
        precalculated_depth_and_max_length: tuple[int, int] = (self._calculate_depth_and_max_length(options) if precalculated_depth_and_max_length is None else precalculated_depth_and_max_length)
        """
        The precalculated depth and max length if given-
        """
        self.max_depth: int = -1
        """
        The calculated max depth
        """
        self.max_length: int = -1
        """
        The max number of shown options
        """
        self.max_depth, self.max_length = precalculated_depth_and_max_length

        self.pre_select_highlighted_page: colored_page_t = None
        """
        Saving for displaying the highlighted text.
        """

        #initializing superclass
        ExpandableDropdownMenu.__init__(
                                            self,
                                            frame_dim=frame_dim,
                                            options=options,
                                            precalculated_depth_and_max_length=precalculated_depth_and_max_length,
                                            parent_frame=parent_frame,
                                            dropdown_parent=dropdown_parent,
                                            font=font,
                                            background_color=background_color,
                                            highlighted_background_color=highlighted_background_color,
                                            in_option_line_margin_p=in_option_line_margin_p,
                                            line_margin_p=line_margin_p,
                                            line_color=line_color,
                                            lines_shown=lines_shown,
                                            outline_size_p=outline_size_p,
                                            outline_color=outline_color,
                                            text_margins_percentage=text_margins_percentage,
                                            highlighted_text_margins_percentage=highlighted_text_margins_percentage,
                                            initial_selected_index=initial_selected_index,
                                            selected_animation_duration=selected_animation_duration
                                        )

        #removing the shown key from the full options
        if ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY in self.dropdown_keys:
            self.dropdown_keys.remove(ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY)


    @override
    def _calculate_depth_and_max_length(self, options: expandable_dropdown_options_t) -> tuple[int, int]:
        #returns the depth of the deepest nested dropdown menu
        #we use a deque in order to avoid putting to many calls on the stack
        mdepth = deque([(options, 1)])
        max_depth = 1
        max_length = -1

        #as long as we havent processed each option
        while len(mdepth) > 0:
            #getting the current option and depth
            option, depth = mdepth.popleft()
            #getting the amount of options in the dropdown
            vlen = sum(
                        1 for k in option
                        if k != ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY
                    )
            max_length = max(max_length, vlen)#minus 1 for n_groups shown key
            for v in option.values():
                if type(v) == dict:
                    #if any of the options values is not None, that means its a dropdown menu
                    max_depth = max(max_depth, depth+1)#we need to check max deptg
                    mdepth.append((v, depth+1)) #add the next option to processing

        return max_depth, max_length

    @property
    def scroll_index(self):
        return self._scroll_index

    @scroll_index.setter
    def scroll_index(self, val):

        if self._scroll_index != val:
            self._scroll_index = val
            self.rerender_arrow_text()

    def n_options_scroll(self) -> int:
        """
        returns the number of options currently shown
        """
        n_opt: int = self.n_options_shown
        if self.state in [ScrollableDropdownMenu.SCROLLING_UP, ScrollableDropdownMenu.SCROLLING_DOWN]:
            n_opt += 1

        return n_opt

    def n_all_options(self) -> int:
        """
        returns the number of all options available.
        """
        return len(self.dropdown_keys)

    def get_options_n_showed(self) -> list[tuple[colored_page_t, colored_page_t]]:
        """
        Returns the slice of pages of options currently shown.
        """
        return self.dropdown_keys[self.scroll_index: self.scroll_index+self.n_options_shown]

    @override
    def unselect_options(self) -> None:
        """
        Unselects the options.
        """
        self.deferred_dropdown_menu = None

        self.selected_index = DropdownMenu.NOTHING_SELECTED_INDEX
        self.moves_buffered = 0
        self.state = DropdownMenu.NOTHING_SELECTED

        self.push_event(
                        ScrollableDropdownMenu.NewOptionHighlightedEvent(
                                                                            option_keys=[self.dropdown_keys[self.selected_index + self.scroll_index]],
                                                                            scroll_indices=[self.scroll_index],
                                                                            indices=[ExpandableDropdownMenu.NOTHING_SELECTED_INDEX],
                                                                            selected_option_strings=[None]
                                                                        )
                        )

        self.raise_prerender_flag()


    @override
    def rerender(self) -> None:
        """
        Rerendering.
        """
        self.arrows_shown = False

        hframe: pygame.Rect = self.original_frame_dim.copy()
        hframe.width //= self.max_depth
        self.with_arrows_frame_dim = graphics.apply_margins(hframe, 0, self.arrow_frame_margin)

        #preparing the own frame for rerendering
        self.frame_dim = self.with_arrows_frame_dim.copy()

        #resetting the scroll indeex
        self._scroll_index = 0
        self.dropdown_options = self.get_options_n_showed()
        #getting the arrow_frames if necessary
        #rerendering the dropdown, calling the dropdown menu, since we need ScrollableDropdownMenus as deferred menus.
        DropdownMenu.rerender(self)
        #adding the other dropdown menus
        self.expanded_dropdown_menus = {}
        #we need to cut the frame of the currernt dopdown menu from the frame for the remaining dropdowns

        #POSSIBLE ERROR: if self.frame_width != self.with_arrows_frame_dim.width
        expanded_frame_dim: pygame.Rect = self.original_frame_dim.copy()
        expanded_frame_dim.x = self.frame_dim.x + self.frame_dim.width
        expanded_frame_dim.width -= self.frame_dim.width

        #adding dropdown menus recursively
        for key, eoptions in self.full_options_dict.items():
            if type(eoptions) == dict:

                new_dropdown = ScrollableDropdownMenu(
                                                        expanded_frame_dim.copy(),
                                                        options=eoptions.copy(),
                                                        arrow_frame_margin=self.arrow_frame_margin,
                                                        arrow_to_text_margin=self.arrow_to_text_margin,
                                                        precalculated_depth_and_max_length=(
                                                            self.max_depth - 1,
                                                            self.max_length
                                                        ),
                                                        parent_frame=self.parent_frame,
                                                        dropdown_parent=self,
                                                        font=self.font,
                                                        background_color=self.background_color,
                                                        highlighted_background_color=self.highlighted_background_color,
                                                        in_option_line_margin_p=self.in_option_line_margin_p,
                                                        line_margin_p=self.line_margin_p,
                                                        line_color=self.line_color,
                                                        lines_shown =self.lines_shown,
                                                        outline_size_p=self.outline_size_p,
                                                        outline_color=self.outline_color,
                                                        text_margins_percentage=self.text_margins_percentage,
                                                        highlighted_text_margins_percentage=self.highlighted_text_margins_percentage,
                                                        initial_selected_index=self.selected_index,
                                                        selected_animation_duration=self.selected_animation_duration
                                                    )

                self.expanded_dropdown_menus[key] = new_dropdown #associating the dropdown with the corresponding option

        #checking for rendering the arrows
        if self.n_options_shown < len(self.dropdown_keys):
            self.arrows_shown = True
        #calculating arrows if arrows_shown == True
        if self.arrows_shown:

            #self.frame_dim == self.with_arrows_frame_dim

            self.top_arrow_surface_pos = (self.original_frame_dim.x, self.original_frame_dim.y)
            self.bottom_arrow_surface_pos = (self.original_frame_dim.x, self.original_frame_dim.y + self.original_frame_dim.height - int(self.original_frame_dim.height * self.arrow_frame_margin / 2))


            topframe: pygame.Rect = pygame.Rect(    0,
                                                    0,
                                                    self.width,
                                                    int(self.original_frame_dim.height * self.arrow_frame_margin / 2)
                                                    )

            bottomframe: pygame.Rect = pygame.Rect(     0,
                                                        0,
                                                        self.width,
                                                        int(self.original_frame_dim.height * self.arrow_frame_margin / 2)
                                                        )

            #splitting percentages
            split_p: list[float] = [(1.0 - self.arrow_to_text_margin), self.arrow_to_text_margin]
            #getting the text and image frames.
            self.top_arrow_text_frame, self.top_arrow_frame = graphics.split_rect_vertically(topframe, split_p)
            self.bottom_arrow_frame, self.bottom_arrow_text_frame = graphics.split_rect_vertically(bottomframe, split_p[::-1])

            #rendering the arrows
            self.top_arrow_rendered, self.top_arrow_pos  = graphics.img_load_and_position(  ScrollableDropdownMenu.ARROW_IMG_PATH,
                                                                                            self.top_arrow_frame)
            self.bottom_arrow_rendered, self.bottom_arrow_pos  = graphics.img_load_and_position(    ScrollableDropdownMenu.ARROW_IMG_PATH,
                                                                                                    self.bottom_arrow_frame)
            #rotating the bottom arrow
            self.bottom_arrow_rendered = pygame.transform.rotate(self.bottom_arrow_rendered, 180.0)
            #surfaces
            self.top_arrow_surface = pygame.Surface((topframe.width, topframe.height), pygame.SRCALPHA)
            self.bottom_arrow_surface = pygame.Surface((bottomframe.width, bottomframe.height), pygame.SRCALPHA)

            self.rerender_arrow_text()
            self.raise_prerender_flag()

    def rerender_arrow_text(self) -> None:
        """
        Rerenders the text above the arrows.
        """
        #if no arrows are shown, return
        if not self.arrows_shown:
            return

        topnum: int = self.scroll_index
        bottomnum: int = len(self.dropdown_keys) - self.scroll_index - self.n_options_shown

        self.top_arrow_text_rendered = graphics.render_page_from_chars_color(
                                                                                self.font,
                                                                                graphics.str_to_colored_page(str(topnum), self.arrow_text_color),
                                                                                self.top_arrow_text_frame,
                                                                                centered=True,
                                                                                vertical_centered=True
                                                                                )

        self.bottom_arrow_text_rendered = graphics.render_page_from_chars_color(
                                                                                    self.font,
                                                                                    graphics.str_to_colored_page(str(bottomnum), self.arrow_text_color),
                                                                                    self.bottom_arrow_text_frame,
                                                                                    centered=True,
                                                                                    vertical_centered=True
                                                                                )
        self.raise_prerender_flag()

    @override
    def prerender(self):
        """
        Prerendering
        """
        #prerendering using the expandable dropdown menu
        ExpandableDropdownMenu.prerender(self)

        #rendering the arrows extra
        if self.arrows_shown:

            self.top_arrow_surface.fill(Colors.TRANSPARENT)
            self.bottom_arrow_surface.fill(Colors.TRANSPARENT)

            self.top_arrow_surface.blit(self.top_arrow_rendered, self.top_arrow_pos)
            graphics.render_rendered_surface_position_tuples(self.top_arrow_surface, self.top_arrow_text_rendered)

            self.bottom_arrow_surface.blit(self.bottom_arrow_rendered, self.bottom_arrow_pos)
            graphics.render_rendered_surface_position_tuples(self.bottom_arrow_surface, self.bottom_arrow_text_rendered)

    @override
    def render(self, screen):
        """
        Render override
        """
        if self.deferred_dropdown_menu is not None:
            self.deferred_dropdown_menu.render(screen)

        screen.blit(self.surface, (self.x, self.y))

        if self.arrows_shown:
            screen.blit(self.top_arrow_surface, self.top_arrow_surface_pos)
            screen.blit(self.bottom_arrow_surface, self.bottom_arrow_surface_pos)

    @override
    def render_at(self, screen, x, y):
        """
        Render override
        """
        if self.deferred_dropdown_menu is not None:
            self.deferred_dropdown_menu.render_at(screen, x + self.width, y)

        screen.blit(self.surface, (x, y + self.top_arrow_surface.height))

        if self.arrows_shown:
            screen.blit(self.top_arrow_surface, (x, y))
            screen.blit(self.bottom_arrow_surface, (x, y + self.top_arrow_surface.height + self.height))

    @override
    def select_option_expanded(self, option_trace: scrollable_option_trace_t) -> None:
        """
        Focuses the option indicated by the option trace.
        """
        if not option_trace:
            return

        #selects the option with subselecting deferred dropdown menus
        coption, state, sindex = option_trace[0]
        self.scroll_index = sindex
        self.dropdown_options = self.get_options_n_showed()

        self.selected_index = self.dropdown_options.index(coption)

        if type(self.full_options_dict[coption]) == dict:
            self.deferred_dropdown_menu = self.expanded_dropdown_menus[coption]
            #getting if it is a full end or not
            self.deferred_dropdown_menu.select_option_expanded(option_trace[1:])

        self.state = state
        self.raise_prerender_flag()

    @override
    def get_option_trace(self) -> scrollable_option_trace_t:
        """
        Returns the trace for a scrollable dropdownmenu
        """

        if self.state == ScrollableDropdownMenu.NOTHING_SELECTED:
            return None
        else:

            trace = [(self.dropdown_options[self.selected_index], self.state, self.scroll_index)]
            if self.deferred_dropdown_menu is not None:
                ext = self.deferred_dropdown_menu.get_option_trace()
                if ext is not None:
                    trace.extend(ext)

            return trace

    @override
    def move_up(self) -> None:
        """
        For pushing events.
        """
        if self.state == DropdownMenu.NOTHING_SELECTED:

            self.push_event(
                                ScrollableDropdownMenu.NewOptionHighlightedEvent(
                                                                                    option_keys=[self.dropdown_keys[self.selected_index + self.scroll_index]],
                                                                                    scroll_indices=[self.scroll_index],
                                                                                    indices=[0],
                                                                                    selected_option_strings=[graphics.colored_page_to_str(self.highlighted_options[self.scroll_index])]
                                                                                    )
                            )

        ExpandableDropdownMenu.move_up(self)

    @override
    def move_down(self) -> None:
        """
        For pushing events.
        """
        if self.state == DropdownMenu.NOTHING_SELECTED:

            self.push_event(
                                ScrollableDropdownMenu.NewOptionHighlightedEvent(
                                                                                    option_keys=[self.dropdown_keys[self.selected_index + self.scroll_index]],
                                                                                    scroll_indices=[self.scroll_index],
                                                                                    indices=[0],
                                                                                    selected_option_strings=[graphics.colored_page_to_str(self.highlighted_options[self.scroll_index])]
                                                                                    )
                            )

        ExpandableDropdownMenu.move_down(self)



    @override
    def tick(self):

        #giving tick command to currently expanded dropdownmenu
        if self.deferred_dropdown_menu is not None:
            self.deferred_dropdown_menu.tick()

        if self.state in self.move_states:

            #saving the previously selected index.
            prev_sindex = self.selected_index
            self.selected_index += self.moves_buffered

            #if we hit the the ceiling, and scrolling is possible, try scrolling up
            if self.selected_index < 0 and prev_sindex >= 0:
                self.selected_index = 0
                self.state = ScrollableDropdownMenu.SCROLLING_UP
                self.initialize_scrolling_up()
            #if we hit the bottom, and scrolling is possible, try scrolling down
            elif self.selected_index >= self.n_options_scroll():
                self.selected_index = self.n_options_scroll() - 1
                self.state = ScrollableDropdownMenu.SCROLLING_DOWN
                self.initialize_scrolling_down()

            #after a move, check if we need to show another dropdown menu
            if self.state not in [ScrollableDropdownMenu.SCROLLING_UP, ScrollableDropdownMenu.SCROLLING_DOWN]:

                if self.dropdown_options[self.selected_index] in self.expanded_dropdown_menus:
                    self.deferred_dropdown_menu = self.expanded_dropdown_menus[self.dropdown_options[self.selected_index]]
                    self.state = ExpandableDropdownMenu.DEFERRED_MENU_SHOWN
                else:
                    self.deferred_dropdown_menu = None
                    self.state = DropdownMenu.OPTION_SELECTED

                if self.moves_buffered != 0:
                    self.push_event(
                                        ScrollableDropdownMenu.NewOptionHighlightedEvent(
                                                                                            option_keys=[self.dropdown_keys[self.selected_index + self.scroll_index]],
                                                                                            scroll_indices=[self.scroll_index],
                                                                                            indices=[self.selected_index],
                                                                                            selected_option_strings=[graphics.colored_page_to_str(self.highlighted_options[self.selected_index+self.scroll_index])]
                                                                                            )
                                    )
            #resetting moves buffered
            self.moves_buffered = 0

            self.raise_prerender_flag()

        elif self.state == DropdownMenu.SELECT_ANIMATION_PLAYING:
            self.render_select_animation()
            self.raise_prerender_flag()

        elif self.state == ScrollableDropdownMenu.SCROLLING_UP:
            self.scroll_up()
            self.raise_prerender_flag()

        elif self.state == ScrollableDropdownMenu.SCROLLING_DOWN:
            self.scroll_down()
            self.raise_prerender_flag()

        #checking events
        if self.deferred_dropdown_menu is not None:
            for event in self.deferred_dropdown_menu.poll_events():

                if event.type == DropdownMenu.EventTypes.SELECT_ANIMATION_ENDED:
                    #if we got a selection finished event, append the own current option, then add it to the event queue
                    #modifying the event
                    event.option_keys.insert(0, self.dropdown_keys[self.selected_index + self.scroll_index])
                    event.scroll_indices.insert(0, self.scroll_index)
                    event.indices.insert(0, self.selected_index)
                    event.selected_option_strings.insert(0, graphics.colored_page_to_str(self.highlighted_options[self.selected_index+self.scroll_index]))

                    event.selected_option_tuples = event.recalculate_option_tuples()

                    self.push_event(event)

                elif event.type == DropdownMenu.EventTypes.NEW_OPTION_HIGHLIGHTED:

                    #modifying the event
                    event.option_keys.insert(0, self.dropdown_keys[self.selected_index + self.scroll_index])
                    event.scroll_indices.insert(0, self.scroll_index)
                    event.indices.insert(0, self.selected_index)
                    event.selected_option_strings.insert(0, graphics.colored_page_to_str(self.highlighted_options[self.selected_index+self.scroll_index]))

                    event.selected_option_tuples = event.recalculate_option_tuples()

                    self.push_event(event)

        if self.prerender_flag_raised():
            self.prerender()
            self.reset_prerender_flag()


    def initialize_scrolling_up(self) -> None:
        """
        Starts the scrolling up animation
        """

        #if no scrolling possible, return
        if self.scroll_index == 0 or len(self.dropdown_keys) <= self.n_options_shown:
            self.state = DropdownMenu.OPTION_SELECTED
            return

        #create new option box
        tmb, htmb = self.text_margin_box.copy(), self.highlighted_text_margin_box.copy()

        tmb.x += self.outline_size
        htmb.x += self.outline_size

        tmb.y += -self.full_box_height + self.outline_size
        htmb.y += -self.full_box_height + self.outline_size


        box = pygame.Rect(
                            self.outline_size,
                            -self.full_box_height + self.outline_size,
                            self.inner_frame_dim.width,
                            self.option_box_height
                            )

        self.boxframes.insert(0, (box, tmb, htmb))
        self.boxframes_copy = [(b.copy(), t.copy(), h.copy()) for b, t, h in self.boxframes]

        dropdownkey = self.dropdown_keys[self.scroll_index-1]
        page = dropdownkey.option_page
        hpage = dropdownkey.highlighted_option_page

        rtext = graphics.render_page_from_chars_color(
                                                        font=self.font,
                                                        page=page,
                                                        frame=tmb,
                                                        centered=True,
                                                        vertical_centered=True,
                                                        line_margin_as_percentage=self.in_option_line_margin_p
                                                        )
        hrtext = graphics.render_page_from_chars_color(
                                                        font=self.font,
                                                        page=hpage,
                                                        frame=htmb,
                                                        centered=True,
                                                        vertical_centered=True,
                                                        line_margin_as_percentage=self.in_option_line_margin_p
                                                        )

        self.rendered_texts.insert(0, rtext)
        self.rendered_highlighted_texts.insert(0, hrtext)
        self.rendered_texts_copy = [[(tr.copy(), pos) for tr, pos in rtext] for rtext in self.rendered_texts]
        self.rendered_highlighted_texts_copy = [[(tr.copy(), pos) for tr, pos in rtext] for rtext in self.rendered_highlighted_texts]

        #setting the selected index down by 1
        self.selected_index = 1
        #starting the clock
        self.scrolling_animation_clock.start()

    def scroll_up(self) -> None:
        """
        Rendering the scrolling animation.
        """

        percentage = self.scrolling_animation_clock.elapsed() / self.scrolling_animation_duration

        if percentage >= 1.0:
            self.finalize_scrolling_up()
        else:

            scroll_px = int(percentage * self.full_box_height)

            for i in range(self.n_options_scroll()):

                cpbox, cptmb, cphtmb = self.boxframes_copy[i]
                box, tmb, htmb = self.boxframes[i]

                box.y = cpbox.y + scroll_px
                tmb.y = cptmb.y + scroll_px
                htmb.y = cphtmb.y + scroll_px
                #text
                rta = []
                for text, pos in self.rendered_texts_copy[i]:
                    rt = (text, (pos[0], pos[1] + scroll_px))
                    rta.append(rt)
                self.rendered_texts[i] = rta
                #highlighted texts
                rta = []
                for text, pos in self.rendered_highlighted_texts_copy[i]:
                    rt = (text, (pos[0], pos[1] + scroll_px))
                    rta.append(rt)
                self.rendered_highlighted_texts[i] = rta

        self.raise_prerender_flag()

    def finalize_scrolling_up(self) -> None:
        """
        Ends the scrolling up animation.
        """
        #we dont need the first box that is not rendered
        self.boxframes = self.boxframes_copy[1:]
        #cutting out the last texts
        self.rendered_texts = self.rendered_texts_copy[:-1]
        #moving all texts one box down
        self.rendered_texts = [[(text, (x, y+self.full_box_height)) for text, (x, y) in op] for op in self.rendered_texts]
        #cutting out the last highlighted texts
        self.rendered_highlighted_texts = self.rendered_highlighted_texts_copy[:-1]
        #moving all texts one box down
        self.rendered_highlighted_texts = [[(text, (x, y+self.full_box_height)) for text, (x, y) in op] for op in self.rendered_highlighted_texts]

        #decrementing the scroll index
        self.scroll_index -= 1
        self.dropdown_options = self.get_options_n_showed()

        self.selected_index = 0
        self.state = DropdownMenu.OPTION_SELECTED

        self.push_event(
                            ScrollableDropdownMenu.NewOptionHighlightedEvent(
                                                                                option_keys=[self.dropdown_keys[self.selected_index + self.scroll_index]],
                                                                                scroll_indices=[self.scroll_index],
                                                                                indices=[self.selected_index],
                                                                                selected_option_strings=[graphics.colored_page_to_str(self.highlighted_options[self.selected_index+self.scroll_index])]
                                                                                )
                        )

        self.raise_prerender_flag()

    def initialize_scrolling_down(self) -> None:
        """
        Initializes the scrolling down animation.
        """

        if self.scroll_index + self.n_options_shown >= len(self.dropdown_keys) or len(self.dropdown_keys) <= self.n_options_shown:
            self.state = DropdownMenu.OPTION_SELECTED
            return

        lbox, ltmb, lhtmb = self.boxframes[-1]

        #create new option box
        tmb = ltmb.copy()
        tmb.y += self.full_box_height
        htmb = lhtmb.copy()
        htmb.y += self.full_box_height

        box = lbox.copy()
        box.y += self.full_box_height

        self.boxframes.append((box, tmb, htmb))
        self.boxframes_copy = [(b.copy(), t.copy(), h.copy()) for b, t, h in self.boxframes]

        dropdownkey = self.dropdown_keys[self.scroll_index+self.n_options_shown]
        page = dropdownkey.option_page
        hpage = dropdownkey.highlighted_option_page

        rtext = graphics.render_page_from_chars_color(
                                                        font=self.font,
                                                        page=page,
                                                        frame=tmb,
                                                        centered=True,
                                                        vertical_centered=True,
                                                        line_margin_as_percentage=self.in_option_line_margin_p
                                                        )
        hrtext = graphics.render_page_from_chars_color(
                                                        font=self.font,
                                                        page=hpage,
                                                        frame=htmb,
                                                        centered=True,
                                                        vertical_centered=True,
                                                        line_margin_as_percentage=self.in_option_line_margin_p
                                                        )

        self.rendered_texts.append(rtext)
        self.rendered_highlighted_texts.append(hrtext)
        self.rendered_texts_copy = [[(tr.copy(), pos) for tr, pos in rtext] for rtext in self.rendered_texts]
        self.rendered_highlighted_texts_copy = [[(tr.copy(), pos) for tr, pos in rtext] for rtext in self.rendered_highlighted_texts]

        self.selected_index = self.n_options_scroll() - 2 #setting the selected index

        self.scrolling_animation_clock.start()

    def scroll_down(self) -> None:
        """
        Rendering the scrolling down animation.
        """
        percentage = self.scrolling_animation_clock.elapsed() / self.scrolling_animation_duration

        if percentage >= 1.0:
            self.finalize_scrolling_down()
        else:

            scroll_px = int(percentage * self.full_box_height)

            for i in range(self.n_options_scroll()):

                cpbox, cptmb, cphtmb = self.boxframes_copy[i]
                box, tmb, htmb = self.boxframes[i]

                box.y = cpbox.y - scroll_px
                tmb.y = cptmb.y - scroll_px
                htmb.y = cphtmb.y - scroll_px
                #text
                rta = []
                for text, pos in self.rendered_texts_copy[i]:
                    rt = (text, (pos[0], pos[1] - scroll_px))
                    rta.append(rt)
                self.rendered_texts[i] = rta
                #highlighted texts
                rta = []
                for text, pos in self.rendered_highlighted_texts_copy[i]:
                    rt = (text, (pos[0], pos[1] - scroll_px))
                    rta.append(rt)
                self.rendered_highlighted_texts[i] = rta

        self.raise_prerender_flag()


    def finalize_scrolling_down(self) -> None:
        """
        Ending the scrolling animation.
        """


        self.boxframes = self.boxframes_copy[:-1]

        self.rendered_texts = self.rendered_texts_copy[1:]
        self.rendered_texts = [[(text, (x, y-self.full_box_height)) for text, (x, y) in op] for op in self.rendered_texts]

        self.rendered_highlighted_texts = self.rendered_highlighted_texts_copy[1:]
        self.rendered_highlighted_texts = [[(text, (x, y-self.full_box_height)) for text, (x, y) in op] for op in self.rendered_highlighted_texts]

        self.scroll_index += 1
        self.dropdown_options = self.get_options_n_showed()

        self.state = DropdownMenu.OPTION_SELECTED
        #we need to set the selected index after changing the state
        self.selected_index = self.n_options_scroll() - 1

        self.push_event(
                            ScrollableDropdownMenu.NewOptionHighlightedEvent(
                                                                                option_keys=[self.dropdown_keys[self.selected_index + self.scroll_index]],
                                                                                scroll_indices=[self.scroll_index],
                                                                                indices=[self.selected_index],
                                                                                selected_option_strings=[graphics.colored_page_to_str(self.highlighted_options[self.selected_index+self.scroll_index])]
                                                                                )
                        )

        self.raise_prerender_flag()

    @override
    def select(self) -> None:
        """
        Selects recursively if the deferred menu is active.
        """
        #if deferred, defer the select command
        if self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.FOCUS_DEFERRED:
            self.deferred_dropdown_menu.select()
        elif self.state == ExpandableDropdownMenu.OPTION_SELECTED:

            self.pre_select_highlighted_page = self.highlighted_options[self.selected_index]
            self.highlighted_options[self.selected_index] = self.highlighted_options[self.selected_index+self.scroll_index]
            #selects the current selected option
            self.state = ExpandableDropdownMenu.SELECT_ANIMATION_PLAYING
            self.rtext_copy = self.rendered_highlighted_texts[self.selected_index]
            self.select_clock.start()

    @override
    def finalize_select_animation(self) -> None:
        """
        Finalizes the select animation.
        """
        self.rendered_highlighted_texts[self.selected_index] = self.rtext_copy
        self.highlighted_options[self.selected_index] = self.pre_select_highlighted_page
        self.pre_select_highlighted_page = None

        if self.deferred_dropdown_menu is None:
            self.state = DropdownMenu.OPTION_SELECTED

        self.push_event(
                            ScrollableDropdownMenu.SelectAnimationEndedEvent(
                                                                                option_keys=[self.dropdown_keys[self.selected_index + self.scroll_index]],
                                                                                scroll_indices=[self.scroll_index],
                                                                                indices=[self.selected_index],
                                                                                selected_option_strings=[graphics.colored_page_to_str(self.highlighted_options[self.selected_index+self.scroll_index])]
                                                                            )
                        )
        self.raise_prerender_flag()
