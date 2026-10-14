from templates.tag_template import *

class General_Card_Tags:

    ITEM_GENERATOR = "Item Generator"
    ITEM_CONSUMER = "Item Consumer"

    HEALING = "Healing"
    HEALING_TOKEN_GENERATOR = "Healing Token Generator"
    HEALING_TOKEN_CONSUMER = "Healing Token Consumer"
    HEALING_TOKEN = "Healing Token"

class Healing_Tag(General_Card_Tag_Template):

    def __init__(self, healing_factor):#healing factor means how much lives are healed
        super().__init__(General_Card_Tags.HEALING)

        self.healing_factor = healing_factor

class Healing_Token(General_Card_Tag_Template):

    def __init__(self):
        super().__init__(General_Card_Tags.HEALING_TOKEN)


class Healing_Token_Generator(General_Card_Tag_Template):

    def __init__(self, amount_generated):
        super().__init__(General_Card_Tags.HEALING_TOKEN_GENERATOR)

        self.amount_generated = amount_generated

class Healing_Token_Consumer(General_Card_Tag_Template):

    def __init__(self, amount_consumed):
        super().__init__(General_Card_Tags.HEALING_TOKEN_CONSUMER)

        self.amount_consumed = amount_consumed

class Item_Generator(General_Card_Tag_Template):

    def __init__(self, items_generated):#items generated is a dict of item_enum: amount
        super().__init__(General_Card_Tags.ITEM_GENERATOR)

        self.items_generated = items_generated

class Item_Consumer(General_Card_Tag_Template):

    def __init__(self, items_consumed):#items consumed is a dict of item_enum: amount
        super().__init__(General_Card_Tags.ITEM_CONSUMER)

        self.items_consumed = items_consumed
