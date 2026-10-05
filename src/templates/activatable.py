from abc import ABC, abstractmethod
from enum import Enum, auto
from Frames.frame import Frame
from Frames.frame_enums import FrameEnums


class ActivationResultEnums(Enum):

    SUCCESS = auto()
    PARTIAL_SUCCESS = auto()
    FAILURE = auto()


class ActivationResult:

    def __init__(self, result, data=None):

        self.result = result
        self.data = (data if data is not None else {})

class Activatable(ABC):

    def __init__(self, activation_phases=None):

        self.activation_phases = (activation_phases if activation_phases is not None else [])

    @abstractmethod
    def activate(self, phaseinfo):

        """
        Returns the activation result.
        """
        pass
