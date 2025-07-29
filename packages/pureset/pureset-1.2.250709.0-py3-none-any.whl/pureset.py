"""
pureset.py
==========

A robust, immutable, homogeneous, and ordered collection library for Python, blending the best features of sets, tuples, sequences, and mappings.

Overview
--------
This module exposes 2 new immutable collection types: PureSet and PureMap.
PureSet provides intuitively immutable containers for unique elements while preserving insertion order and enforcing type homogeneity.
PureMap works similarly, but enforces type homogeneity for both keys and values.

Features
--------
- **Immutability:** Once instantiated, elements (and, in PureMap, keys/values) cannot be altered, added, or removed.
- **Homogeneity:** All elements (and keys/values in PureMap) are type- or structure-homogeneous.
- **Uniqueness:** Duplicate elements/keys are disallowed, and order is preserved.
- **Rich API:** Supports serialization, comparison, concatenation, set-like and mapping operations, mapping/filtering, indexing, slicing, and introspection.
- **Extensible:** Specialized behaviors for sets and mappings; fits symbolic, mathematical, and configuration use-cases.

Typical Use Cases
-----------------
- Symbolic, configuration, or dataset domains requiring immutable, deterministic collections.
- Hashable, reproducible "frozen" sets and maps for functional programming, caching, and high-integrity computing.

Examples
--------
>>> PureSet(1, 2, 3)
PureSet(1, 2, 3)
>>> PureSet([1, 2], [3, 4])
PureSet([1, 2], [3, 4])
>>> PureSet()
PureSet()
>>> PureSet(1, 2, 2, 3)
PureSet(1, 2, 3)
>>> PureSet(1, 'a')
Traceback (most recent call last):
  ...
TypeError: Incompatible element type or shape at position 2:
Exp: <class 'int'>;
Got: <class 'str'>

>>> PureMap(a=1, b=2)
PureMap('a': 1, 'b': 2)
>>> PureMap({'x': 42, 'y': 99})
PureMap('x': 42, 'y': 99)
>>> PureMap([('foo', 1), ('bar', 2)])
PureMap('foo': 1, 'bar': 2)
>>> PureMap()
PureMap()
>>> PureMap({'a': 1, 'a': 2})
PureMap('a': 2)
>>> PureMap(John="Manager", Mary="Secretary", Joe=id("Engineer"))
Traceback (most recent call last):
  ...
TypeError: Value type/shape mismatch:
Exp: <class 'str'>
Got: <class 'int'>

Author
------
Gabriel Maia (@gabrielmsilva00)
Electric Engineering Undergraduate at the Universidade Estadual do Rio de Janeiro (UERJ), Brasil

License
-------
Apache License 2.0

Links
-----
Repository: https://github.com/gabrielmsilva00/pureset  
Contact:    gabrielmaia.silva00@gmail.com
"""

from __future__ import annotations
from copy import deepcopy
from functools import total_ordering
from collections import UserList, UserDict, UserString, deque, ChainMap, Counter, OrderedDict, defaultdict
from collections.abc import Sequence, Mapping, Set
from numbers import Number
from enum import Enum
from array import array
from typing import Any, TypeVar, Union, Optional, Callable, Hashable, Iterator, overload
from types import MappingProxyType

__title__   = "pureset"
__desc__    = "An immutable, homogeneous, and ordered collection type for Python."
__version__ = "1.2.250709.0"
__author__  = "gabrielmsilva00"
__contact__ = "gabrielmaia.silva00@gmail.com"
__repo__    = "github.com/gabrielmsilva00/pureset"
__license__ = "Apache License 2.0"
__all__     = ["PureSet", "PureMap"]

T = TypeVar("T")

