import pygame

import graphics
from widgets.widget import Widget
from event_queue_manager import Event
from constants import Colors, Fonts
from clock import Clock


class DropdownMenu(Widget):

    NOTHING_SELECTED = 0
    OPTION_SELECTED = 1
    SELECT_ANIMATION_PLAYING = 2

    class EventTypes:

        SELECT_ANIMATION_ENDED = 0

    def __init__(self,
                frame_dim,
                options=None,#list of lines of options, where each line is a list of sentences
                font=Fonts.MINECRAFT,
                background_color=Colors.T(Colors.BLACK),
                highlighted_background_color=Colors.T(Colors.DARK_SLATE_GRAY),
                text_color=Colors.T(Colors.WHITE),
                in_option_line_margin=5,#px
                highlighted_text_color=Colors.T(Colors.YELLOW),
                line_margin=5,#px,
                line_color = Colors.GRAY,
                lines_shown = True,
                outline_size=0,
                outline_color=Colors.T(Colors.BLACK),
                text_margins_percentage=(0.4, 0.4),
                highlighted_text_margins_percentage=(0.1, 0.1),
                initial_selected_index=-1,
                selected_animation_duration=800#ms
                ):

        if options is None or len(options) == 0:
            raise RuntimeError("No options provided")

        super().__init__(frame_dim)

        self.options = options

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

        self.surface = None
        self.highlight_inside_frame_dim = None
        self.n_options = 0
        self.option_box_width = self.width
        self.option_box_height = 0

        self.text_margin_box = None
        self.highlighted_text_margin_box = None

        self.selected_animation_duration = selected_animation_duration

        self.selected_index = initial_selected_index
        self.last_selected_index = initial_selected_index

        self.state = (DropdownMenu.NOTHING_SELECTED if self.selected_index == -1 else DropdownMenu.OPTION_SELECTED)

        self.rendered_texts = []
        self.rendered_highlighted_texts = []
        self.option_frames = []

        self.moves_buffered = 0
        self.move_states = [DropdownMenu.OPTION_SELECTED]

        self.select_clock = Clock()

        self.rerender()


    def move_up(self):

        if self.state == DropdownMenu.NOTHING_SELECTED:
            self.selected_index = 0
            self.state = DropdownMenu.OPTION_SELECTED
            return
        if self.state in self.move_states:
            self.moves_buffered -= 1

    def move_down(self):

        if self.state == DropdownMenu.NOTHING_SELECTED:
            self.selected_index = self.n_options-1
            self.state = DropdownMenu.OPTION_SELECTED
            return
        if self.state in self.move_states:
            self.moves_buffered += 1


    def select(self):
        if self.state == DropdownMenu.NOTHING_SELECTED or self.state == DropdownMenu.SELECT_ANIMATION_PLAYING:
            return
        #selects the current selected option
        self.state = DropdownMenu.SELECT_ANIMATION_PLAYING
        self.select_clock.start()

    def unfocus(self):

        self.selected_index = -1
        self.moves_buffered = 0
        self.state = DropdownMenu.NOTHING_SELECTED

        self.render()

    def focus_on(self, index):

        self.selected_index = index
        self.moves_buffered = 0
        self.state = DropdownMenu.OPTION_SELECTED
        self.render()

    def render_select_animation(self):

        percentage = self.select_clock.elapsed() / self.selected_animation_duration

        if percentage >= 1.0:
            self.finalize_select_animation()
            return

        else:

            if percentage <= 0.5:

                fp = 2*percentage

                cx = self.highlight_inside_frame_dim.x - self.x
                cy = self.highlight_inside_frame_dim.y - self.y + (self.selected_index) * self.full_box_height
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

                cx = self.highlight_inside_frame_dim.x - self.x
                cy = self.highlight_inside_frame_dim.y - self.y + (self.selected_index) * self.full_box_height
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



        self.render()



    def finalize_select_animation(self):

        data = self.selected_index
        fevent = Event(DropdownMenu.EventTypes.SELECT_ANIMATION_ENDED, data)
        self.event_queue.append(fevent)

        self.state = DropdownMenu.OPTION_SELECTED

        self.rerender()

    def render(self):

        self.surface.fill(self.background_color)

        #rendering outline
        if self.outline_size > 0:
            pygame.draw.rect(self.surface, self.outline_color, self.frame_dim, width=self.outline_size)

        for i in range(self.n_options):

            box, _1, _2 = self.boxframes[i]
            bcolor = (self.highlighted_background_color if i == self.selected_index else self.background_color)

            pygame.draw.rect(self.surface, bcolor, box)

        #drawing the lines#
        lwidth = int(self.highlight_inside_frame_dim.width * 0.8)
        lstart = int(self.highlight_inside_frame_dim.width * 0.1)

        for i in range(1, self.n_options):

            cy = (self.highlight_inside_frame_dim.y - self.y) + i*self.option_box_height
            pygame.draw.line(self.surface, self.line_color, (lstart, cy), (lstart + lwidth, cy))

        for i in range(self.n_options):
            if (i == self.selected_index):
                for text, pos in self.rendered_highlighted_texts[i]:
                        self.surface.blit(text, pos)
            else:
                for text, pos in self.rendered_texts[i]:
                    self.surface.blit(text, pos)



    def rerender(self):

        self.moves_buffered = 0
        self.rendered_texts = []
        self.rendered_highlighted_texts = []
        self.option_frames = []
        self.boxframes = []

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.highlight_inside_frame_dim = pygame.Rect(self.x + self.outline_size, self.y + self.outline_size,
                                                        self.width + 2*self.outline_size, self.height + 2*self.outline_size)

        self.n_options = len(self.options)

        hifd = self.highlight_inside_frame_dim

        no_lines_height = hifd.height - (self.n_options - 1) * self.line_margin

        self.option_box_width = hifd.width
        self.option_box_height = no_lines_height // self.n_options
        self.full_box_height = hifd.height // self.n_options

        self.text_margin_box = graphics.apply_margins(pygame.Rect(0, 0, self.option_box_width, self.option_box_height), *self.text_margins_percentage)
        self.highlighted_text_margin_box = graphics.apply_margins(pygame.Rect(0, 0, self.option_box_width, self.option_box_height), *self.highlighted_text_margins_percentage)

        cx = self.highlight_inside_frame_dim.x - self.x
        cy = self.highlight_inside_frame_dim.y - self.y

        for page in self.options:

            tmb, htmb = self.text_margin_box.copy(), self.highlighted_text_margin_box.copy()
            tmb.x += cx
            tmb.y += cy
            htmb.x += cx
            htmb.y += cy

            box = pygame.Rect(cx, cy, hifd.width, self.option_box_height)

            self.boxframes.append((box, tmb, htmb))


            rtext = graphics.render_page_from_chars(self.font, page, tmb, self.text_color, centered=True, vertical_centered=True, line_margin=self.in_option_line_margin)
            hrtext = graphics.render_page_from_chars(self.font, page, htmb, self.highlighted_text_color, centered=True, vertical_centered=True, line_margin=self.in_option_line_margin)

            self.rendered_texts.append(rtext)
            self.rendered_highlighted_texts.append(hrtext)

            cy += self.full_box_height


        self.state = (DropdownMenu.NOTHING_SELECTED if self.selected_index == -1 else DropdownMenu.OPTION_SELECTED)

        self.render()


    def get_surfaces(self):

        return [self.surface]

    def get_surfaces_with_position(self):

        return [(self.surface, (self.x, self.y))]


    def tick(self):

        if self.state in self.move_states:
            self.selected_index += self.moves_buffered
            self.selected_index %= self.n_options
            self.moves_buffered = 0
            self.render()
        if self.state == DropdownMenu.SELECT_ANIMATION_PLAYING:
            self.render_select_animation()
