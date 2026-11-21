from __future__ import annotations
from typing import Type, Any, Callable, override

import pygame

from collections import deque
import graphics
from graphics import page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t

from event_queue_manager import Event
from constants import Colors, Fonts, R_ID, color_t, id_t, point_t
from clock import Clock
from enum import Enum, auto
from collections.abc import Sequence
import calculations

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.dropdown_menu import DropdownMenu

class DropDownKey:
    """
    Class used for defining a dropdown key.
    """

    @staticmethod
    def from_tuple(
                    tp: tuple[str],
                    text_color: color_t = Colors.WHITE,
                    highlighted_text_color: color_t = Colors.BLACK
                    ) -> DropDownKey:
        """
        Creates a dropdown key frmo the given tuple.
        A color is not necessary for hash based accessing.
        """
        return DropDownKey(
                            option_page=graphics.page_to_colored_page(page=list(tp), text_color=text_color),
                            highlighted_option_page=graphics.page_to_colored_page(page=list(tp), text_color=highlighted_text_color)
                            )

    @staticmethod
    def tuples_to_dropdownkeys(
                                tps: Sequence[tuple[str]],
                                text_color: color_t = Colors.WHITE,
                                highlighted_text_color: color_t = Colors.BLACK
                                ) -> list[DropDownKey]:
        """
        Transforms a sequence of tuples into a
        list of dropdownkeys.
        """
        return list(
                    map(
                        lambda tp: DropDownKey.from_tuple(tp=tp, text_color=text_color, highlighted_text_color=highlighted_text_color),
                        tps
                        )
                    )

    def __init__(self, option_page: colored_page_t, highlighted_option_page: colored_page_t):
        self.option_page: colored_page_t = option_page
        self.highlighted_option_page: colored_page_t = highlighted_option_page

    def __eq__(self, other: DropdownKey) -> bool:
        """
        Comparator.
        """
        if type(other) != DropDownKey:
            return False

        if (graphics.colored_page_to_str(self.option_page) == graphics.colored_page_to_str(other.option_page))\
            and (graphics.colored_page_to_str(self.highlighted_option_page) == graphics.colored_page_to_str(other.highlighted_option_page)):
            return True
        else:
            return False

    def __hash__(self) -> int:
        """
        Hash function.
        """
        #hashes using the colors and strings of the pages
        option_page_str: str = graphics.colored_page_to_str(self.option_page)
        highlighted_option_page_str: str = graphics.colored_page_to_str(self.highlighted_option_page)

        option_page_color_string: str = ""
        highlighted_option_page_color_string: str = ""

        for line in self.option_page:
            for (text, color) in line:
                for i in range(len(color)):
                    option_page_color_string += str(color[i])

        for line in self.highlighted_option_page:
            for (text, color) in line:
                for i in range(len(color)):
                    highlighted_option_page_color_string += str(color[i])

        full_str: str = option_page_str + option_page_color_string + highlighted_option_page_str + highlighted_option_page_color_string

        return hash(full_str)


type expandable_tuple_options_t = dict[tuple[str, ...], expandable_tuple_options_t | None]
type expandable_dropdown_options_t = dict[DropDownKey, expandable_dropdown_options_t | None]
type option_trace_element_t = tuple[DropDownKey, int]
type option_trace_t = list[option_trace_element_t]
type tuple_dropdown_mapping_t = dict[ tuple[ tuple[str] ], DropDownKey ]

