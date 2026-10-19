import os
import importlib
from enum import Enum, auto
import constants

biome_cards_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.biome_cards")
biomes_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.biomes")
blueprints_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.blueprints")
boss_cards_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.boss_cards")
bosses_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.bosses")
buildings_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.buildings")
explorer_cards_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.explorer_cards")
explorer_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.explorer")
items_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.items")
miniboss_cards_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.miniboss_cards")
minibosses_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.minibosses")
objectives_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.objectives")
packs_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.packs")
scenarios_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.scenarios")
explorer_supporters_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.explorer_supporters")
village_boss_cards_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.village_boss_cards")
village_bosses_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.village_bosses")
village_cards_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.village_cards")
village_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.village")
villagers_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.villagers")
village_supporters_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.village_supporters")

tags = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.tags")
enums = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.enums")

explorer_mappings = {
                        enums.ExplorerEnums.BASIC_EXPLORER: explorer_module.Basic_Explorer
}

explorer_cards_mappings = {
                            enums.ExplorerCardEnums.EXAMPLE_CARD_1: explorer_cards_module.Example_Card_1,
                            enums.ExplorerCardEnums.EXAMPLE_CARD_2: explorer_cards_module.Example_Card_2,
                            enums.ExplorerCardEnums.EXAMPLE_CARD_3: explorer_cards_module.Example_Card_3,
                            enums.ExplorerCardEnums.EXAMPLE_CARD_4: explorer_cards_module.Example_Card_4,
                            enums.ExplorerCardEnums.EXAMPLE_CARD_5: explorer_cards_module.Example_Card_5,
                            enums.ExplorerCardEnums.EXAMPLE_CARD_6: explorer_cards_module.Example_Card_6,
                            enums.ExplorerCardEnums.EXAMPLE_CARD_7: explorer_cards_module.Example_Card_7,
                            enums.ExplorerCardEnums.EXAMPLE_CARD_8: explorer_cards_module.Example_Card_8,
                            enums.ExplorerCardEnums.EXAMPLE_CARD_9: explorer_cards_module.Example_Card_9,
                            enums.ExplorerCardEnums.EXAMPLE_CARD_10: explorer_cards_module.Example_Card_10,

                            enums.ExplorerCardEnums.SMALL_REST: explorer_cards_module.Small_Rest
}

village_cards_mappings = {

}

village_boss_cards_mappings = {

}

miniboss_cards_mappings = {

}

boss_cards_mappings = {

}

items_mappings = {

}

explorer_supporters_mappings = {

}

village_supporters_mappings = {

}


blueprints_mappings = {

}

packs_mappings = {

}

village_mappings = {

}

buildings_mappings = {

}

villagers_mappings = {

}

biome_cards_mappings = {

}

biomes_mappings = {

}

minibosses_mappings = {

}

objectives_mappings = {

}

scenarios_mappings = {

}

bosses_mappings = {

}

village_bosses_mappings = {

}
