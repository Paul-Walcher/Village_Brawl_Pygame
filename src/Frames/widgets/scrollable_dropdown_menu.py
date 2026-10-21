import pygame

from collections import deque
from copy import deepcopy
import graphics
from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from event_queue_manager import Event
from constants import Colors, Fonts, R_ID
from clock import Clock
from Frames.widgets.dropdown_menu import DropdownMenu
from Frames.widgets.expandable_dropdown_menu import ExpandableDropdownMenu

class ScrollableDropdownMenu(ExpandableDropdownMenu):

    #states
    SCROLLING_UP = R_ID()
    SCROLLING_DOWN = R_ID()


    N_OPTIONS_SHOWN_KEY = "n_options_shown"


    def __init__(
                    self,
                    frame_dim,
                    options,
                    #Options is a dict like:
                    #
                    # {
                    #   (("line1", "line2"), options_shown): {OPTIONS FOR THE NEXT DROPDOWN MENU} //or if there is no Menu its just None
                    #   and one extra key_value pair: "options_shown": n, which
                    #}

                    precalculated_depth_and_max_length=None,#depth == how many dropdown manus follow this one,
                                                            #max_length == number of options in the dropdown menu with the most options
                                                            #only the first dropdown menu needs to calculate this,
                                                            #and can pass the information on
                    dropdown_parent=None, #since this class works recursively, each expandable dropdown menu needs to know which menu it is attached to


                    #for the rest see dropdown_menu.py
                    focus_group="",
                    font=Fonts.MINECRAFT,
                    background_color=Colors.T(Colors.BLACK),
                    highlighted_background_color=Colors.T(Colors.WHITE),
                    text_color=Colors.T(Colors.WHITE),
                    highlighted_text_color=Colors.T(Colors.BLACK),
                    in_option_line_margin=5,#px
                    line_margin=5,#px,
                    line_color = Colors.GRAY,
                    lines_shown = True,
                    outline_size=10,
                    outline_color=Colors.T(Colors.BLACK),
                    text_margins_percentage=(0.4, 0.4),
                    highlighted_text_margins_percentage=(0.1, 0.1),
                    initial_selected_index=-1,
                    selected_animation_duration=800,#ms
                    scrolling_animation_duration=300#ms

                ):

        self.full_options = list(options.keys())
        if ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY in self.full_options:
            self.full_options.remove(ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY)
        self.n_options_shown = -1
        if ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY in options:
            self.n_options_shown = options[ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY]
        else:
            self.n_options_shown = len(options)

        if self.n_options_shown <= 0:
            raise RuntimeError("N options shown must be > 0")

        self.scroll_index = 0

        self.scrolling_animation_duration = scrolling_animation_duration
        self.scrolling_animation_clock = Clock()

        ExpandableDropdownMenu.__init__(
                                            self,
                                            frame_dim=frame_dim,
                                            options=options,
                                            precalculated_depth_and_max_length=precalculated_depth_and_max_length,
                                            dropdown_parent=dropdown_parent,
                                            focus_group=focus_group,
                                            font=font,
                                            background_color=background_color,
                                            highlighted_background_color=highlighted_background_color,
                                            text_color=text_color,
                                            highlighted_text_color=highlighted_text_color,
                                            in_option_line_margin=in_option_line_margin,
                                            line_margin=line_margin,
                                            line_color=line_color,
                                            lines_shown=lines_shown,
                                            outline_size=outline_size,
                                            outline_color=outline_color,
                                            text_margins_percentage=text_margins_percentage,
                                            highlighted_text_margins_percentage=highlighted_text_margins_percentage,
                                            initial_selected_index=initial_selected_index,
                                            selected_animation_duration=selected_animation_duration
                                        )



    def _calculate_depth_and_max_length(self, options):
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
            vlen = len([v for v in option.values() if v != ScrollableDropdownMenu.N_OPTIONS_SHOWN_KEY])
            max_length = max(max_length, vlen)#minus 1 for n_groups shown key
            for v in option.values():
                if type(v) == dict:
                    #if any of the options values is not None, that means its a dropdown menu
                    max_depth = max(max_depth, depth+1)#we need to check max deptg
                    mdepth.append((v, depth+1)) #add the next option to processing

        return max_depth, max_length

    def get_options_n_showed(self):

        return self.full_options[self.scroll_index: self.scroll_index+self.n_options_shown]

    def rerender(self):

        self.scroll_index = 0
        self.options = self.get_options_n_showed()
        #rerendering the dropdown
        DropdownMenu.rerender(self)
        #adding the other dropdown menus
        self.expanded_dropdown_menus = {}
        #we need to cut the frame of the currernt dopdown menu from the frame for the remaining dropdowns
        expanded_frame_dim = self.original_frame_dim.copy()
        expanded_frame_dim.x = self.frame_dim.x + self.frame_dim.width
        expanded_frame_dim.width -= self.frame_dim.width
        #adding dropdown menus recursively
        for key, eoptions in self.dictionary_options.items():
            if type(eoptions) == dict:

                new_dropdown = ScrollableDropdownMenu(
                                                        expanded_frame_dim.copy(),
                                                        options=eoptions.copy(),
                                                        precalculated_depth_and_max_length=(
                                                            self.max_depth - 1,
                                                            self.max_length
                                                        ),
                                                        dropdown_parent=self,
                                                        font=self.font,
                                                        background_color=self.background_color,
                                                        highlighted_background_color=self.highlighted_background_color,
                                                        text_color=self.text_color,
                                                        in_option_line_margin=self.in_option_line_margin,
                                                        highlighted_text_color=self.highlighted_text_color,
                                                        line_margin=self.line_margin,
                                                        line_color=self.line_color,
                                                        lines_shown=self.lines_shown,
                                                        outline_size=self.outline_size,
                                                        outline_color=self.outline_color,
                                                        text_margins_percentage=self.text_margins_percentage,
                                                        highlighted_text_margins_percentage=self.highlighted_text_margins_percentage,
                                                        initial_selected_index=self.selected_index,
                                                        selected_animation_duration=self.selected_animation_duration
                                                    )

                self.expanded_dropdown_menus[key] = new_dropdown #associating the dropdown with the corresponding option


    def tick(self):

        #giving tick command to currently expanded dropdownmenu
        if self.deferred_dropdown_menu is not None:
            self.deferred_dropdown_menu.tick()

        if self.state in self.move_states:
            prev_sindex = self.selected_index
            self.selected_index += self.moves_buffered
            if self.selected_index < 0 and prev_sindex >= 0:
                self.selected_index = 0
                self.state = ScrollableDropdownMenu.SCROLLING_UP
                self.initialize_scrolling_up()
            elif self.selected_index >= self.n_options:
                self.selected_index = self.n_options - 1
                self.state = ScrollableDropdownMenu.SCROLLING_DOWN
                self.initialize_scrolling_down()
            self.moves_buffered = 0
            #after a move, check if we need to show another dropdown menu
            if self.state not in [ScrollableDropdownMenu.SCROLLING_UP, ScrollableDropdownMenu.SCROLLING_DOWN]:
                if self.options[self.selected_index] in self.expanded_dropdown_menus:
                    self.deferred_dropdown_menu = self.expanded_dropdown_menus[self.options[self.selected_index]]
                    self.state = ExpandableDropdownMenu.DEFERRED_MENU_SHOWN
                else:
                    self.deferred_dropdown_menu = None
                    self.state = DropdownMenu.OPTION_SELECTED
            self.prerender()

        elif self.state == DropdownMenu.SELECT_ANIMATION_PLAYING:
            self.render_select_animation()

        elif self.state == ScrollableDropdownMenu.SCROLLING_UP:
            self.scroll_up()

        elif self.state == ScrollableDropdownMenu.SCROLLING_DOWN:
            self.scroll_down()

        #checking events
        if self.deferred_dropdown_menu is not None:
            for event in self.deferred_dropdown_menu.poll_events():
                if event.type == ExpandableDropdownMenu.EventTypes.SELECTION_FINISHED_EVENT:
                    #if we got a selection finished event, append the own current option, then add it to the event queue
                    event.add_selected_name(self.options[self.selected_index])
                    self.event_queue.append(event)


    def initialize_scrolling_up(self):

        if self.scroll_index == 0 or len(self.full_options) <= self.n_options_shown:
            self.state = DropdownMenu.OPTION_SELECTED
            return

        #create new option box
        tmb, htmb = self.text_margin_box.copy(), self.highlighted_text_margin_box.copy()

        tmb.x += self.outline_size
        htmb.x += self.outline_size

        tmb.y += -self.full_box_height + self.outline_size
        htmb.y += -self.full_box_height + self.outline_size


        box = pygame.Rect(self.outline_size,
                            -self.full_box_height + self.outline_size,
                            self.inner_frame_dim.width,
                            self.option_box_height)

        self.boxframes.insert(0, (box, tmb, htmb))
        self.boxframes_copy = [(b.copy(), t.copy(), h.copy()) for b, t, h in self.boxframes]

        page = self.full_options[self.scroll_index-1]
        rtext = graphics.render_page_from_chars(self.font, page, tmb, self.text_color, centered=True, vertical_centered=True, line_margin=self.in_option_line_margin)
        hrtext = graphics.render_page_from_chars(self.font, page, htmb, self.highlighted_text_color, centered=True, vertical_centered=True, line_margin=self.in_option_line_margin)

        self.rendered_texts.insert(0, rtext)
        self.rendered_highlighted_texts.insert(0, hrtext)
        self.rendered_texts_copy = [[(tr.copy(), pos) for tr, pos in rtext] for rtext in self.rendered_texts]
        self.rendered_highlighted_texts_copy = [[(tr.copy(), pos) for tr, pos in rtext] for rtext in self.rendered_highlighted_texts]

        self.n_options += 1 #only temporarily
        self.selected_index = 1

        self.scrolling_animation_clock.start()

    def scroll_up(self):

        percentage = self.scrolling_animation_clock.elapsed() / self.scrolling_animation_duration

        if percentage >= 1.0:
            self.finalize_scrolling_up()
        else:

            scroll_px = int(percentage * self.full_box_height)

            for i in range(self.n_options):

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

    def finalize_scrolling_up(self):

        self.boxframes = self.boxframes_copy[1:]

        self.rendered_texts = self.rendered_texts_copy[:-1]
        self.rendered_texts = [[(text, (x, y+self.full_box_height)) for text, (x, y) in op] for op in self.rendered_texts]

        self.rendered_highlighted_texts = self.rendered_highlighted_texts_copy[:-1]
        self.rendered_highlighted_texts = [[(text, (x, y+self.full_box_height)) for text, (x, y) in op] for op in self.rendered_highlighted_texts]

        self.n_options -= 1
        self.scroll_index -= 1
        self.options = self.get_options_n_showed()

        self.selected_index = 0
        self.state = DropdownMenu.OPTION_SELECTED

    def initialize_scrolling_down(self):

        if self.scroll_index + self.n_options_shown >= len(self.full_options) or len(self.full_options) <= self.n_options_shown:
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

        page = self.full_options[self.scroll_index+self.n_options_shown]
        rtext = graphics.render_page_from_chars(self.font, page, tmb, self.text_color, centered=True, vertical_centered=True, line_margin=self.in_option_line_margin)
        hrtext = graphics.render_page_from_chars(self.font, page, htmb, self.highlighted_text_color, centered=True, vertical_centered=True, line_margin=self.in_option_line_margin)

        self.rendered_texts.append(rtext)
        self.rendered_highlighted_texts.append(hrtext)
        self.rendered_texts_copy = [[(tr.copy(), pos) for tr, pos in rtext] for rtext in self.rendered_texts]
        self.rendered_highlighted_texts_copy = [[(tr.copy(), pos) for tr, pos in rtext] for rtext in self.rendered_highlighted_texts]

        self.n_options += 1 #only temporarily
        self.selected_index = self.n_options - 2

        self.scrolling_animation_clock.start()

    def scroll_down(self):


        percentage = self.scrolling_animation_clock.elapsed() / self.scrolling_animation_duration

        if percentage >= 1.0:
            self.finalize_scrolling_down()
        else:

            scroll_px = int(percentage * self.full_box_height)

            for i in range(self.n_options):

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


    def finalize_scrolling_down(self):

        self.boxframes = self.boxframes_copy[:-1]

        self.rendered_texts = self.rendered_texts_copy[1:]
        self.rendered_texts = [[(text, (x, y-self.full_box_height)) for text, (x, y) in op] for op in self.rendered_texts]

        self.rendered_highlighted_texts = self.rendered_highlighted_texts_copy[1:]
        self.rendered_highlighted_texts = [[(text, (x, y-self.full_box_height)) for text, (x, y) in op] for op in self.rendered_highlighted_texts]

        self.n_options -= 1
        self.scroll_index += 1
        self.options = self.get_options_n_showed()

        self.selected_index = self.n_options - 1
        self.state = DropdownMenu.OPTION_SELECTED