class ExpandableDropdownMenu(DropdownMenu):
    """
    Provides a dropdown menu, that can open up and reveal more options,
    after one option is highlighted.
    """

    DEFERRED_MENU_SHOWN: id_t = R_ID() #means the deferred menu is shown, but not selected
    FOCUS_DEFERRED: id_t = R_ID() #means the the deferred menu is fully active.

    class SelectAnimationEndedEvent(Event):

        def __init__(
                        self,
                        option_keys: list[DropDownKey],
                        indices: list[int],
                        selected_option_strings: list[str]
                        ):

            Event.__init__(self, etype=DropdownMenu.EventTypes.SELECT_ANIMATION_ENDED, data=None)

            self.option_keys: list[DropDownKey] = option_keys
            self.indices: list[int] = indices
            self.selected_option_strings: list[str] = selected_option_strings
            self.selected_option_tuples: list[tuple[str]] = self.recalculate_option_tuples()

        def recalculate_option_tuples(self) -> list[tuple[str]]:
            """
            Calculates self.selected_option_tuples, then returns it.
            """
            return [tuple(strings.split("\n")) for strings in self.selected_option_strings if strings is not None]

        @override
        def copy(self) -> ExpandableDropdownMenu.SelectAnimationEndedEvent:
            return ExpandableDropdownMenu.SelectAnimationEndedEvent(self.option_keys, self.indices, self.selected_option_strings)

    class NewOptionHighlightedEvent(Event):

        def __init__(
                        self,
                        option_keys: list[DropDownKey],
                        indices: list[int],
                        selected_option_strings: list[str]
                        ):

            Event.__init__(self, etype=DropdownMenu.EventTypes.NEW_OPTION_HIGHLIGHTED, data=None)

            self.option_keys: list[DropDownKey] = option_keys
            self.indices: list[int] = indices
            self.selected_option_strings: list[str] = selected_option_strings
            self.selected_option_tuples: list[tuple[str]] = self.recalculate_option_tuples()

        def recalculate_option_tuples(self) -> list[tuple[str]]:
            """
            Calculates self.selected_option_tuples, then returns it.
            """
            return [tuple(strings.split("\n")) for strings in self.selected_option_strings if strings is not None]

        @override
        def copy(self) -> ExpandableDropdownMenu.NewOptionHighlightedEvent:
            return ExpandableDropdownMenu.NewOptionHighlightedEvent(self.option_keys, self.indices, self.selected_option_strings)


    @staticmethod
    def page_keys_to_dropdownkey(
                                    options_dict: expandable_tuple_options_t,
                                    text_color: color_t,
                                    highlighted_text_color: color_t,

                                    prev_tuple: tuple[str] = None #the previous tuple, if its a recursive call

                                    ) -> tuple[expandable_dropdown_options_t, dict[ tuple[ tuple[str] ] , DropDownKey]]:
        """
        Given a dictionary with keys like:

        options = {
                    ("line 1", "line 2"): {
                                                ("E",): None,
                                                ("RT", "TZ", "IO"): {
                                                                        ("ERERER", "BZTT"): None,
                                                                        ("HBEDZG",): None,
                                                                        ("EE", "RR"): None,
                                                                        ("WWW", "TT"): None,

                                                                        "n_options_shown": 2
                                                                            }
                                            },
                    ("LINE",): None,
                    ("JJ", "JJ", "JJ", "JJ"): None,
                    ("GGG",): None,
                    ("JKIJI", "IJUHU"): None,
                    "n_options_shown": 3

                    }
        This function returns the same dictionary, but with the tuple keys
        transformed into (colored_page, highlighted_colored_page) tuples.

        The second argument that is returned is a mapping of tuples: dropdownkey.

        E.g. in the returned dict for options the key
        (("line 1", "line 2"), ("E",)) -> Dropdownkey for ("E",)
        """

        back_dict: expandable_dropdown_options_t = {}
        mapping_dict: dict[ tuple[tuple[str]], DropDownKey ] = {}

        for key, value in options_dict.items():

            if type(key) == tuple:

                #transforming the key
                option_page: colored_page_t = graphics.page_to_colored_page(list(key), text_color)
                highlighted_option_page: colored_page_t = graphics.page_to_colored_page(list(key), highlighted_text_color)

                new_options: expandable_dropdown_options_t = None
                new_mappings: dict[ tuple[ tuple[str] ] , DropDownKey] = None

                #mapping dict
                tuple_key: tuple[tuple[str]] = (key,)
                if prev_tuple is not None:
                    tuple_key = (*prev_tuple, key)

                if type(value) == dict:
                    new_options, new_mappings = ExpandableDropdownMenu.page_keys_to_dropdownkey(
                                                                                                options_dict=value,
                                                                                                text_color=text_color,
                                                                                                highlighted_text_color=highlighted_text_color,

                                                                                                prev_tuple=tuple_key
                                                                                                )
                    mapping_dict.update(new_mappings)

                new_key = DropDownKey(option_page=option_page, highlighted_option_page=highlighted_option_page)

                back_dict[new_key] = new_options
                mapping_dict[tuple_key] = new_key

            else:
                back_dict[key] = value

        return (back_dict, mapping_dict)

    def __init__(
                self,
                frame_dim: pygame.Rect,
                options: expandable_dropdown_options_t,
                #Options is a dict like:
                #
                # {
                #   (normal_option_page, highlighted_option_page) : {OPTIONS FOR THE NEXT DROPDOWN MENU} //or if there is no Menu its just None
                #}
                precalculated_depth_and_max_length: tuple[int, int] = None,  	#depth == how many dropdown manus follow this one,
                                                                                #max_length == number of options in the dropdown menu with the most options
                                                                                #only the first dropdown menu needs to calculate this,
                                                                                #and can pass the information on
                parent_frame: Frame = None, #since this class works recursively, each expandable dropdown menu needs to know which menu it is attached to
                dropdown_parent: Frame = None,
                #for the rest see dropdown_menu.py
                font: pygame.font.Font = Fonts.STANDARD_FONT,
                background_color: color_t = Colors.BLACK,
                highlighted_background_color: color_t = Colors.WHITE,
                in_option_line_margin_p: float = 0.05,#px
                line_margin_p: float = 0.02,#px,
                line_color: color_t = Colors.GRAY,
                lines_shown: bool = True,
                outline_size_p: float = 0.02,
                outline_color: color_t = Colors.BLACK,
                text_margins_percentage: tuple[float, float] = (0.4, 0.4),
                highlighted_text_margins_percentage: tuple[float, float] = (0.1, 0.1),
                initial_selected_index: int = -1,
                selected_animation_duration: float = 400#ms
                ):

        self.expanded_dropdown_menus: dict[DropDownKey, ExpandableDropdownMenu] = {}
        """
        list of immediate dropdown menus. if an option tuple has a follow up menu,
        the option tuple is the key and the follow up dropdown menu is the value
        """
        self.deferred_dropdown_menu: ExpandableDropdownMenu = None
        """
        if no follow up dropdown menu is open, this is None.
        Otherwise contains a reference to the follow up dropdown menu, to which the commands will be funneled.
        """
        self.dropdown_parent: Frame = dropdown_parent
        """
        parent dropdown menu. is None for the first dropdown menu
        """
        self.dictionary_options: expandable_dropdown_options_t = options
        """
        since we use a list to give the options to the parent class to initialize, we need to save the
        dictionary for ourselves
        """
        self.original_frame_dim: pygame.Rect = frame_dim
        """
        the original frame dimension, we split it horizontally for follow up dropdown menus
        """
        self.max_depth: int = -1
        """
        Decides the maximum amount of ExpandableDropdownMenus open at the same time,
        or the deepest your can subselect an option.
        """
        self.max_length: int = -1
        """
        The maximum number of options across all ExpandableDropdownMenus
        """
        self.max_depth, self.max_length = (self._calculate_depth_and_max_length(options) if precalculated_depth_and_max_length is None else precalculated_depth_and_max_length)

        frame_dim = frame_dim.copy() #getting an copy of the frame dimension
        frame_dim.width = frame_dim.width // self.max_depth #adjusting the frame dimension, splitting horizontally
        frame_dim.height = (frame_dim.height // self.max_length) * len(options) #adjusting the frame dimension based on the maximum options

        #calculating the options as a list of pages
        self.dropdown_keys: list[DropDownKey] = [key for key in options.keys() if type(key) == DropDownKey]
        option_pages: list[colored_page_t] = [key.option_page for key in self.dropdown_keys]
        highlighed_option_pages: list[colored_page_t] = [key.highlighted_option_page for key in self.dropdown_keys]

        #calling the superconstructor
        DropdownMenu.__init__(
                                self,
                                frame_dim=frame_dim,
                                options=option_pages,
                                highlighted_options=highlighed_option_pages,
                                parent_frame=parent_frame,
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

        #we need to move during when we show the deferred menu, and are not in an entered state
        self.move_states.append(ExpandableDropdownMenu.DEFERRED_MENU_SHOWN)

    def _calculate_depth_and_max_length(self, options: expandable_dropdown_options_t) -> tuple[int, int]:
        """
        returns the depth of the deepest nested dropdown menu
        we use a deque in order to avoid putting to many calls on the stack
        """
        mdepth = deque([(options, 1)])
        max_depth = 1
        max_length = -1

        #as long as we havent processed each option
        while len(mdepth) > 0:
            #getting the current option and depth
            option, depth = mdepth.popleft()
            #getting the amount of options in the dropdown
            max_length = max(max_length, len(list(option.values())))
            for v in option.values():
                if v is not None:
                    #if any of the options values is not None, that means its a dropdown menu
                    max_depth = max(max_depth, depth+1)#we need to check max deptg
                    mdepth.append((v, depth+1)) #add the next option to processing

        return max_depth, max_length

    #property override
    @DropdownMenu.selected_index.setter
    @override
    def selected_index(self, new_idx: int) -> None:
        """
        Fires a new option highlighted event.
        """

        if self._selected_index != new_idx:

            self._selected_index = new_idx

            self.push_event(
                ExpandableDropdownMenu.NewOptionHighlightedEvent(

                    option_keys=[self.dropdown_keys[self.selected_index]],
                    indices=[self.selected_index],
                    selected_option_strings=[graphics.colored_page_to_str(self.highlighted_options[self.selected_index])]
                )
            )

    #getting the index of the option box the mouse is hovering over
    def get_indices_from_mouse_pos(self, mpos: point_t) -> list[int]:
        """
        Returns a list of the indices tracing
        the deferred dropdown menus of the option the mouse is currently hovering over,
        or None if no option is selected.
        """

        prev_indices: list[int] = None

        if self.deferred_dropdown_menu is not None:

            prev_indices = self.deferred_dropdown_menu.get_indices_from_mouse_pos(mpos)

        if prev_indices is not None:
            prev_indices.insert(0, self.selected_index)
            return prev_indices

        #checking the boxframes
        for i in range(len(self.boxframes)):

            bframe, oframe, hoframe = self.boxframes[i]

            if calculations.point_collides(point=mpos, rect=bframe):
                return [i]

        return None

    def is_deferred(self) -> bool:
        """
        returns if this dropdown menu is deferred
        """
        return (self.state == ExpandableDropdownMenu.FOCUS_DEFERRED)

    @override
    def rerender(self):

        #rerendering the dropdown menu
        DropdownMenu.rerender(self)
        #clearing dropdown menus
        self.expanded_dropdown_menus = {}
        #we need to cut the frame of the current dopdown menu from the frame for the remaining dropdowns
        expanded_frame_dim = self.original_frame_dim.copy()
        expanded_frame_dim.x = self.frame_dim.x + self.frame_dim.width
        expanded_frame_dim.width -= self.frame_dim.width


    def get_expanded_dropdown_menu(self, key: DropDownKey) -> ScrollableDropdownMenu:
        """
        Creates and returns the requested menu lazily,
        or returns None.
        """

        value = self.full_options_dict[key]

        if type(value) != dict:
            return None

        #so it is a dict
        if key not in self.expanded_dropdown_menus:

            #POSSIBLE ERROR: if self.frame_width != self.with_arrows_frame_dim.width
            expanded_frame_dim: pygame.Rect = self.original_frame_dim.copy()
            expanded_frame_dim.x = self.frame_dim.x + self.frame_dim.width
            expanded_frame_dim.width -= self.frame_dim.width

            new_dropdown = ExpandableDropdownMenu(
                                                    expanded_frame_dim.copy(),
                                                    options=value.copy(),
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
                                                    lines_shown=self.lines_shown,
                                                    outline_size_p=self.outline_size_p,
                                                    outline_color=self.outline_color,
                                                    text_margins_percentage=self.text_margins_percentage,
                                                    highlighted_text_margins_percentage=self.highlighted_text_margins_percentage,
                                                    initial_selected_index=ExpandableDropdownMenu.NOTHING_SELECTED_INDEX,
                                                    selected_animation_duration=self.selected_animation_duration
                                                )

            self.expanded_dropdown_menus[key] = new_dropdown #associating the dropdown with the corresponding option

        return self.expanded_dropdown_menus[key]

    @override
    def move_up(self) -> None:
        """
        Moving up.
        """
        if self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.FOCUS_DEFERRED:
            #if deferred, let the deferred menu handle it
            self.deferred_dropdown_menu.move_up()
        else:
            #handle normally
            DropdownMenu.move_up(self)

    @override
    def move_down(self) -> None:
        """
        Moving down.
        """
        if self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.FOCUS_DEFERRED:
            #if deferred, let the deferred menu handle it
            self.deferred_dropdown_menu.move_down()
        else:
            #handle normally
            DropdownMenu.move_down(self)

    def move_right(self) -> None:
        """
        If a deferred menu is present, we give it the focus.
        """
        #defer if menu shown and going right
        if self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.DEFERRED_MENU_SHOWN:
            self.state = ExpandableDropdownMenu.FOCUS_DEFERRED
            self.deferred_dropdown_menu.move_up()
        #if it is already deferred, let the next dropdown menu handle it
        elif self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.FOCUS_DEFERRED:
            self.deferred_dropdown_menu.move_right()

        self.raise_prerender_flag()

    def move_left(self) -> None:
        """
        Moves back and relinquishes the focus if a deferred menu is present.
        """
        #if the signal to move left arrives, and a deferred menu exists, give the signal to the menu
        if self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.FOCUS_DEFERRED:
            self.deferred_dropdown_menu.move_left()
        else:
            #otherwise, if a parent exists give control back to the parent dropdown menu
            if self.dropdown_parent is not None:
                self.state = ExpandableDropdownMenu.NOTHING_SELECTED
                self.selected_index = ExpandableDropdownMenu.NOTHING_SELECTED_INDEX
                self.dropdown_parent.state = ExpandableDropdownMenu.DEFERRED_MENU_SHOWN
            else:
                #unfocus after going too far left
                self.unselect_options()

        self.raise_prerender_flag()

    @override
    def unselect_options(self) -> None:
        """
        Unselects the options.
        """
        self.deferred_dropdown_menu = None

        self.selected_index = DropdownMenu.NOTHING_SELECTED_INDEX
        self.moves_buffered = 0
        self.state = DropdownMenu.NOTHING_SELECTED

        self.raise_prerender_flag()

    def select_option_expanded(self, option_trace: option_trace_t) -> None:
        """
        Selects an expanded option, using an option trace,
        where the trace is a list of (option_key, state)
        """
        if not option_trace:
            return
        #selects the option with subselecting deferred dropdown menus
        coption, state = option_trace[0]
        self.selected_index = self.options.index(coption)

        self.deferred_dropdown_menu = self.get_expanded_dropdown_menu(coption)
        if self.deferred_dropdown_menu is not None:
            #getting if it is a full end or not
            self.deferred_dropdown_menu.select_option_expanded(option_trace[1:])

        self.state = state

        self.raise_prerender_flag()

    def get_option_trace(self) -> option_trace_t:
        """
        Gets a snapshot of the state as an option trace.
        """
        if self.state == ExpandableDropdownMenu.NOTHING_SELECTED:
            return None
        else:
            trace = [(self.dropdown_keys[self.selected_index], self.state)]
            if self.deferred_dropdown_menu is not None:
                ext = self.deferred_dropdown_menu.get_option_trace()
                if ext is not None:
                    trace.extend(ext)

            return trace

    @override
    def select(self) -> None:
        """
        Selects recursively if the deferred menu is active.
        """
        #if deferred, defer the select command
        if self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.FOCUS_DEFERRED:
            self.deferred_dropdown_menu.select()
        elif self.state == ExpandableDropdownMenu.OPTION_SELECTED:
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

        if self.deferred_dropdown_menu is None:
            self.state = DropdownMenu.OPTION_SELECTED

        self.push_event(
                            ExpandableDropdownMenu.SelectAnimationEndedEvent(
                                                                                option_keys=[self.dropdown_keys[self.selected_index]],
                                                                                indices=[self.selected_index],
                                                                                selected_option_strings=[graphics.colored_page_to_str(self.highlighted_options[self.selected_index])]
                                                                            )
                        )

        self.raise_prerender_flag()

    def select_options_deferred(self, indices: Sequence[int]) -> None:
        """
        Selects the options based on the indices.
        """

        if len(indices) == 0:
            return

        idx = indices[0]

        if idx < 0 or idx >= self.n_options():
            return

        self.selected_index = idx
        dkey: DropDownKey = self.dropdown_keys[idx]

        self.state = ExpandableDropdownMenu.OPTION_SELECTED

        self.deferred_dropdown_menu = self.get_expanded_dropdown_menu(dkey)

        if self.deferred_dropdown_menu is not None:

            self.state = ExpandableDropdownMenu.FOCUS_DEFERRED
            self.deferred_dropdown_menu.select_options_deferred(indices[1:])

        self.raise_prerender_flag()

    def select_by_keys(self, keys: Sequence[DropDownKey]) -> None:
        """
        Selects a given endpoint using the dropdownkeys.
        """

        if len(keys) == 0 or self.state not in\
            [
                ExpandableDropdownMenu.NOTHING_SELECTED,
                ExpandableDropdownMenu.OPTION_SELECTED,
                ExpandableDropdownMenu.DEFERRED_MENU_SHOWN,
                ExpandableDropdownMenu.FOCUS_DEFERRED
            ]:
            return

        hash_key: DropDownKey = keys[0]

        self.deferred_dropdown_menu = self.get_expanded_dropdown_menu(hash_key)
        if self.deferred_dropdown_menu is not None:

            self.selected_index = self.dropdown_keys.index(hash_key)

            self.state = ExpandableDropdownMenu.FOCUS_DEFERRED

            self.deferred_dropdown_menu.select_by_keys(keys[1:])

        else:

            if hash_key in self.dropdown_keys:

                self.selected_index = self.dropdown_keys.index(hash_key)

                self.state = ExpandableDropdownMenu.OPTION_SELECTED

        self.raise_prerender_flag()

    def select_by_tuples(self, tuple_keys: Sequence[tuple[str]]) -> None:
        """
        Selects a given endpoint by
        transforming the tuple keys into dropdownkeys.
        """

        if len(tuple_keys) == 0:
            return

        #converting to keys, then selecting by keys.
        keys: list[DropDownKey] = DropDownKey.tuples_to_dropdownkeys(tps=tuple_keys)
        self.select_by_keys(keys)


    @override
    def prerender(self) -> None:
        """
        Prerendering the deferred dropdown menu
        """
        DropdownMenu.prerender(self)
        #prerender next menu
        if self.deferred_dropdown_menu is not None:
            self.deferred_dropdown_menu.prerender()

    @override
    def render(self, screen):
        """
        Renders recursively.
        """
        screen.blit(self.surface, (self.x, self.y))

        if self.deferred_dropdown_menu is not None:
            self.deferred_dropdown_menu.render(screen)

    @override
    def render_at(self, screen, x, y):
        """
        Renders recursively.
        """
        screen.blit(self.surface, (x, y))

        if self.deferred_dropdown_menu is not None:
            self.deferred_dropdown_menu.render_at(screen, self.width+x, y)

    def options_key_from_index(self, index: int) -> DropDownKey:
        """
        Creates the key for the options from the selected index.
        """
        return self.dropdown_keys[index]

    @override
    def tick(self):

        #giving tick command to currently expanded dropdownmenu
        if self.deferred_dropdown_menu is not None:
            self.deferred_dropdown_menu.tick()

        if self.state in self.move_states:

            self.selected_index += self.moves_buffered
            self.selected_index %= self.n_options()

            #after a move, check if we need to show another dropdown menu
            self.deferred_dropdown_menu = self.get_expanded_dropdown_menu(self.options_key_from_index(self.index))
            if self.deferred_dropdown_menu is not None:
                self.deferred_dropdown_menu.unselect_options()
                self.state = ExpandableDropdownMenu.DEFERRED_MENU_SHOWN
            else:
                self.state = DropdownMenu.OPTION_SELECTED

            self.moves_buffered = 0

            self.raise_prerender_flag()

        if self.state == DropdownMenu.SELECT_ANIMATION_PLAYING:
            self.render_select_animation()
            self.raise_prerender_flag()

        #checking events
        if self.deferred_dropdown_menu is not None:
            for event in self.deferred_dropdown_menu.poll_events():

                if event.type == DropdownMenu.EventTypes.SELECT_ANIMATION_ENDED:
                    #if we got a selection finished event, append the own current option, then add it to the event queue
                    #modifying the event
                    event.option_keys.insert(0, self.dropdown_keys[self.selected_index])
                    event.indices.insert(0, self.selected_index)
                    event.selected_option_strings.insert(0, graphics.colored_page_to_str(self.highlighted_options[self.selected_index]))

                    event.selected_option_tuples = event.recalculate_option_tuples()

                    self.push_event(event)

                elif event.type == DropdownMenu.EventTypes.NEW_OPTION_HIGHLIGHTED:

                    #modifying the event
                    event.option_keys.insert(0, self.dropdown_keys[self.selected_index])
                    event.indices.insert(0, self.selected_index)
                    event.selected_option_strings.insert(0, graphics.colored_page_to_str(self.highlighted_options[self.selected_index]))

                    event.selected_option_tuples = event.recalculate_option_tuples()

                    self.push_event(event)

        if self.prerender_flag_raised():
            self.prerender()
            self.reset_prerender_flag()
