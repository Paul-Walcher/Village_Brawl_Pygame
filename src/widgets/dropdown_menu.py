import pygame

import graphics
from widgets.widget import Widget
from event_queue_manager import Event
from constants import Colors, Fonts
from clock import Clock


class DropdownMenu(Widget):

    NOTHING_SELECTED = 0
    OPTION_SELECTED = 1
    SELECTED_ANIMATION_PLAYING = 2

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
                text_margins_percentage=(0.3, 0.3),
                highlighted_text_margins_percentage=(0.2, 0.2),
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

        self.selected_index = initial_selected_index
        self.last_selected_index = initial_selected_index

        self.state = (DropdownMenu.NOTHING_SELECTED if self.selected_index == -1 else DropdownMenu.OPTION_SELECTED)

        self.rendered_texts = []
        self.rendered_highlighted_texts = []
        self.option_frames = []

        self.moves_buffered = 0
        self.move_states = [DropdownMenu.NOTHING_SELECTED, DropdownMenu.OPTION_SELECTED]

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
        pass
