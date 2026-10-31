"""
Context data instances are passed from frame to frame.
"""
from __future__ import annotations
from modules import Modules

class ContextData:
    """
    Saves all important data passed from frame to frame.
    """

    def __init__(
                    self,
                    mouse_enabled: bool = False,
                    #data
                    current_playset: str = None,
                    current_savefile_name: str = None,
                    modules: Modules = None
                ):

        self.mouse_enabled: bool = mouse_enabled
        """
        If the mouse events are enabled or not.
        """
        #data
        self.current_playset: str = current_playset
        """
        The current playset that is loaded.
        """
        self.current_savefile_name: str = current_savefile_name
        """
        Name of the current savefile
        """
        self.modules: Modules = modules
        """
        Loaded modules. See modules.py
        """
