from constants import Colors

class Renderable_Card:

    def __init__(self,
                name="",
                name_color=Colors.BLACK,
                description="",
                card_image_path="",
                standard_image_path=""
                ):

        self.name = name
        self.name_color = name_color
        self.description = description
        self.card_image_path = card_image_path
        self.standard_image_path = standard_image_path
