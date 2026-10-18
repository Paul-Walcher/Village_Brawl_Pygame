import pygame

from collections import deque
import graphics
from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from event_queue_manager import Event
from constants import Colors, Fonts, R_ID
from clock import Clock
from Frames.widgets.dropdown_menu import DropdownMenu


class ExpandableDropdownMenu(DropdownMenu):

    DEFERRED_MENU_SHOWN = R_ID()
    FOCUS_DEFERRED = R_ID()

    class EventTypes:

        SELECT_ANIMATION_ENDED = R_ID()
        SELECTION_FINISHED_EVENT = R_ID()

    class SelectionFinishedEvent(Event):

        def __init__(self, idx_list):
            super().__init__(ExpandableDropdownMenu.EventTypes.SELECTION_FINISHED_EVENT, idx_list)
            #idx_list or self.data contains a list with with tuples, where the tuples are the page of the selected
            #where every time the event gets pushed up one dropdo1n menu,
            #a the text of the currently selected option is inserted at 0 into the list
            #e.g data = [("A", "B"), ("V",), ("C",)]

        def add_selected_name(self, name):
            #adds the selected option to the data
            self.data.insert(0, name)



    def __init__(self,
                frame_dim,
                options=None,
                #Options is a dict like:
                #
                # {
                #   ("line1", "line2"): {OPTIONS FOR THE NEXT DROPDOWN MENU} //or if there is no Menu its just None
                #}
                precalculated_depth_and_max_length=None,#depth == how many dropdown manus follow this one,
                                                        #max_length == number of options in the dropdown menu with the most options
                                                        #only the first dropdown menu needs to calculate this,
                                                        #and can pass the information on
                dropdown_parent=None, #since this class works recursively, each expandable dropdown menu needs to know which menu it is attached to


                #for the rest see dropdown_menu.py
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
                selected_animation_duration=800#ms
                ):

        if options is None or len(options) == 0:
            raise RuntimeError("No options provided")

        self.expanded_dropdown_menus = {}   #list of immediate dropdown menus. if an option tuple has a follow up menu,
                                            #the option tuple is the key and the follow up dropdown menu is the value
        self.deferred_dropdown_menu = None  #if no follow up dropdown menu is open, this is None.
                                            #Otherwise contains a reference to the follow up dropdown menu
        self.dropdown_parent = dropdown_parent #parent dropdown menu. is None for the first dropdown menu

        self.dictionary_options = options   #since we use a list to give the options to the parent class to initialize, we need to save the
                                            #dictionary for ourselves
        self.original_frame_dim = frame_dim #the original frame dimension, we split it horizontally for follow up dropdown menus

        #now calculating the depth
        self.max_depth, self.max_length = (self._calculate_depth_and_max_length(options) if precalculated_depth_and_max_length is None else precalculated_depth_and_max_length)

        frame_dim = frame_dim.copy() #getting an copy of the frame dimension
        frame_dim.width = frame_dim.width // self.max_depth #adjusting the frame dimension, splitting horizontally
        frame_dim.height = (frame_dim.height // self.max_length) * len(options) #adjusting the frame dimension based on the maximum options

        #calling the superconstructor
        DropdownMenu.__init__(self,
                        frame_dim,
                        options=list(options.keys()),
                        font=font,
                        background_color=background_color,
                        highlighted_background_color=highlighted_background_color,
                        text_color=text_color,
                        in_option_line_margin=in_option_line_margin,
                        highlighted_text_color=highlighted_text_color,
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
        #we need to move during when we show the deferred menu, and are not in an entered state
        self.move_states.append(ExpandableDropdownMenu.DEFERRED_MENU_SHOWN)

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
            max_length = max(max_length, len(list(option.values())))
            for v in option.values():
                if v is not None:
                    #if any of the options values is not None, that means its a dropdown menu
                    max_depth = max(max_depth, depth+1)#we need to check max deptg
                    mdepth.append((v, depth+1)) #add the next option to processing

        return max_depth, max_length


    def is_deferred(self):
        #returns if this dropdown menu is deferred
        return self.state == ExpandableDropdownMenu.FOCUS_DEFERRED


    def rerender(self):

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
            if eoptions is not None:

                new_dropdown = ExpandableDropdownMenu(
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

    def move_up(self):

        if self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.FOCUS_DEFERRED:
            #if deferred, let the deferred menu handle it
            self.deferred_dropdown_menu.move_up()
        else:
            #handle normally
            DropdownMenu.move_up(self)

    def move_down(self):

        if self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.FOCUS_DEFERRED:
            #if deferred, let the deferred menu handle it
            self.deferred_dropdown_menu.move_down()
        else:
            #handle normally
            DropdownMenu.move_down(self)

    def move_right(self):

        #defer if menu shown and going right
        if self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.DEFERRED_MENU_SHOWN:
            self.state = ExpandableDropdownMenu.FOCUS_DEFERRED
            self.deferred_dropdown_menu.move_up()
        #if it is already deferred, let the next dropdown menu handle it
        elif self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.FOCUS_DEFERRED:
            self.deferred_dropdown_menu.move_right()

    def move_left(self):

        #if the signal to move left arrives, and a deferred menu exists, give the signal to the menu
        if self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.FOCUS_DEFERRED:
            self.deferred_dropdown_menu.move_left()
        else:
            #otherwise, if a parent exists give control back to the parent dropdown menu
            if self.dropdown_parent is not None:
                self.state = DropdownMenu.NOTHING_SELECTED
                self.selected_index = -1
                self.dropdown_parent.state = ExpandableDropdownMenu.DEFERRED_MENU_SHOWN
            else:
                #unfocus after going too far left
                self.unfocus()




    def select(self):

        #if were not in a position to select, return
        if self.state == DropdownMenu.NOTHING_SELECTED or self.state == DropdownMenu.SELECT_ANIMATION_PLAYING\
            or self.state == ExpandableDropdownMenu.DEFERRED_MENU_SHOWN:
            return
        #if deferred, defer the select command
        if self.deferred_dropdown_menu is not None and self.state == ExpandableDropdownMenu.FOCUS_DEFERRED:
            self.deferred_dropdown_menu.select()
        else:
            #selects the current selected option
            self.state = DropdownMenu.SELECT_ANIMATION_PLAYING
            self.select_clock.start()

    def unfocus(self):

        self.deferred_dropdown_menu = None
        self.selected_index = -1
        self.moves_buffered = 0
        self.state = DropdownMenu.NOTHING_SELECTED

        self.prerender()

    def focus_on(self, index):

        self.deferred_dropdown_menu = None
        self.selected_index = index
        self.moves_buffered = 0
        self.state = DropdownMenu.OPTION_SELECTED
        self.prerender()

    def render_select_animation(self):

        #select animation: first half decreases the size to normal text margin, then goes back up

        percentage = self.select_clock.elapsed() / self.selected_animation_duration

        if percentage >= 1.0:
            self.finalize_select_animation()
            return

        else:

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

                rtext = graphics.render_page_from_chars(self.font, self.options[self.selected_index], rframe,
                                                        text_color=self.highlighted_text_color, centered=True,
                                                        vertical_centered=True)

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

                rtext = graphics.render_page_from_chars(self.font, self.options[self.selected_index], rframe,
                                                        text_color=self.highlighted_text_color, centered=True,
                                                        vertical_centered=True)

                self.rendered_highlighted_texts[self.selected_index] = rtext



        self.prerender()



    def finalize_select_animation(self):

        #create the event
        data = self.selected_index
        fevent = ExpandableDropdownMenu.SelectionFinishedEvent([self.options[self.selected_index]])
        self.event_queue.append(fevent)

        if self.deferred_dropdown_menu is None:
            self.state = DropdownMenu.OPTION_SELECTED

        self.rerender()


    def prerender(self):

        DropdownMenu.prerender(self)
        #prerender next menu
        if self.deferred_dropdown_menu is not None:
            self.deferred_dropdown_menu.prerender()



    def render(self, screen):

        self.prerender()
        if self.deferred_dropdown_menu is not None:
            self.deferred_dropdown_menu.render(screen)
        screen.blit(self.surface, (self.x, self.y))


    def tick(self):

        #giving tick command to currently expanded dropdownmenu
        if self.deferred_dropdown_menu is not None:
            self.deferred_dropdown_menu.tick()

        if self.state in self.move_states:
            self.selected_index += self.moves_buffered
            self.selected_index %= self.n_options
            self.moves_buffered = 0
            #after a move, check if we need to show another dropdown menu
            if self.options[self.selected_index] in self.expanded_dropdown_menus:
                self.deferred_dropdown_menu = self.expanded_dropdown_menus[self.options[self.selected_index]]
                self.state = ExpandableDropdownMenu.DEFERRED_MENU_SHOWN
            else:
                self.deferred_dropdown_menu = None
                self.state = DropdownMenu.OPTION_SELECTED
            self.prerender()

        if self.state == DropdownMenu.SELECT_ANIMATION_PLAYING:
            self.render_select_animation()

        #checking events
        if self.deferred_dropdown_menu is not None:
            for event in self.deferred_dropdown_menu.poll_events():
                if event.type == ExpandableDropdownMenu.EventTypes.SELECTION_FINISHED_EVENT:
                    #if we got a selection finished event, append the own current option, then add it to the event queue
                    event.add_selected_name(self.options[self.selected_index])
                    self.event_queue.append(event)
