from templates.tag_template import *

class General_Card_Tags:

    ITEM_GENERATOR = "Item Generator"
    ITEM_CONSUMER = "Item Consumer"

    HEALING = "Healing"
    HEALING_TOKEN_GENERATOR = "Healing Token Generator"
    HEALING_TOKEN_CONSUMER = "Healing Token Consumer"
    HEALING_TOKEN = "Healing Token"

#colors
HEALING_COLOR = (0, 255, 0)
ITEM_COLOR = (0, 0, 255)

class Healing_Tag(General_Card_Tag_Template):

    def __init__(self, healing_factor):#healing factor means how much lives are healed
        super().__init__(General_Card_Tags.HEALING, HEALING_COLOR)

        self.healing_factor = healing_factor

    def __repr__(self):
        return f"{self.own_enum}: Healing Factor = {self.healing_factor}"

class Healing_Token(General_Card_Tag_Template):

    def __init__(self):
        super().__init__(General_Card_Tags.HEALING_TOKEN, HEALING_COLOR)


class Healing_Token_Generator(General_Card_Tag_Template):

    def __init__(self, amount_generated):
        super().__init__(General_Card_Tags.HEALING_TOKEN_GENERATOR, HEALING_COLOR)

        self.amount_generated = amount_generated

    def __repr__(self):
        return f"{self.own_enum}: Amount Generated = {self.amount_generated}"

class Healing_Token_Consumer(General_Card_Tag_Template):

    def __init__(self, amount_consumed):
        super().__init__(General_Card_Tags.HEALING_TOKEN_CONSUMER, HEALING_COLOR)

        self.amount_consumed = amount_consumed

    def __repr__(self):
        return f"{self.own_enum}: Amount Consumed = {self.amount_consumed}"

class Item_Generator(General_Card_Tag_Template):

    def __init__(self, items_generated):#items generated is a dict of item_enum: amount
        super().__init__(General_Card_Tags.ITEM_GENERATOR, ITEM_COLOR)

        self.items_generated = items_generated

    def __repr__(self):
        return f"{self.own_enum}: Items Generated = {self.items_generated}"

class Item_Consumer(General_Card_Tag_Template):

    def __init__(self, items_consumed):#items consumed is a dict of item_enum: amount
        super().__init__(General_Card_Tags.ITEM_CONSUMER, ITEM_COLOR)

        self.items_consumed = items_consumed

    def __repr__(self):
        return f"{self.own_enum}: Items Consumed = {self.amount_generated}"
