import pygame

import graphics
from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from event_queue_manager import Event
from constants import Colors, Fonts, R_ID
from clock import Clock


class DropdownMenu(Frame):

    #Available Options

    #Nothing selected means nothing will be highlighted
    NOTHING_SELECTED = R_ID()
    #option selected means the currently selected option will be highlighted
    OPTION_SELECTED = R_ID()
    #Means the selection animation is playing, and the selection progress is going on
    SELECT_ANIMATION_PLAYING = R_ID()

    class EventTypes:

        SELECT_ANIMATION_ENDED = R_ID() #iniicates the selection animation is over,
                                        #and the selection process finished

    def __init__(self,
                frame_dim, #dimensions into which the dropdown menu gets rendered
                options=None,   #list of lines of options, where each line is a list of sentences
                                #example: options=[["Option 1"], ["This line is long", "so it gets broken up"]]
                focus_group="",
                font=Fonts.MINECRAFT, #font for the option text
                background_color=Colors.T(Colors.BLACK), #background color for unhighlighted option boxes
                highlighted_background_color=Colors.T(Colors.WHITE), #background color for highlighted option boxes
                text_color=Colors.T(Colors.WHITE), #colors of the text for an option that is not highlighted
                highlighted_text_color=Colors.T(Colors.BLACK), #color for the text that is selected
                in_option_line_margin=5,#px, the distance between lines inside an option box
                line_margin=5,#px, the margin between lines for the option text
                line_color = Colors.GRAY, #color of the line dividing the options
                lines_shown = True, #decides if the dividing line is shown or not
                outline_size=5, #px, size of the outline of the dropdown menu
                outline_color=Colors.T(Colors.WHITE), #color of the outline of the dropdown menu
                text_margins_percentage=(0.4, 0.4), #means the text will be moved in by text_margins_percentage / 2
                highlighted_text_margins_percentage=(0.1, 0.1), #if the text is highlighted, the box of it
                                                                #should not be moved in and made smaller as much
                initial_selected_index=-1, #what will initially be selected. if initial_selected_index==-1, nothing is selected at first
                selected_animation_duration=800#ms, #how long the selection animation plays
                ):

        if options is None or len(options) == 0:
            raise RuntimeError("No options provided")

        super().__init__(FrameEnums.DROPDOWN_MENU_WIDGET, None, frame_dim, focus_group=focus_group)

        #Assigning the initial values
        self.options = options
        self.selected_index = initial_selected_index
        self.font = font
        self.background_color = background_color
        self.highlighted_background_color = highlighted_background_color
        self.text_color = text_color
        self.highlighted_text_color = highlighted_text_color
        self.in_option_line_margin = in_option_line_margin
        self.line_margin = line_margin
        self.line_color = line_color
        self.lines_shown = lines_shown
        self.outline_size = outline_size
        self.outline_color = outline_color
        self.text_margins_percentage = text_margins_percentage
        self.highlighted_text_margins_percentage = highlighted_text_margins_percentage
        self.selected_animation_duration = selected_animation_duration

        #additional variables

        #the surface onto which everything will be rendered
        self.surface = None
        #inner_frame_dim describes the frame dimension after removing the outline
        self.inner_frame_dim = None
        #number of options available
        self.n_options = len(self.options)
        #width of the option box, which shows the text for one option
        self.option_box_width = self.width
        #height of the option box. is set to 0, gets calculated in rerender()
        self.option_box_height = 0
        #placeholder for the frame dimension rectangle inside an option box after applying
        #the text margin
        self.text_margin_box = None
        #same as text_margin_box but for a option box that is highlighted
        self.highlighted_text_margin_box = None
        #height of a option box
        self.full_box_height = 0
        #list of the dimension rects of the option boxes.
        #each element is a tuple: (option_box_dim, normal_text_dim, highlighted_text_dim)
        self.boxframes = []
        #the state of the dropdown menu
        self.state = (DropdownMenu.NOTHING_SELECTED if self.selected_index == -1 else DropdownMenu.OPTION_SELECTED)
        #container for the rendered option texts
        self.rendered_texts = []
        #container for the rendered highlighted texts. The highlighted
        #text surfaces will be prerendered even if nothing is currently selected
        self.rendered_highlighted_texts = []
        #buffer for the up/down moves
        self.moves_buffered = 0
        #states in which moving up or down is possible
        self.move_states = [DropdownMenu.OPTION_SELECTED]
        #clock for the select animation
        self.select_clock = Clock()

        #start rerendering
        self.rerender()

    def rerender(self):
        #redraws and resets the entire dropdownmenu

        #resetting all internal variables
        self.moves_buffered = 0
        self.rendered_texts = []
        self.rendered_highlighted_texts = []
        self.boxframes = []
        self.state = (DropdownMenu.NOTHING_SELECTED if self.selected_index == -1 else DropdownMenu.OPTION_SELECTED)
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.n_options = len(self.options)
        #calculating the inner frame without the outline
        self.inner_frame_dim = pygame.Rect(self.x + self.outline_size, self.y + self.outline_size,
                                                        self.width - 2*self.outline_size, self.height - 2*self.outline_size)
        #height available without the dividing lines
        no_lines_height = self.inner_frame_dim.height - (self.n_options - 1) * self.line_margin
        #calculating the option box dimensions
        self.option_box_width = self.inner_frame_dim.width
        self.option_box_height = no_lines_height // self.n_options
        self.full_box_height = self.inner_frame_dim.height // self.n_options
        #calculating the text margin boxes
        self.text_margin_box = graphics.apply_margins(pygame.Rect(0, 0, self.option_box_width, self.option_box_height), *self.text_margins_percentage)
        self.highlighted_text_margin_box = graphics.apply_margins(pygame.Rect(0, 0, self.option_box_width, self.option_box_height), *self.highlighted_text_margins_percentage)
        #the topleft corner of the current option box
        cx = self.outline_size
        cy = self.outline_size

        for page in self.options:
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
            rtext = graphics.render_page_from_chars(self.font, page, tmb, self.text_color, centered=True, vertical_centered=True, line_margin=self.in_option_line_margin)
            hrtext = graphics.render_page_from_chars(self.font, page, htmb, self.highlighted_text_color, centered=True, vertical_centered=True, line_margin=self.in_option_line_margin)
            self.rendered_texts.append(rtext)
            self.rendered_highlighted_texts.append(hrtext)
            #increasing the height for the next option frame
            cy += self.full_box_height

        #prerendering onto self.surface
        self.prerender()

    def prerender(self):
        #renders everything onto self.surface

        #filling the surface
        self.surface.fill(self.background_color)
        #rendering the the options
        for i in range(self.n_options):
            box, _1, _2 = self.boxframes[i]
            bcolor = (self.highlighted_background_color if i == self.selected_index else self.background_color)
            pygame.draw.rect(self.surface, bcolor, box)
        #drawing the lines
        lwidth = self.inner_frame_dim.width
        lstart = 0
        for i in range(1, self.n_options):
            cy = (self.inner_frame_dim.y - self.y) + i*self.option_box_height
            pygame.draw.line(self.surface, self.line_color, (lstart, cy), (lstart + lwidth, cy), width=int(0.025 * self.option_box_height))
        #rendering the text
        for i in range(self.n_options):
            if (i == self.selected_index):
                for text, pos in self.rendered_highlighted_texts[i]:
                        self.surface.blit(text, pos)
            else:
                for text, pos in self.rendered_texts[i]:
                    self.surface.blit(text, pos)
        #rendering the outline
        if self.outline_size > 0:
            pygame.draw.rect(self.surface, self.outline_color, pygame.Rect(0, 0, self.width, self.height), width=self.outline_size)


    def move_up(self):
        #moves the selected option one up, wraps around if necessary

        if self.state == DropdownMenu.NOTHING_SELECTED:
            self.selected_index = 0
            self.state = DropdownMenu.OPTION_SELECTED
            return
        if self.state in self.move_states:
            self.moves_buffered -= 1

    def move_down(self):
        #moves the selected option one down, wraps around if necessary

        if self.state == DropdownMenu.NOTHING_SELECTED:
            self.selected_index = self.n_options-1
            self.state = DropdownMenu.OPTION_SELECTED
            return
        if self.state in self.move_states:
            self.moves_buffered += 1


    def select(self):
        #starts the selection process, only if something is selected
        if self.state == DropdownMenu.NOTHING_SELECTED or self.state == DropdownMenu.SELECT_ANIMATION_PLAYING:
            return
        #selects the current selected option
        self.state = DropdownMenu.SELECT_ANIMATION_PLAYING
        self.select_clock.start()

    def unfocus(self):
        #resets the state to nothing focused

        self.selected_index = -1
        self.moves_buffered = 0
        self.state = DropdownMenu.NOTHING_SELECTED

        self.prerender()

    def focus_on(self, index):
        #focuses on the option at the given index

        self.selected_index = index
        self.moves_buffered = 0
        self.state = DropdownMenu.OPTION_SELECTED
        self.prerender()

    def render_select_animation(self):
        #calculates the select animation

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
        #rerenders, then sets the state to option selected, and adds a SELECT_ANIMATION_ENDED event to the event queue

        data = self.selected_index
        fevent = Event(DropdownMenu.EventTypes.SELECT_ANIMATION_ENDED, data)
        self.event_queue.append(fevent)
        self.state = DropdownMenu.OPTION_SELECTED
        self.rerender()

    def render(self, screen):
        #renders onto the screen

        self.prerender()
        screen.blit(self.surface, (self.x, self.y))


    def tick(self):

        #move then render
        if self.state in self.move_states:
            self.selected_index += self.moves_buffered
            self.selected_index %= self.n_options
            self.moves_buffered = 0
            self.prerender()

        if self.state == DropdownMenu.SELECT_ANIMATION_PLAYING:
            self.render_select_animation()
