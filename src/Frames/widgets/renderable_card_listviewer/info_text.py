"""
The info text contains
functionality for showing the information text inside the
RenderableCardListviewer
"""

from __future__ import annotations
from typing import Type, Any, Callable, override, TYPE_CHECKING

from constants import Colors

if TYPE_CHECKING:
    from constants import (
                            color_rgb_t,
                            color_rgba_t,
                            color_t
                            )


class InfoTextPalette:
    """
    The palette for the info text.
    """

    def __init__(
                    self,

                    # info text specifications
                    info_text_hlen_p: float = 0.3,  # horizontal length percentage
                    info_text_vlen_p: float = 0.15,  # vertical length percentage
                    info_text_surface_alpha: int = 180,
                    info_text_color: color_rgb_t = None,
                    info_text_warning_color: color_rgb_t = None,
                    info_text_error_color: color_rgb_t = None,
                    ):

        self.info_text_hlen_p: float = info_text_hlen_p
        """
        Width of the info text as a percentage relative to self.width.
        """
        self.info_text_vlen_p: float = info_text_vlen_p
        """
        Height of the info text as a percentage relative to self.height.
        """
        self.info_text_color: color_rgb_t = info_text_color
        """
        The standard info text color for the text.
        """
        self.info_text_warning_color: color_rgb_t = info_text_warning_color
        """
        The color for the info text for when a warning is displayed.
        """
        self.info_text_error_color: color_rgb_t = info_text_error_color
        """
        The color for the info text for when an error is displayed.
        """