@total_ordering
class PureSet(Sequence[T]):
  """
  Immutable, homogeneous, and ordered collection of unique elements.

  PureSet combines deterministic storage, structure-aware uniqueness, and strong type checking,
  making it ideal for reproducible, functional applications.
  """
  __slots__ = (
      "_items",
      "_signature",
      "_restored_cache",
      "_items_set",
  )

  def __init__(self, *args: T) -> None:
    if not args:
      self._items = ()
      self._signature = None
      self._restored_cache = None
      self._items_set = None
      return

    PRIMITIVE = (int, float, bool, str, bytes, frozenset, type)
    T0 = type(args[0])

    if all(isinstance(x, T0) for x in args) and T0 in PRIMITIVE:
      self._signature = T0
      items = tuple(dict.fromkeys(args))
      self._items = items
      self._restored_cache = None
      self._items_set = set(items)
      return

    self._signature = PureSet.get_signature(args[0])
    for i, item in enumerate(args):
      sig = PureSet.get_signature(item)
      if sig != self._signature:
        raise TypeError(
            f"Incompatible element type or shape at position {i + 1}:\nExp: {self._signature};\nGot: {sig}"
        )

    frozen_args = tuple(PureSet.freeze(item) for item in args)

    try: hashable = all(hash(x) is not None for x in frozen_args)
    except Exception: hashable = False

    if hashable:
      items = tuple(dict.fromkeys(frozen_args))
      self._items = items
      self._restored_cache = None
      self._items_set = set(items)
    else:
      seen = []
      unique_items = []
      for item in frozen_args:
        if item not in seen:
          seen.append(item)
          unique_items.append(item)
      self._items = tuple(unique_items)
      self._restored_cache = None
      self._items_set = None

  def __setattr__(self, name: str, value: Any) -> None:
    if name in self.__slots__: object.__setattr__(self, name, value)
    else: raise AttributeError(f"{self.__class__.__name__} is immutable")

  @property
  def items(self) -> tuple[T, ...]: return self.restored

  @property
  def signature(self) -> Any: return self._signature

  @property
  def restored(self):
    if self._restored_cache is not None: return self._restored_cache
    self._restored_cache = tuple(self.restore(o) for o in self._items)
    return self._restored_cache

  def __contains__(self, item: object) -> bool:
    if self._items_set is not None:
      try: return item in self._items_set
      except Exception: pass
    frozen = self.freeze(item)
    return frozen in self._items

  def __reduce__(self) -> tuple: return (self.__class__, self.restored)

  def __copy__(self) -> PureSet[T]: return self.__class__(*self.restored)

  def __deepcopy__(self, memo: dict[int, Any]) -> PureSet[T]:
    return self.__class__(*(deepcopy(item, memo) for item in self.restored))

  def __len__(self) -> int: return len(self._items)

  def __iter__(self) -> Iterator[T]: return iter(self.restored)

  def __hash__(self) -> int: return hash((type(self), self._items))

  def __repr__(self) -> str:
    if not self._items: return f"{self.__class__.__name__}()"
    return f"{self.__class__.__name__}({', '.join(map(repr, self.restored))})"

  def __str__(self) -> str:
    if not self._items: return f"{self.__class__.__name__}()"
    items_str = ", ".join(repr(item) for item in self.restored[:10])
    if len(self._items) > 10: items_str += f", ... ({len(self._items) - 10} more items)"
    return f"{self.__class__.__name__}({items_str})"

  def __getitem__(self, idx: Union[int, slice, T]) -> Union[T, PureSet[T]]:
    if isinstance(idx, int): return self.restore(self._items[idx])
    elif isinstance(idx, slice): return self.__class__(*(self.restore(x) for x in self._items[idx]))
    else:
      frozen = self.freeze(idx)
      if isinstance(self._items, Hashable):
        for x in self._items:
          if x == frozen: return self.restore(x)
      else:
        for x in self._items:
          if x == frozen: return self.restore(x)
    raise KeyError(f"Value {idx!r} not found in {self.__class__.__name__}")

  def __eq__(self, other: object) -> bool: return isinstance(other, PureSet) and self._items == other._items

  def __lt__(self, other: PureSet[T]) -> bool:
    if not isinstance(other, PureSet): raise TypeError("Cannot compare PureSet with non-PureSet")
    return self.restored < other.restored

  def __le__(self, other: PureSet[T]) -> bool:
    if not isinstance(other, PureSet): raise TypeError("Cannot compare PureSet with non-PureSet")
    return self.restored <= other.restored

  def __gt__(self, other: PureSet[T]) -> bool:
    if not isinstance(other, PureSet): raise TypeError("Cannot compare PureSet with non-PureSet")
    return self.restored > other.restored

  def __ge__(self, other: PureSet[T]) -> bool:
    if not isinstance(other, PureSet): raise TypeError("Cannot compare PureSet with non-PureSet")
    return self.restored >= other.restored

  def __add__(self, other: PureSet[T]) -> PureSet[T]:
    if not isinstance(other, PureSet): raise TypeError("Cannot concatenate PureSet with non-PureSet")
    if self.signature and other.signature and self.signature != other.signature:
      raise TypeError(
        f"Cannot concatenate PureSets with different element types: "
        f"Exp: {self.signature}\nGot: {other.signature}"
      )
    if not self._items: return other
    if not other._items: return self
    seen = set(self._items)
    merged = list(self.restored)
    for item in other.restored:
      f = self.freeze(item)
      if f not in seen:
        seen.add(f)
        merged.append(item)
    return self.__class__(*merged)

  def __mul__(self, n: int) -> PureSet[T]:
    if not isinstance(n, int): raise TypeError("Repetitions must be an integer")
    return self if n > 0 else self.__class__()

  def pos(self, index: int) -> T: return self.restored[index]

  def index(self, value: T, start: int = 0, stop: Optional[int] = None) -> int:
    r = self.restored
    return r.index(value, start, stop) if stop is not None else r.index(value, start)

  def count(self, value: T) -> int: return 1 if value in self else 0

  def join(self, sep: str) -> str: return sep.join(map(str, self.restored))

  def reverse(self) -> PureSet[T]: return self.__class__(*reversed(self.restored))

  def to_list(self) -> list[T]: return list(self.restored)

  def to_tuple(self) -> tuple[T, ...]: return self.restored

  def to_frozenset(self) -> frozenset: return frozenset(self.restored)

  def compatible(self, other: PureSet[T]) -> PureSet[T]:
    if not isinstance(other, PureSet): raise TypeError(f"Expected PureSet, got '{type(other)}'")
    if self._items and other._items and self.signature != other.signature:
      raise TypeError(
        f"Incompatible element types:\nExp: {self.signature}\nGot: {other.signature}"
      )
    return other

  def __or__(self, other: PureSet[T]) -> PureSet[T]:
    other = self.compatible(other)
    if not other._items: return self
    if not self._items: return other
    seen = set(self._items)
    result = list(self.restored)
    for item in other.restored:
      f = self.freeze(item)
      if f not in seen:
        seen.add(f)
        result.append(item)
    return self.__class__(*result)

  def __and__(self, other: PureSet[T]) -> PureSet[T]:
    other = self.compatible(other)
    if isinstance(self._items, Hashable) and isinstance(other._items, Hashable):
      set_other = set(other._items)
      return self.__class__(*(self.restore(x) for x in self._items if x in set_other))
    else: return self.__class__(*(x for x in self.restored if x in other))

  def __sub__(self, other: PureSet[T]) -> PureSet[T]:
    other = self.compatible(other)
    if isinstance(self._items, Hashable) and isinstance(other._items, Hashable):
      set_other = set(other._items)
      return self.__class__(*(self.restore(x) for x in self._items if x not in set_other))
    else: return self.__class__(*(x for x in self.restored if x not in other))

  def __xor__(self, other: PureSet[T]) -> PureSet[T]:
    other = self.compatible(other)
    result = [x for x in self.restored if x not in other]
    result.extend(x for x in other.restored if x not in self)
    return self.__class__(*result)

  def filter(self, predicate: Callable[[T], bool]) -> PureSet[T]:
    return self.__class__(*filter(predicate, self.restored))

  def map(self, function: Callable[[T], Any]) -> PureSet[Any]:
    return self.__class__(*map(function, self.restored))

  def first(self, default: Optional[T] = None) -> Optional[T]:
    return self.restored[0] if self.restored else default

  def last(self, default: Optional[T] = None) -> Optional[T]:
    return self.restored[-1] if self.restored else default

  def sorted(self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> PureSet[T]:
    return self.__class__(*sorted(self.restored, key=key, reverse=reverse))

  def unique(self) -> PureSet[T]: return self

  def get(self, item: T, default: Optional[T] = None) -> T: return item if item in self.restored else default

  @staticmethod
  def get_signature(obj: object) -> Union[type, tuple]:
    """Get the signature of a given object.

    The signature is a tuple of the object type and the signatures of its
    properties or elements if it is a container.

    Parameters
    ----------
    obj : object
      Object to get the signature of

    Returns
    -------
    Union[type, tuple]
      The signature of the object
    """
    if obj is None: return type(None)

    try:
      import numpy as np
      import pandas as pd
      if isinstance(obj, np.ndarray): return (np.ndarray, obj.shape, str(obj.dtype))
      if isinstance(obj, np.generic): return type(obj)
      if isinstance(obj, pd.Series): return (pd.Series, str(obj.dtype), len(obj))
      if isinstance(obj, pd.Index): return (pd.Index, str(obj.dtype), len(obj))
      if isinstance(obj, pd.DataFrame):
        return (pd.DataFrame, tuple(obj.columns), tuple(str(dt) for dt in obj.dtypes), obj.shape)
    except ImportError:
      pass

    obj_type = type(obj)
    if obj_type in (int, float, complex, bool, str, bytes): return obj_type

    if isinstance(obj, dict): return (dict, {k: PureSet.get_signature(v) for k, v in sorted(obj.items())})

    if hasattr(obj, "__dict__") or hasattr(obj, "__slots__"):
      props = {
        name: PureSet.get_signature(getattr(obj, name))
        for name in dir(obj)
        if not (
          name.startswith("_")
          or name.endswith("_")
          or callable(getattr(obj, name))
        )
      }

      if props: return (obj_type, props)

    if hasattr(obj, "__iter__") and obj_type not in (str, bytes, type):
      types       = []
      last_type   = None
      last_count  = 0

      for item in obj:
        current_type = PureSet.get_signature(item)
        if current_type == last_type: last_count += 1
        else:
          if last_type is not None:
            types.append(
              (last_type, last_count) if last_count > 1 else last_type
            )

          last_type   = current_type
          last_count  = 1

      if last_type is not None: types.append((last_type, last_count) if last_count > 1 else last_type)

      if len(types) == 1: return (obj_type, types[0])
      return (obj_type, *types)

    if (
      hasattr(obj, "__len__")
      and hasattr(obj, "__getitem__")
      and obj_type not in (str, bytes, type)
    ):
      element_types   = [PureSet.get_signature(x) for x in obj]
      current_type    = element_types[0]
      count           = 1
      types           = []

      for elem_type in element_types[1:]:
        if elem_type == current_type: count += 1
        else:
          types.append((current_type, count) if count > 1 else current_type)
          current_type = elem_type
          count = 1

      types.append((current_type, count) if count > 1 else current_type)
      return (obj_type, types[0] if len(types) == 1 else tuple(types))

    return obj_type

  @staticmethod
  def freeze(obj: object, seen: Optional[Set] = None) -> Hashable:
    """Freeze the given object into a hashable object.

    Parameters
    ----------
    obj : object
      Object to freeze
    seen : Optional[Set]
      Set of already seen objects

    Returns
    -------
    Hashable
      Hashable representation of the object
    """
    if seen is None: seen = set()
    obj_id = id(obj)
    if obj_id in seen: raise ValueError("Cyclical reference detected")
    seen.add(obj_id)
    try:
      if obj is None or isinstance(obj, (Number, bool, str, bytes, frozenset, type)): return obj
      try: import numpy as np
      except ImportError: np = None
      if np is not None:
        if isinstance(obj, np.ndarray): return (np.ndarray, (obj.shape, str(obj.dtype), obj.tobytes()))
        if isinstance(obj, np.generic): return (type(obj), obj.item())
      try: import pandas as pd
      except ImportError: pd = None
      if pd is not None:
        if isinstance(obj, pd.Series): return (pd.Series, (obj.dtype.name, tuple(obj.index), tuple(obj.values)))
        if isinstance(obj, pd.Index): return (pd.Index, (obj.dtype.name, tuple(obj)))
        if isinstance(obj, pd.DataFrame):
          return (
            pd.DataFrame,
            (tuple(obj.columns), tuple(obj.dtypes.astype(str)), tuple(obj.index), tuple(map(tuple, obj.values)))
          )
      if isinstance(obj, PureSet): return (PureSet, tuple(PureSet.freeze(x, seen) for x in obj.restored))
      if isinstance(obj, range): return (range, (obj.start, obj.stop, obj.step))
      if isinstance(obj, memoryview): return (memoryview, obj.tobytes())
      if isinstance(obj, array): return (array, (obj.typecode, obj.tobytes()))
      if isinstance(obj, UserString): return (UserString, PureSet.freeze(obj.data, seen))
      if isinstance(obj, UserList): return (UserList, tuple(PureSet.freeze(x, seen) for x in obj))
      if isinstance(obj, UserDict):
        return (UserDict, tuple(sorted((PureSet.freeze(k, seen), PureSet.freeze(v, seen)) for k, v in obj.items())))
      if isinstance(obj, deque): return (deque, tuple(PureSet.freeze(x, seen) for x in obj))
      if isinstance(obj, ChainMap): return (ChainMap, tuple(PureSet.freeze(m, seen) for m in obj.maps))
      if isinstance(obj, Counter):
        return (Counter, tuple(sorted((PureSet.freeze(k, seen), PureSet.freeze(v, seen)) for k, v in obj.items())))
      if isinstance(obj, OrderedDict):
        return (OrderedDict, tuple((PureSet.freeze(k, seen), PureSet.freeze(v, seen)) for k, v in obj.items()))
      if isinstance(obj, defaultdict):
        factory = obj.default_factory.__name__ if obj.default_factory else None
        return (
          defaultdict,
          (factory, tuple(sorted((PureSet.freeze(k, seen), PureSet.freeze(v, seen)) for k, v in obj.items())))
        )
      if isinstance(obj, Enum): return (type(obj), obj.value)
      if isinstance(obj, tuple) and hasattr(obj, "_fields"):
        return (type(obj), tuple(PureSet.freeze(getattr(obj, f), seen) for f in obj._fields))
      if isinstance(obj, tuple): return (tuple, tuple(PureSet.freeze(x, seen) for x in obj))
      if isinstance(obj, list): return (list, tuple(PureSet.freeze(x, seen) for x in obj))
      if isinstance(obj, set): return (set, tuple(sorted(PureSet.freeze(x, seen) for x in obj)))
      if isinstance(obj, dict):
        return (dict, tuple(sorted((PureSet.freeze(k, seen), PureSet.freeze(v, seen)) for k, v in obj.items())))
      if isinstance(obj, Mapping):
        return (type(obj), tuple(sorted((PureSet.freeze(k, seen), PureSet.freeze(v, seen)) for k, v in obj.items())))
      if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, tuple, list, PureSet, UserString, deque)):
        return (type(obj), tuple(PureSet.freeze(x, seen) for x in obj))
      if isinstance(obj, Set) and not isinstance(obj, (set, frozenset, PureSet)):
        return (type(obj), tuple(sorted(PureSet.freeze(x, seen) for x in obj)))
      if hasattr(obj, '__dataclass_fields__'):
        field_names = sorted(f.name for f in obj.__dataclass_fields__.values())
        return (type(obj), tuple((f, PureSet.freeze(getattr(obj, f), seen)) for f in field_names))
      if hasattr(obj, '__slots__'):
        slot_fields = [
          (s, PureSet.freeze(getattr(obj, s), seen))
          for s in sorted(getattr(obj, '__slots__', ()))
          if hasattr(obj, s)
        ]
        if slot_fields: return (type(obj), tuple(slot_fields))
      if hasattr(obj, '__dict__'):
        fields = [
          (k, PureSet.freeze(v, seen))
          for k, v in sorted(vars(obj).items())
          if not (k.startswith('__') and k.endswith('__')) and not callable(getattr(obj, k))
        ]
        if fields: return (type(obj), tuple(fields))
      raise TypeError(f"Cannot safely freeze object of type {type(obj)} for PureSet.")
    finally: seen.remove(obj_id)

  @staticmethod
  def restore(obj: tuple[T, object]) -> T:
    """Restore the given object from a hashable representation.

    Parameters
    ----------
    obj : tuple[T, object]
      Object to restore

    Returns
    -------
    T
      Restored object
    """
    try: import pandas as pd
    except ImportError: pd = None
    try: import numpy as np
    except ImportError: np = None
    if obj is None or isinstance(obj, (Number, bool, str, bytes, frozenset, type)): return obj
    if isinstance(obj, tuple) and len(obj) == 2:
      kind, content = obj
      if np is not None:
        if kind is np.ndarray:
          shape, dtype, bts = content
          return np.frombuffer(bts, dtype=dtype).reshape(shape)
        if np and isinstance(kind, type) and issubclass(kind, np.generic): return kind(content)
      if pd is not None:
        if kind is pd.Series:
          dtype_name, idx, vals = content
          return pd.Series(list(vals), index=list(idx), dtype=dtype_name)
        if kind is pd.DataFrame:
          cols, dtypes, idx, rows = content
          import numpy as np
          arr = np.array(rows)
          df = pd.DataFrame(arr, columns=cols, index=idx)
          for c, dtype in zip(cols, dtypes): df[c] = df[c].astype(dtype)
          return df
        if kind is pd.Index:
          dtype_name, vals = content
          return pd.Index(list(vals), dtype=dtype_name)
      if kind is PureSet: return PureSet(*(PureSet.restore(x) for x in content))
      if kind is UserString: return UserString(PureSet.restore(content))
      if kind is UserList: return UserList([PureSet.restore(x) for x in content])
      if kind is UserDict: return UserDict({PureSet.restore(k): PureSet.restore(v) for k, v in content})
      if kind is deque: return deque([PureSet.restore(x) for x in content])
      if kind is ChainMap: return ChainMap(*[PureSet.restore(m) for m in content])
      if kind is Counter: return Counter({PureSet.restore(k): PureSet.restore(v) for k, v in content})
      if kind is OrderedDict: return OrderedDict((PureSet.restore(k), PureSet.restore(v)) for k, v in content)
      if kind is defaultdict:
        _, items = content
        d = defaultdict(None)
        d.update({PureSet.restore(k): PureSet.restore(v) for k, v in items})
        return d
      if kind is range:
        s, e, st = content
        return range(s, e, st)
      if kind is memoryview: return memoryview(PureSet.restore(content))
      if kind is array:
        tc, bts = content
        return array(tc, bts)
      if isinstance(kind, type) and issubclass(kind, Enum): return kind(content)
      if isinstance(kind, type) and hasattr(kind, "_fields"): return kind(*(PureSet.restore(x) for x in content))
      if kind is tuple: return tuple(PureSet.restore(x) for x in content)
      if kind is list: return [PureSet.restore(x) for x in content]
      if kind is set: return set(PureSet.restore(x) for x in content)
      if kind is dict: return {PureSet.restore(k): PureSet.restore(v) for k, v in content}
      if isinstance(kind, type) and issubclass(kind, Mapping):
        return kind((PureSet.restore(k), PureSet.restore(v)) for k, v in content)
      if isinstance(kind, type) and issubclass(kind, Sequence) and not hasattr(kind, "_fields"):
        return kind(PureSet.restore(x) for x in content)
      if isinstance(kind, type) and issubclass(kind, Set): return kind(PureSet.restore(x) for x in content)
      if hasattr(kind, '__dataclass_fields__'):
        field_data = {k: PureSet.restore(v) for k, v in content}
        return kind(**field_data)
      if hasattr(kind, "__new__"):
        inst = kind.__new__(kind)
        for k, v in content:
          if not (k.startswith('__') and k.endswith('__')): setattr(inst, k, PureSet.restore(v))
        return inst
    if isinstance(obj, tuple): return tuple(PureSet.restore(x) for x in obj)
    return obj


