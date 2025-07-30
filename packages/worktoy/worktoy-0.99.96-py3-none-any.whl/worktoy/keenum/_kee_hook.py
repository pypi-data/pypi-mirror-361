"""
KeeHook provides the namespace hook for the KeeSpace namespace class.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..mcls.space_hooks import AbstractSpaceHook
from . import _AutoMember
from ..utilities import maybe
from ..waitaminute.keenum import KeeNumTypeException, DuplicateKeeNum

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Optional


class KeeSpaceHook(AbstractSpaceHook):
  """
  KeeHook provides the namespace hook for the KeeSpace namespace class.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __future_value_type__ = None

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _addMember(self, name: str, value: Any = None, **kwargs) -> None:
    """
    Add a member to the KeeSpace namespace.
    """
    if isinstance(value, _AutoMember):
      value = value.getValue()
    value = maybe(value, name)
    existing = self.space.get('__future_entries__', {})
    if existing:
      if name in existing:
        raise DuplicateKeeNum(name, value)
      for _, val in existing.items():
        valType = type(val)
        if not isinstance(value, valType):
          raise KeeNumTypeException(name, value, valType)
    existing[name] = value
    self.space['__future_entries__'] = existing

  def _getValueType(self) -> Optional[type]:
    """
    Get the value type for the KeeSpace namespace.
    """
    return getattr(self.space, '__future_value_type__', None)

  def setItemPhase(self, key: str, value: Any, oldValue: Any, ) -> bool:
    """
    The setItemHook method is called when an item is set in the
    namespace.
    """
    if hasattr(value, '__is_root__'):  # ignores, stubs only
      return True
    if key.startswith('__') and key.endswith('__'):
      # Skip special keys
      return False
    if callable(value):
      return False
    self._addMember(key.upper(), value)
    return False

  def preCompilePhase(self, compiledSpace: dict) -> dict:
    """Hook for preCompile. This is called before the __init__ method of
    the namespace object is called. The default implementation does nothing
    and returns the contents unchanged. """
    compiledSpace['__future_entries__'] = dict()
    compiledSpace['__future_value_type__'] = self._getValueType()
    return compiledSpace
