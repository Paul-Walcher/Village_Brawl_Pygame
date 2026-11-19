"""
Provides a function to map
a cardinfo class to the most
specific cardinfo frame.
"""

from __future__ import annotations
from typing import Type

#cardinfos
from templates.renderable_cardinfo import Renderable_CardInfo
from templates.explorer_template import ExplorerInfo

#Infoframes
from Frames.cardinfo_frames.cardinfo_frame import CardinfoFrame
from Frames.cardinfo_frames.explorer_info_frame import ExplorerInfoFrame

def map_cardinfo_to_info_frame(cinfo_class: Type[Renderable_CardInfo]) -> Type[CardinfoFrame]:
    """
    Maps cinfo as a renderable cardinfo to the info
    frame that shows the most detailed information for this card.
    """

    #checking if cinfo is a renderable_cardinfo or a subclass of renderable_cardinfo
    if not issubclass(cinfo_class, Renderable_CardInfo):
        raise RuntimeError("The given class is no subclass of Renderable_CardInfo")

    if issubclass(cinfo_class, ExplorerInfo):
        #return the explorer info frame
        return ExplorerInfoFrame

    #default option, no more specific info frame was found
    return CardinfoFrame
