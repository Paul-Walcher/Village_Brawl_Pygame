"""
Loads the modules
"""
import importlib
from constants import PLAYSETS_FOLDER

class Modules:

    @staticmethod
    def load_playset(playset_name):

        #loading the modules
        playset = f"{PLAYSETS_FOLDER}.{playset_name}"

        modules = Modules()

        modules.biome_cards_module = importlib.import_module(f"{playset}.biome_cards")
        modules.biomes_module = importlib.import_module(f"{playset}.biomes")
        modules.blueprints_module = importlib.import_module(f"{playset}.blueprints")
        modules.boss_cards_module = importlib.import_module(f"{playset}.boss_cards")
        modules.bosses_module = importlib.import_module(f"{playset}.bosses")
        modules.buildings_module = importlib.import_module(f"{playset}.buildings")
        modules.explorer_cards_module = importlib.import_module(f"{playset}.explorer_cards")
        modules.explorer_module = importlib.import_module(f"{playset}.explorer")
        modules.items_module = importlib.import_module(f"{playset}.items")
        modules.miniboss_cards_module = importlib.import_module(f"{playset}.miniboss_cards")
        modules.minibosses_module = importlib.import_module(f"{playset}.minibosses")
        modules.objectives_module = importlib.import_module(f"{playset}.objectives")
        modules.packs_module = importlib.import_module(f"{playset}.packs")
        modules.scenarios_module = importlib.import_module(f"{playset}.scenarios")
        modules.supporters_module = importlib.import_module(f"{playset}.supporters")
        modules.village_boss_cards_module = importlib.import_module(f"{playset}.village_boss_cards")
        modules.village_bosses_module = importlib.import_module(f"{playset}.village_bosses")
        modules.village_cards_module = importlib.import_module(f"{playset}.village_cards")
        modules.village_module = importlib.import_module(f"{playset}.village")
        modules.villagers_module = importlib.import_module(f"{playset}.villagers")

        modules.tags = importlib.import_module(f"{playset}.tags")
        modules.mappings = importlib.import_module(f"{playset}.mappings")
        modules.enums = importlib.import_module(f"{playset}.enums")

        return modules



    def __init__(self):

        self.biome_cards_module = None
        self.biomes_module = None
        self.blueprints_module  = None
        self.boss_cards_module = None
        self.bosses_module = None
        self.buildings_module = None
        self.explorer_cards_module = None
        self.explorer_module = None
        self.items_module = None
        self.miniboss_cards_module = None
        self.minibosses_module = None
        self.objectives_module = None
        self.packs_module = None
        self.scenarios_module = None
        self.supporters_module = None
        self.village_boss_cards_module = None
        self.village_bosses_module = None
        self.village_cards_module = None
        self.village_module = None
        self.villagers_module = None

        self.tags = None
        self.mappings = None
        self.enums = None