class PureMap(PureSet, Mapping):
  __slots__ = (
    "_items",
    "_signature",
    "_restored_cache",
    "_items_set",
    '_keys',
    '_values',
    '_items_dict',
    '_restored_map',
    '_signature_k',
    '_signature_v',
  )

  def __init__(self, *args, **kwargs):
    if args and kwargs: raise TypeError('PureMap cannot mix mapping/sequence and keyword arguments')
    if args:
      if len(args) > 1: raise TypeError('PureMap only accepts one positional mapping or iterable')
      try: items = dict(args[0])
      except BaseException as e: raise TypeError(f"Unable to create PureMap from {args[0]!r}: {e!r}")
    else: items = dict(kwargs)

    if not items:
      self._keys = PureSet()
      self._values = PureSet()
      self._items_dict = {}
      self._restored_map = {}
      self._signature_k = None
      self._signature_v = None
      super().__init__()
      return

    key_sample = next(iter(items))
    val_sample = items[key_sample]
    sig_k = PureSet.get_signature(key_sample)
    sig_v = PureSet.get_signature(val_sample)

    keys = []
    values = []
    tuples = []
    seen_keys = set()
    for k, v in items.items():
      ksig = PureSet.get_signature(k)
      vsig = PureSet.get_signature(v)
      if ksig != sig_k: raise TypeError(f"Key type/shape mismatch:\nExp: {sig_k}\nGot: {ksig}")
      if vsig != sig_v: raise TypeError(f"Value type/shape mismatch:\nExp: {sig_v}\nGot: {vsig}")
      if k in seen_keys: raise TypeError(f"Duplicate key detected in PureMap: {k!r}")
      seen_keys.add(k)
      keys.append(k)
      values.append(v)
      tuples.append((k, v))

    self._signature_k = sig_k
    self._signature_v = sig_v
    self._items_dict = dict(tuples)
    self._restored_map = None

    super().__init__(*tuples)

    self._keys = PureSet(*keys)
    self._values = PureSet(*values)

  @property
  def signature(self): return (self._signature_k, self._signature_v)

  def __getitem__(self, key): return self._items_dict[key]

  def __iter__(self): return iter(self._items_dict)

  def __len__(self): return len(self._items_dict)

  def __contains__(self, key): return key in self._items_dict

  @property
  def items(self): return self._items_dict.items()

  @property
  def keys(self): return self._keys

  @property
  def values(self): return self._values

  @property
  def restored(self):
    if self._restored_map is not None: return tuple(self._restored_map.values())
    self._restored_map = self.as_dict()
    return tuple(self._restored_map.values())

  def as_dict(self):
    result = {}
    for frozen in self._items:
      k, v = PureSet.restore(frozen)
      result[k] = v
    return result

  def as_map(self):
    return MappingProxyType(self.as_dict())

  def __repr__(self):
    return f"PureMap({', '.join(f'{k!r}: {v!r}' for k, v in self.as_dict().items())})"

  def __str__(self):
    return self.__repr__()

  def copy(self):
    return PureMap(self._items_dict.copy())

  def get(self, key, default=None): return self._items_dict.get(key, default)

if __name__ == '__main__':
  import doctest
  doctest.testmod()