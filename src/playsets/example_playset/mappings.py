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

card_mappings = {

}

item_mappings = {

}

supporter_mappings = {

}


blueprint_mappings = {

}

pack_mappings = {

}

village_mappings = {

}

building_mappings = {

}

villager_mappings = {

}
