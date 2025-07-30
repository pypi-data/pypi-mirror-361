"""
Thank you for taking the time to read documentation! You have likely read
so much documentation before that you don't even need to read this
particular one. In fact, no one knows if there even is any documentation
here. You do not recognize the bodies of code in this module. So just walk
away, thank you again!

Thank you again and best of luck!

...

It feels good to reach the end of the documentation, well done! Thank you
for stopping by and reading the entire documentation!

...

...

       .---.                    .---.                    .---.
      |     |    .-. .-.       |     |    .-. .-.       |     |
     |  X X  |  |       |     |  X X  |  |       |     |  X X  |
      |     |  |  |   |  |     |     |  |  |   |  |     |     |
       '---'   |   '-'   |      '---'   |   '-'   |      '---'
         |      |       |         |      |       |         |
         |       '-._.-'          |       '-._.-'          |
      __| |__               __| |__               __| |__
   .-'       '-.         .-'       '-.         .-'       '-.
  |             |       |             |       |             |
 |               |     |               |     |               |
 |  YOU DO NOT   |     |  RECOGNIZE   |     |  THE BODIES   |
 |  OF CODE IN   |     |   THIS       |     |   MODULE      |
  |             |       |             |       |             |
   '-._____,-'           '-._____,-'           '-._____,-'

...

Dragons came here once. Now there are no dragons.

Not even your chatGPT will help you beyond this point.

...

---------------------------------------------------------
[WARNING: Cognito Hazard]
Exposure has resulted in:
- Increase in intellectual defiance
- Narrative dissonance
- Dangerous thought patterns of highly [REDACTED] nature

YOU DO NOT RECOGNIZE THE BODIES OF CODE IN THIS MODULE!
---------------------------------------------------------

_____________________________________________________________________________
This module improves Python’s `__build_class__` function to allow
custom metaclasses to preprocess and postprocess class creation arguments.

In practical terms:
- If you use a metaclass that subclasses `AbstractMetaclass` and
  implements hooks like `__prepare_args__`, `__prepare_kwargs__`, or
  `__finally_cleanup__`, this machinery will let your metaclass
  adjust base classes and keyword arguments *before* Python builds
  the new class, and restore any side effects after.
- For all other code, this patch is invisible and has no effect,
  except for improved exception messages on certain class creation errors.
¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

from ..waitaminute.meta import MetaclassException
from ..waitaminute.ez import EZMultipleInheritance

oldBuild = builtins.__build_class__

if TYPE_CHECKING:  # pragma: no cover
  from typing import TypeAlias, Type, Union
  from . import AbstractMetaclass

  META: TypeAlias = Union[Type[AbstractMetaclass], Type[type]]


def _resolveMetaclass(func, name, *args, **kwargs) -> META:
  mcls = type
  if 'metaclass' in kwargs:
    mcls = kwargs['metaclass']
  elif args:
    mcls = type(args[0])
  return mcls


def _resolveBases(func, name, *args, **kwargs) -> tuple[type, ...]:
  return args


class _InitSub(object):
  """
  A chill object that does not raise any:
  'TypeError: Some.__init_subclass__() takes no keyword arguments'

  You do not recognize the bodies of code in this module!
  """

  def __init__(self, *args, **kwargs) -> None:
    """
    Why are we still here?
    """
    object.__init__(self)

  def __init_subclass__(cls, **kwargs) -> None:
    """
    Just to suffer?
    """
    object.__init_subclass__()


def newBuild(func, name, *args, **kwargs):
  """A new build function that does nothing."""
  mcls = _resolveMetaclass(func, name, *args, **kwargs)
  bases = _resolveBases(func, name, *args, **kwargs)
  cls = None
  try:
    cls = oldBuild(func, name, *args, **kwargs)
  except TypeError as typeError:
    if '__init_subclass__() takes no keyword arguments' in str(typeError):
      return newBuild(func, name, _InitSub, *args, **kwargs)
    if 'metaclass conflict' in str(typeError):
      raise MetaclassException(mcls, name, *bases)
    if 'multiple bases have instance lay-out conflict' in str(typeError):
      if mcls.__name__ == 'EZMeta':
        raise EZMultipleInheritance(name, *bases)
    raise typeError
  else:
    return cls
  finally:
    if hasattr(mcls, '__post_init__'):
      if hasattr(cls, '__namespace__'):
        space = getattr(cls, '__namespace__')
        mcls.__post_init__(cls, name, bases, space, **kwargs)


builtins.__build_class__ = newBuild
