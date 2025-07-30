"""
RGBNum enumerates colors represented by instances of the RGB dataclass.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from worktoy.keenum import KeeNum, auto
from . import RGB


class RGBNum(KeeNum):
  """RGBNum enumerates colors represented by instances of the RGB
  dataclass. """

  BLACK = auto(RGB(0, 0, 0))
  WHITE = auto(RGB(255, 255, 255))
  SILVER = auto(RGB(192, 192, 192))
  GRAY = auto(RGB(128, 128, 128))
  LEAD = auto(RGB(96, 96, 96))
  ASH = auto(RGB(64, 64, 64))

  RED = auto(RGB(255, 0, 0))
  GREEN = auto(RGB(0, 255, 0))
  BLUE = auto(RGB(0, 0, 255))

  YELLOW = auto(RGB(255, 255, 0))
  CYAN = auto(RGB(0, 255, 255))
  MAGENTA = auto(RGB(255, 0, 255))

  ORANGE = auto(RGB(255, 136, 0))
  MINT = auto(RGB(0, 255, 136))
  PURPLE = auto(RGB(136, 0, 255))
  PINK = auto(RGB(255, 0, 136))
  AZURE = auto(RGB(0, 136, 255))
  LIME = auto(RGB(136, 255, 0))
