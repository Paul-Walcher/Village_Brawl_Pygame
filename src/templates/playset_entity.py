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
from templates.renderable_cardinfo import Renderable_CardInfo


class PlaysetEntity(Frame):

    """
    Describes a card/entity that needs to be rendered to the screen,
    and does actions every frame, needing to be updated using tick().

    Playset entities are in the same focus group as the main frames,
    so frames take the inputs before the main frame does.

    This should not happen by the entity calling focus() itself,
    but by queueing itself in in a focus-queue by the parent frame.
    """

    @staticmethod
    def info() -> Renderable_CardInfo:
        """
        Returns a renderable cardinfo describing the object.
        """
        pass

    def __init__(   self,
                    modules: Modules,
                    entity_type: TypeEnums,
                    frame_enum: FrameEnums = FrameEnums.PLAYSET_ENTITY,
                    data: Any = None,
                    frame_dim: pygame.Rect = constants.FULLSCREEN,
                    parent_frame: Frame = None,
                    focus_group: str = "",
                    has_focus: bool = False #no focus by default
                    ):

        super().__init__(frame_enum=frame_enum, data=data, frame_dim=frame_dim, parent_frame=parent_frame, focus_group=focus_group, has_focus=has_focus)

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
        self.entity_type: TypeEnums = entity_type
        """
        The type of this entity.
        """

    def tick(
                self,
                phaseinfo: PhaseInfo
                ) -> Frame:

        """
        Tick function for the entity.
        Rceceives Information about the game state as PhaseInfo instances.
        """


        return self

    def rerender(self) -> None:
        """
        Rerendering upon reentry.
        """
        pass

    def render(self, screen: pygame.Surface) -> None:
        """
        Render function. The default is drawing nothing.
        """
        pass
