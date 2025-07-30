"""
RGB provides a simple dataclass representation of RGB colorspace.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from worktoy.ezdata import EZData

if TYPE_CHECKING:  # pragma: no cover
  pass


class RGB(EZData):
  """
  RGB represents a color as a tuple of RGB values.
  """

  red = 255
  green = 255
  blue = 255

  def __str__(self) -> str:
    """Returns the hex representation of the RGB color (ie: #RRGGBB). """
    return f"#{self.red:02X}{self.green:02X}{self.blue:02X}"

  def __repr__(self) -> str:
    """Returns code that would instantiate this RGB object."""
    infoSpec = """%s(%r, %r, %r)"""
    clsName = type(self).__name__
    return infoSpec % (clsName, self.red, self.green, self.blue)
