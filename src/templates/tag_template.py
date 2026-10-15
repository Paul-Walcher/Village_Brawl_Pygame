from constants import Colors
from abc import abstractmethod, ABC
from templates.type_enums import TypeEnums

class Tag_Template(ABC):
    def __init__(self, type_enum, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):

        self.type_enum = type_enum
        self.own_enum = own_enum

        self.tag_color = tag_color

    def __repr__(self):
        tab_in = " "*len(self.own_enum)
        return f"{self.own_enum}: -"

class General_Card_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.GENERAL_CARD, own_enum, tag_color)

class General_Supporter_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.GENERAL_SUPPORTER, own_enum, tag_color)

class Biome_Card_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.BIOME_CARD, own_enum, tag_color)

class Biome_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.BIOME, own_enum, tag_color)

class Blueprint_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.BLUEPRINT, own_enum, tag_color)

class Boss_Card_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.BOSS_CARD, own_enum, tag_color)

class Boss_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.BOSS, own_enum, tag_color)

class Building_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.BUILDING, own_enum, tag_color)

class Explorer_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.EXPLORER, own_enum, tag_color)

class Explorer_Card_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.EXPLORER_CARD, own_enum, tag_color)

class Item_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.ITEM, own_enum, tag_color)

class Miniboss_Card_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.MINIBOSS_CARD, own_enum, tag_color)

class Miniboss_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.MINIBOSS, own_enum, tag_color)

class Objective_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.OBJECTIVE, own_enum, tag_color)

class Pack_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.PACK, own_enum, tag_color)

class Scenario_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.SCENARIO, own_enum, tag_color)

class Explorer_Supporter_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.EXPLORER_SUPPORTER, own_enum, tag_color)

class Village_Supporter_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.VILLAGE_SUPPORTER, own_enum, tag_color)

class Village_Boss_Card_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.VILLAGE_BOSS_CARD, own_enum, tag_color)

class Village_Boss_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.VILLAGE_BOSS, own_enum, tag_color)

class Village_Card_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.VILLAGE_CARD, own_enum, tag_color)

class Village_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.VILLAGE, own_enum, tag_color)

class Villager_Tag_Template(Tag_Template):

    def __init__(self, own_enum, tag_color=Colors.STANDARD_TEXT_COLOR):
        super().__init__(TypeEnums.VILLAGER, own_enum, tag_color)
