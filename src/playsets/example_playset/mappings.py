import os
import importlib
from enum import Enum, auto
import constants

enums = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.enums")
item_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.items")
supporter_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.supporters")
blueprint_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.blueprints")
pack_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.packs")
explorer_module = importlib.import_module(f"{constants.PLAYSETS_FOLDER}.example_playset.explorer")

explorer_mappings = {
                        enums.ExplorerEnums.BASIC_EXPLORER: explorer_module.Basic_Explorer()
}

explorer_cards_mappings = {

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

supporters_mappings = {

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
