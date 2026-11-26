"""
This file provides the featurestate, used for
the renderable card listviewer.
"""
from __future__ import annotations
from typing import Type, Any, Callable, override

class FeatureState:
    """
    This class provides the variables for the features,
    defining what is possible and what not.
    """

    def __init__(self):

        # all state variables
        self.group_selection_enabled: bool = True
        self.group_creation_enabled: bool = True
        self.group_deletion_enabled: bool = True
        self.group_importing_enabled: bool = True
        # if the info panel for the main list is shown,
        self.main_list_state_info_panel_shown: bool = True
        # that depicts what actions can be carried out in the main list.
        # main list states

        # info state is always enabled
        self.selection_main_list_state_enabled: bool = True
