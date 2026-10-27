from __future__ import annotations
from typing import Callable, Any
from types import ModuleType

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
import constants
from modules import Modules
from templates.type_enums import TypeEnums
from Frames.frame_enums import FrameEnums
from phases import Phases, phase_transition_t, PhaseInfo


class PlaysetEntity(Frame):

    """
    Describes a card/entity that needs to be rendered to the screen,
    and does actions every frame, needing to be updated using tick().
    """

    @staticmethod
    def info():
        pass

    def __init__(   self,
                    modules: Modules,
                    entity_type: TypeEnums,
                    frame_enum: FrameEnums = FrameEnums.PLAYSET_ENTITY,
                    data: Any = None,
                    frame_dim: pygame.Rect = constants.FULLSCREEN,
                    parent_frame: Frame = None
                    ):

        super().__init__(frame_enum, data, frame_dim, parent_frame)

        self.modules: Modules = modules
        """
        Module reference, for individual loading modules from the playset.
        """
        self.mappings: ModuleType = modules.mappings
        """
        Direct reference to the mappings.
        Defined for readability.
        """
        self.enums: ModuleType = modules.enums
        """
        Direct reference to the enums.
        Defined for readability
        """
        self.tags: ModuleType = modules.tags
        """
        Direct reference to the tags.
        Defined for readability
        """
        self._prev_phase: Phases = None
        """
        Saves the previous phase for detecting phase transitions.
        """
        self.entity_type: TypeEnums = entity_type
        """
        The type of this entity.
        """
        self._transition_callbacks: dict[ phase_transition_t, list[Callable[ [Phases, Phases, PhaseInfo] , None]] ] = {}
        """
        A dictionary storing the functions called when the phase changes.
        If (prev_phase, new_phase) in phase_change_functions, all stored functions will be executed there.
        """

    def tick(
                self,
                phaseinfo: PhaseInfo
                ) -> Frame:

        """
        Tick function for the entity.
        """

        self.execute_phase_change(phaseinfo)

        return self

    def render(self, screen: pygame.Surface) -> None:
        """
        Render function. The default is drawing nothing.
        """
        pass

    def execute_phase_change(self, phaseinfo: PhaseInfo) -> None:

        """
        Executes all corresponding callback functions if a phase change ocurred.
        """

        cphase = phaseinfo.phase

        if self._prev_phase != cphase:

            transitions = [(self._prev_phase, cphase), (Phases.ANY_PHASE, cphase), (self._prev_phase, Phases.ANY_PHASE)]

            for transition in transitions:
                if transition in self._transition_callbacks:
                    for func in self._transition_callbacks[transition]:
                        func(self._prev_phase, cphase, phaseinfo)


        self._prev_phase = cphase

    def add_transition_callback(self, transition: phase_transition_t, func: Callable[[Phases, Phases, PhaseInfo], None]) -> bool:
        """
        Adds the given callback function to the callbacks for the given transition.
        Return False if the function is already registered for the same transition,
        True else.
        """

        if transition not in self._transition_callbacks:
            self._transition_callbacks[transition] = []
        else:
            if func in self._transition_callbacks[transition]:
                return False

        self._transition_callbacks[transition].append(func)

        return True

    def remove_transition_callback(self, transition: phase_transition_t, func: Callable[[Phases, Phases, PhaseInfo], None]) -> bool:
        """
        Tries to remove the given function from the phase change functions.
        If the function is not registered for the transition, this fails to remove it and returns False.
        Otherwise True is returned.
        """

        if transition in self._transition_callbacks:
            if func in self._transition_callbacks[transition]:
                self._transition_callbacks[transition].remove(func)
                return True

        return False

    def clear_transition_callback(self, transition: phase_transition_t) -> list[ Callable[ [Phases, Phases, PhaseInfo], None ] ]:
        """
        Removes all callbacks registered for transition, then returns all functions removed
        in a list.
        """
        if transitions not in self._transition_callbacks:
            return []
        else:

            funcs = self._transition_callbacks[transition]
            self._transition_callbacks[transition] = []

            return funcs

    def clear_all_transition_callback(self) -> dict[ phase_transition_t, list[Callable[ [Phases, Phases, PhaseInfo] , None]] ]:
        """
        Clears all callbacks, then returns the transition dictionary before being cleared.
        """
        back = self._transition_callbacks
        self._transition_callbacks = {}

        return back
