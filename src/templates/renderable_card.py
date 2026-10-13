from constants import Colors, Fonts
import graphics

class Renderable_Card:

    def __init__(self,
                name="",
                name_color=Colors.BLACK,
                description="",
                description_color=None, #if this is given, it is a list of [(text, color), ] for rendering
                card_image_path="",
                standard_image_path="",
                description_line_length=40,
                description_page_size=5,
                width_to_height_ratio = 5/7
                ):

        self.name = name
        self.name_color = name_color
        self.__description = description
        self.card_image_path = card_image_path
        self.standard_image_path = standard_image_path
        self.__description_color = None
        self.__description_line_length = description_line_length
        self.__description_page_size = description_page_size

        self.description_pages = graphics.page_by_chars(self.__description, self.__description_line_length, self.__description_page_size)
        self.description_pages_color = self.description_color
        if self.description_pages_color is not None:
            self.description_pages_color = graphics.page_by_chars_color(self.__description_color, self.__description_line_length, self.__description_page_size)

        self.n_pages = len(self.description_pages)
        self.n_pages_color = (len(self.description_pages_color) if self.description_pages_color is not None else -1)

        self.width_to_height_ratio = width_to_height_ratio

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, desc):

        self.__description = desc
        self.description_pages = graphics.page_by_chars(self.__description, self.__description_line_length, self.__description_page_size)

        self.n_pages = len(self.description_pages)
        self.n_pages_color = (len(self.description_pages_color) if self.description_pages_color is not None else -1)

    @property
    def description_color(self):
        return self.__description_color

    @description_color.setter
    def description_color(self, desc):

        self.__description_color = desc
        self.description_pages_color = graphics.page_by_chars_color(self.__description_color, self.__description_line_length, self.__description_page_size)

        self.n_pages = len(self.description_pages)
        self.n_pages_color = (len(self.description_pages_color) if self.description_pages_color is not None else -1)

    @property
    def description_line_length(self):
        return self.__description_line_length

    @description_line_length.setter
    def description_line_length(self, ll):

        self.__description_line_length = ll

        self.description_pages = graphics.page_by_chars(self.__description, self.__description_line_length, self.__description_page_size)
        if self.description_pages_color is not None:
            self.description_pages_color = graphics.page_by_chars_color(self.__description_color, self.__description_line_length, self.__description_page_size)

        self.n_pages = len(self.description_pages)
        self.n_pages_color = (len(self.description_pages_color) if self.description_pages_color is not None else -1)

    @property
    def description_page_size(self):
        return self.__description_page_size

    @description_page_size.setter
    def description_page_size(self, ps):

        self.__description_page_size = ps

        self.description_pages = graphics.page_by_chars(self.__description, self.__description_line_length, self.__description_page_size)
        if self.description_pages_color is not None:
            self.description_pages_color = graphics.page_by_chars_color(self.__description_color, self.__description_line_length, self.__description_page_size)

        self.n_pages = len(self.description_pages)
        self.n_pages_color = (len(self.description_pages_color) if self.description_pages_color is not None else -1)

    def render_name(self, target_frame_dim, font=Fonts.MINECRAFT, line_margin=5):

        fsize = graphics.get_fontsize(font, [self.name], line_margin)
        surf = graphics.render_text(font, fsize, self.name, self.name_color)
        return surf

    def render_description_page(self, page_index, target_frame_dim, font=Fonts.MINECRAFT, color=Colors.BLACK, centered=True,
                                vertical_centered=True, line_margin=5):

        return graphics.render_page_from_chars(font, self.description_pages[page_index], target_frame_dim,
                                                color, centered=centered, vertical_centered=vertical_centered, line_margin=line_margin
                                                )


    def render_description_page_color(self, page_index, target_frame_dim, font=Fonts.MINECRAFT, backup_color=Colors.BLACK, centered=True,
                                vertical_centered=True, line_margin=5):

        if self.description_pages_color is None:
            return None

        return graphics.render_page_from_chars_color(font, self.description_pages_color[page_index], target_frame_dim,
                                                backup_color, centered=centered, vertical_centered=vertical_centered, line_margin=line_margin
                                                )
