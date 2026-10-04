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

        modules.explorer_module = importlib.import_module(f"{playset}.explorer")
        modules.cards_module = importlib.import_module(f"{playset}.cards")
        modules.items_module = importlib.import_module(f"{playset}.items")
        modules.supporters_module = importlib.import_module(f"{playset}.supporters")
        modules.blueprints_module = importlib.import_module(f"{playset}.blueprints")
        modules.packs_module = importlib.import_module(f"{playset}.packs")



    def __init__(self):

        self.explorer_module = None
        self.cards_module = None
        self.items_module = None
        self.supporters_module = None
        self.blueprints_module = None
        self.packs_module = None

        self.tags = None
        self.mappings = None
        self.enums = None
