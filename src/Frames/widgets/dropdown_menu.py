from __future__ import annotations
from typing import Typing, Callable, Any, override

import pygame

import graphics
from graphics import page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t

from event_queue_manager import Event
from constants import Colors, Fonts, R_ID, color_t
from clock import Clock
from enum import Enum, auto

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums


class DropdownMenu(Frame):

    """
    The dropdown menu.
    This class provides a dropdown menu, which is handled externally using
    move_up or move_down.
    """

    #Available Options
    NOTHING_SELECTED_INDEX: int = -1 #index when nothing is selected

    #Nothing selected means nothing will be highlighted
    NOTHING_SELECTED = R_ID()
    #option selected means the currently selected option will be highlighted
    OPTION_SELECTED = R_ID()
    #Means the selection animation is playing, and the selection progress is going on
    SELECT_ANIMATION_PLAYING = R_ID()

    class EventTypes(Enum):

        SELECT_ANIMATION_ENDED = auto() #indicates the selection animation is over,
                                        #and the selection process finished
        NEW_OPTION_HIGHLIGHTED = auto()


    class SelectAnimationEndedEvent(Event):

        def __init__(self, selected_index: int, selected_option_str: str):

            Event.__init__(self, etype=DropdownMenu.EventTypes.SELECT_ANIMATION_ENDED, data=None)

            self.selected_index: int = selected_index
            self.selected_option_str: str = selected_option_str

        @override
        def copy(self) -> SelectAnimationEndedEvent:
            return SelectAnimationEndedEvent(self.selected_index, self.selected_option_str)

    class NewOptionHighlightedEvent(Event):

        def __init__(self, selected_index: int, selected_option_str: str):

            Event.__init__(self, etype=DropdownMenu.EventTypes.NEW_OPTION_HIGHLIGHTED, data=None)

            self.selected_index: int = selected_index
            self.selected_option_str: str = selected_option_str

        @override
        def copy(self) -> NewOptionHighlightedEvent:
            return NewOptionHighlightedEvent(self.selected_index, self.selected_option_str)

    def __init__(
                self,
                frame_dim: pygame.Rect, #dimensions into which the dropdown menu gets rendered
                options: list[colored_page_t],   #list of lines of options, where each line is a list of sentences
                                                        #example: options=[["Option 1"], ["This line is long", "so it gets broken up"]]
                highlighted_options: list[colored_page_t] = None, #the highlighted option pages
                parent_frame: Frame = None,
                font: pygame.font.Font = Fonts.STANDARD_FONT, #font for the option text
                background_color: color_t = Colors.BLACK, #background color for unhighlighted option boxes
                highlighted_background_color: color_t = Colors.WHITE, #background color for highlighted option boxes
                in_option_line_margin_p: float = 0.02,#px, the distance between lines inside an option box
                line_margin_p: float = 0.02, #size of the lines dividing the otion boxes relative to self.height
                line_color: color_t = Colors.GRAY, #color of the line dividing the options
                lines_shown: bool = True, #decides if the dividing line is shown or not
                outline_size_p: float = 0.05, #px, size of the outline of the dropdown menu, relative to min(self.width, self.height)
                outline_color: color_t = Colors.WHITE, #color of the outline of the dropdown menu
                text_margins_percentage: tuple[float, float] = (0.4, 0.4), #means the text will be moved in by text_margins_percentage / 2
                highlighted_text_margins_percentage: tuple[float, float] = (0.1, 0.1), #if the text is highlighted, the box of it
                                                                #should not be moved in and made smaller as much
                initial_selected_index: int = DropdownMenu.NOTHING_SELECTED_INDEX, #what will initially be selected. if initial_selected_index==-1, nothing is selected at first
                selected_animation_duration: float = 400#ms, #how long the selection animation plays
                ):

        if options is None or len(options) == 0:
            raise RuntimeError("No options provided")

        super().__init__(
                            frame_enum=FrameEnums.DROPDOWN_MENU_WIDGET,
                            data=None,
                            frame_dim=frame_dim,
                            parent_frame=parent_frame,
                            focus_group=None
                            )

        #Assigning the initial values
        self.options: list[colored_page_t] = options
        """
        The selected options.
        """
        self.highlighted_options: list[colored_page_t] = (highlighted_options if highlighted_options is not None else self.options.copy())
        """
        The highlighted pages.
        """
        self.selected_index: int = initial_selected_index
        """
        The selected index.
        """
        self.font: pygame.font.Font = font
        """
        Font for the option texts
        """
        self.background_color: color_t = background_color
        """
        The background color of the option boxes.
        """
        self.highlighted_background_color: color_t = highlighted_background_color
        """
        The background color for a selected option box.
        """
        self.in_option_line_margin_p: float = in_option_line_margin_p
        """
        Line margin for the text inside the option boxes.
        """
        self.line_margin_p: float = line_margin_p
        """
        size of the lines in relation to self.height.
        """
        self.line_margin: int = -1
        """
        The actual size of a dividing line.
        """
        self.line_color: color_t = line_color
        """
        The color of the dividing lines.
        """
        self.lines_shown: bool = lines_shown
        """
        Whether the lines are shown or not.
        """
        self.outline_size_p: float = outline_size_p
        """
        Size of the outline, relative to min(self.width, self.height)
        """
        self.outline_size: int = -1
        """
        The actual outline size.
        """
        self.outline_color: color_t = outline_color
        """
        The color of the outline.
        """
        self.text_margins_percentage: tuple[int, int] = text_margins_percentage
        """
        The margins for inside an option box.
        """
        self.highlighted_text_margins_percentage: tuple[int, int] = highlighted_text_margins_percentage
        """
        The margins for a selected option box.
        """
        self.selected_animation_duration: float = selected_animation_duration
        """
        Duration of the select animation.
        """
        #additional variables

        #the surface onto which everything will be rendered
        self.surface: pygame.Surface = None
        """
        The own surface.
        """
        #inner_frame_dim describes the frame dimension after removing the outline
        self.inner_frame_dim: pygame.Rect = None
        """
        The frame after subtracting the outline size.
        """
        self.option_box_width: int = -1
        """
        width of the option box, which shows the text for one option.
        """
        self.option_box_height: int = -1
        """
        height of the option box.
        """
        self.text_margin_box: pygame.Rect = None
        """
        The frame the text will be rendered into after applying the text margins.
        """
        self.highlighted_text_margin_box: pygame.Rect = None
        """
        The frame for highlighted option text.
        """
        self.full_box_height: int = -1
        """
        The height of a full box, including dividing lines.
        """
        self.boxframes: list[pygame.Rect] = None
        """
        list of the dimension rects of the option boxes, relative to self.surface, x and y
        positions calculated.
        each element is a tuple:    (option_box_dim, -> the full option box frame
                                    normal_text_dim, -> the frame after the text margins have been applied
                                    highlighted_text_dim -> the frame after the highlighted text margins have been applied.
                                    )
        """
        self.state: int = (DropdownMenu.NOTHING_SELECTED if self.selected_index == DropdownMenu.NOTHING_SELECTED_INDEX else DropdownMenu.OPTION_SELECTED)
        """
        the state of the dropdown menu
        """
        self.rendered_texts: list[rendered_surface_position_tuples_t] = None
        """
        container for the rendered option texts
        """
        self.rendered_highlighted_texts: list[rendered_surface_position_tuples_t] = None
        """
        container for the highlighted option texts.
        """
        self.moves_buffered: int = 0
        """
        buffer for the up/down moves. < 0 moves down, > 0 moves up.
        """
        self.move_states: list[int] = [DropdownMenu.OPTION_SELECTED]
        """
        Specifies which states are suitable for moving.
        """
        self.select_clock: Clock = Clock()
        """
        Clock for the select animation.
        """
        self.rtext_copy: pygame.Surface = None
        """
        Copy for saving the highlighted surface when playing the select animation.
        """

        #start rerendering
        self.rerender()

    def n_options(self) -> int:
        """
        Returns the number of options available.
        """
        return len(self.options)

    @override
    def rerender(self) -> None:

        #resetting all internal variables
        self.moves_buffered = 0
        self.rendered_texts = []
        self.rendered_highlighted_texts = []
        self.boxframes = []
        self.state = (DropdownMenu.NOTHING_SELECTED if self.selected_index == DropdownMenu.NOTHING_SELECTED_INDEX else DropdownMenu.OPTION_SELECTED)
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        #calculating the sizes
        self.line_margin = int(self.height * self.line_margin_p)
        self.outline_size = int(min(self.width, self.height) * self.outline_size_p)

        #calculating the inner frame without the outline
        self.inner_frame_dim = pygame.Rect(self.x + self.outline_size, self.y + self.outline_size,
                                                        self.width - 2*self.outline_size, self.height - 2*self.outline_size)
        #height available without the dividing lines
        no_lines_height = self.inner_frame_dim.height - (self.n_options() - 1) * self.line_margin

        #calculating the option box dimensions
        self.option_box_width = self.inner_frame_dim.width
        self.option_box_height = no_lines_height // self.n_options()
        self.full_box_height = self.inner_frame_dim.height // self.n_options()

        #calculating the text margin boxes
        self.text_margin_box = graphics.apply_margins(pygame.Rect(0, 0, self.option_box_width, self.option_box_height), *self.text_margins_percentage)
        self.highlighted_text_margin_box = graphics.apply_margins(pygame.Rect(0, 0, self.option_box_width, self.option_box_height), *self.highlighted_text_margins_percentage)

        #the topleft corner of the current option box
        cx = self.outline_size
        cy = self.outline_size

        for i in range(self.n_options()):

            #rendering the option boxes and calculating their dimensions
            tmb, htmb = self.text_margin_box.copy(), self.highlighted_text_margin_box.copy()
            tmb.x += cx
            tmb.y += cy
            htmb.x += cx
            htmb.y += cy

            #getting the option box dimensions
            box = pygame.Rect(cx, cy, self.inner_frame_dim.width, self.option_box_height)
            self.boxframes.append((box, tmb, htmb))

            #rendering the texts
            rtext: rendered_surface_position_tuples_t = graphics.render_page_from_chars_color(
                                                                                                font=self.font,
                                                                                                page=self.options[i],
                                                                                                frame=tmb,
                                                                                                centered=True,
                                                                                                vertical_centered=True,
                                                                                                line_margin_as_percentage=self.in_option_line_margin_p
                                                                                                )
            hrtext: rendered_surface_position_tuples_t = graphics.render_page_from_chars_color(
                                                                                            font=self.font,
                                                                                            page=self.highlighted_options[i],
                                                                                            frame=htmb,
                                                                                            centered=True,
                                                                                            vertical_centered=True,
                                                                                            line_margin_as_percentage=self.in_option_line_margin_p
                                                                                        )
            self.rendered_texts.append(rtext)
            self.rendered_highlighted_texts.append(hrtext)
            #increasing the height for the next option frame
            cy += self.full_box_height

        #prerendering onto self.surface
        self.prerender()

    def prerender(self) -> None:
        #filling the surface
        self.surface.fill(self.background_color)
        #rendering the the options
        for i in range(self.n_options()):
            box, _1, _2 = self.boxframes[i]
            bcolor = (self.highlighted_background_color if i == self.selected_index else self.background_color)
            pygame.draw.rect(self.surface, bcolor, box)
        #drawing the lines
        lwidth = self.inner_frame_dim.width
        lstart = self.outline_size
        for i in range(1, self.n_options):
            cy = (self.inner_frame_dim.y - self.y) + i*self.full_box_height
            pygame.draw.line(self.surface, self.line_color, (lstart, cy), (lstart + lwidth, cy), width=self.line_margin)
        #rendering the text
        for i in range(self.n_options()):
            if (i == self.selected_index):
                graphics.render_rendered_surface_position_tuples(self.surface, self.rendered_highlighted_texts[i])
            else:
                graphics.render_rendered_surface_position_tuples(self.surface, self.rendered_texts[i])
        #rendering the outline
        if self.outline_size > 0:
            pygame.draw.rect(self.surface, self.outline_color, pygame.Rect(0, 0, self.width, self.height), width=self.outline_size)

    def move_up(self) -> None:
        """
        Moves the selected option one up, if nothing is selected it selected option 0.
        """

        if self.state == DropdownMenu.NOTHING_SELECTED:
            self.selected_index = 0
            self.state = DropdownMenu.OPTION_SELECTED
            return

        if self.state in self.move_states:
            self.moves_buffered -= 1

    def move_down(self) -> None:
        """
        Moves the selected option one down, if nothing is selected it selected option 0.
        """

        if self.state == DropdownMenu.NOTHING_SELECTED:
            self.selected_index = 0
            self.state = DropdownMenu.OPTION_SELECTED
            return

        if self.state in self.move_states:
            self.moves_buffered += 1


    def select(self) -> None:
        """
        Starts the select animation.
        """
        #starts the selection process, only if something is selected
        if self.state == DropdownMenu.NOTHING_SELECTED or self.state == DropdownMenu.SELECT_ANIMATION_PLAYING:
            return
        #selects the current selected option
        self.state = DropdownMenu.SELECT_ANIMATION_PLAYING
        self.rtext_copy = self.rendered_highlighted_texts[self.selected_index]
        self.select_clock.start()

    def unselect_options(self) -> None:
        """
        Unselects all options.
        """
        self.selected_index = DropdownMenu.NOTHING_SELECTED_INDEX
        self.moves_buffered = 0
        self.state = DropdownMenu.NOTHING_SELECTED

        self.push_event(DropdownMenu.NewOptionHighlightedEvent(DropdownMenu.NOTHING_SELECTED_INDEX, None))

        self.prerender()

    def select_option(self, index: int) -> None:

        """
        Jumps to the option at the index.
        """

        self.selected_index = index
        self.moves_buffered = 0
        self.state = DropdownMenu.OPTION_SELECTED
        self.prerender()

    def render_select_animation(self) -> None:
        """
        Renders the select animation.
        """

        #what percentage elapsed of the animation duration
        percentage = self.select_clock.elapsed() / self.selected_animation_duration
        #if the percenatge >= 1.0, finish the animation and selection process
        if percentage >= 1.0:
            self.finalize_select_animation()
            return

        else:

            #The animation works by first decreasing the textsize, then increasing it
            if percentage <= 0.5:

                fp = 2*percentage

                cx = self.inner_frame_dim.x - self.x
                cy = self.inner_frame_dim.y - self.y + (self.selected_index) * self.full_box_height
                cw = self.option_box_width
                ch = self.option_box_height

                mx, my = self.text_margins_percentage
                hmx, hmy = self.highlighted_text_margins_percentage

                mxd, myd = hmx + (mx - hmx) * fp, hmy + (my - hmy) * fp


                sframe = pygame.Rect(cx, cy, cw, ch)
                rframe = graphics.apply_margins(sframe, mxd, myd)

                rtext = graphics.render_page_from_chars_color(
                                                                font=self.font,
                                                                page=self.highlighted_options[self.selected_index],
                                                                frame=rframe,
                                                                centered=True,
                                                                vertical_centered=True,
                                                                line_margin_as_percentage=self.in_option_line_margin_p
                                                                )

                self.rendered_highlighted_texts[self.selected_index] = rtext

            else:

                fp = 2 * (percentage - 0.5)

                cx = self.inner_frame_dim.x - self.x
                cy = self.inner_frame_dim.y - self.y + (self.selected_index) * self.full_box_height
                cw = self.option_box_width
                ch = self.option_box_height

                mx, my = self.text_margins_percentage
                hmx, hmy = self.highlighted_text_margins_percentage

                mxd, myd = mx + (hmx - mx) * fp, my + (hmy - my) * fp

                sframe = pygame.Rect(cx, cy, cw, ch)
                rframe = graphics.apply_margins(sframe, mxd, myd)

                rtext = graphics.render_page_from_chars(
                                                        font=self.font,
                                                        page=self.highlighted_options[self.selected_index],
                                                        frame=rframe,
                                                        centered=True,
                                                        vertical_centered=True
                                                        line_margin_as_percentage=self.in_option_line_margin_p
                                                        )

                self.rendered_highlighted_texts[self.selected_index] = rtext



        self.prerender()

    def finalize_select_animation(self) -> None:
        """
        rerenders, then sets the state to option selected, and adds a SELECT_ANIMATION_ENDED event to the event queue
        """

        #getting the data for the event
        selected_index: int = self.selected_index
        selected_option_str: str = graphics.colored_page_to_str(self.highlighted_options[self.selected_index])

        fevent = DropdownMenu.SelectAnimationEndedEvent(selected_index=selected_index, selected_option_str=selected_option_str)
        self.push_event(fevent)

        self.rendered_highlighted_texts[self.selected_index] = self.rtext_copy
        self.state = DropdownMenu.OPTION_SELECTED

        self.prerender()

    @override
    def render(self, screen: pygame.Surface) -> None:
        #renders onto the screen
        screen.blit(self.surface, (self.x, self.y))

    @override
    def tick(self):

        #move then render
        if self.state in self.move_states:
            self.selected_index += self.moves_buffered
            self.selected_index %= self.n_options
            if self.moves_buffered != 0:
                self.push_event(
                                    DropdownMenu.NewOptionHighlightedEvent(
                                                                            self.selected_index,
                                                                            graphics.colored_page_to_str(self.highlighted_options[self.selected_index])
                                                                            )
                                )
            self.moves_buffered = 0
            self.prerender()

        if self.state == DropdownMenu.SELECT_ANIMATION_PLAYING:
            self.render_select_animation()
