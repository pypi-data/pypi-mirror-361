<p align="center">
<img src="https://raw.githubusercontent.com/gabrielmsilva00/pureset/e920683cd8f19ac740eb1f06cc4df1a30a5fe5d1/img/PureSet.svg"><br/>
<a href="https://python.org/downloads"><img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version" width=256 style="vertical-align:middle;margin:5px"><br/>
<a href="https://www.apache.org/licenses/LICENSE-2.0.txt"><img src="https://img.shields.io/badge/License-Apache%202.0-green.svg" alt="License" width=256 style="vertical-align:middle;margin:5px"><br/>
<a href="https://github.com/gabrielmsilva00/pureset"><img src="https://img.shields.io/badge/GitHub-Repository-2A3746?logo=github" width=256 style="vertical-align:middle;margin:5px"><br/>
<a href="https://pypi.org/project/pureset"><img src="https://img.shields.io/pypi/v/pureset.svg?logo=pypi" alt="Version" width=256 style="vertical-align:middle;margin:5px"><br/>
</p>

<p align="center">
<h1 align="center">pureset</h1>
<h6 align="center">For general Python development matters, being this package or any, contact me at<br/><a href="mailto:gabrielmaia.silva00@gmail.com">gabrielmaia.silva00@gmail.com<a/><h6>
</p>

---

#### A robust, immutable, homogeneous, and ordered collection library for Python, blending the best features of sets, tuples, sequences, and mappings.

**PureSet** and **PureMap** offer _accuracy, predictability_, and _clarity_ in managing **homogeneous data structures**.

They ensure **type homogeneity** across elements or entries, making them robust **replacements for sets, sequences, or dictionaries** in production applications.

**NumPy** and **Pandas** support is added with no dependency to the package itself. Currently supported types are:
- `numpy.ndarray`
- `pandas.Series`
- `pandas.DataFrame`
- `pandas.Index`

---

## **Core Features**

- **Immutability:** Elements (PureSet) and key-value pairs (PureMap) cannot be changed after creation, assuring data integrity.
- **Ordering:** Retains insertion sequence—predictable for iteration, exporting, or display use cases.
- **Hashability:** Collections of hashable (and nested) objects are themselves hashable; can be used as dictionary keys.
- **Uniqueness:** Sets remove duplicates by value; maps ensure unique keys.
- **Deep Type & Schema Homogeneity:** All elements (PureSet) or keys and values (PureMap) must share the same type and “shape”.
- **Performance:** Optimized for membership, intersection, union, mapping, and set-like operations—even at scale.
- **Signature Inspection:** `.signature` property represents the canonical type/structure, for debugging and schema checks.
- **Universal Container:** Works seamlessly with primitives, containers, numpy, pandas, UserString/UserList/..., and nested containers.
- **Extensible:** Transparent support for new types via freeze/restore protocol.
- **Serialization Ready:** Pickleable and custom freeze/restore.
- **Advanced API:** Set operations, mapping/filtering, slices, composition, schema validation, and more, for both types.

---

## **Installation & Requirements**

To install the latest `PureSet` package, use pip:

```bash
pip install -U pureset
```

- **Python Versions:** Python 3.9+.
- **Dependencies:** None!

---

## **Usage & API Overview**

This section presents realistic, production-focused examples for both `PureSet` and `PureMap`.

---

### Basic Example Usage**

```pycon
>>> from pureset import PureSet
>>> PureSet(1, 2, 3)
PureSet(1, 2, 3)
>>> PureSet(1, 2, 2, 3)
PureSet(1, 2, 3)
>>> PureSet("a", "b", "b")
PureSet('a', 'b')
>>> len(PureSet(8, 8, 9))
2

>>> from pureset import PureMap
>>> pm = PureMap(a=1, b=2)
>>> pm['a']
1

>>> user_ages = PureMap({"alice": 30, "bob": 28})
>>> set(user_ages.keys())
{'alice', 'bob'}
>>> user_ages.signature
(<class 'str'>, <class 'int'>)

>>>PureMap({1: 'abc', "key": 123})
Traceback (most recent call last):
  ...
TypeError: All keys/values must be of the same type/shape.
```

---

### **PureSet: Robust Enum Replacement | State Management**

```pycon
>>> ORDER_STATES = PureSet("Pending", "Processing", "Shipped", "Delivered", "Cancelled")
>>> "Processing" in ORDER_STATES
True
>>> "Returned" in ORDER_STATES
False
```

---

### **PureSet: Contracts & API Schema Checking**

```pycon
>>> user_profiles = PureSet(
...   {"id": 1, "name": "Alice Smith", "age": 28, "email": "alice@example.com"},
...   {"id": 2, "name": "Bob Johnson", "age": 35, "email": "bob@example.com"},
... )
>>> user_profiles.signature
(<class 'dict'>, {'age': <class 'int'>, 'email': <class 'str'>, 'id': <class 'int'>, 'name': <class 'str'>})
```

---

### **Deduplication and Set Algebra (PureSet)**

```pycon
>>> a = PureSet(1, 2, 3)
>>> b = PureSet(3, 4, 2)
>>> (a | b).to_list()
[1, 2, 3, 4]
>>> (a & b).to_list()
[2, 3]
>>> (a - b).to_list()
[1]
>>> (a ^ b).to_list()
[1, 4]
```

---

### **Using PureSet and PureMap with Numpy and Pandas**

```pycon
>>> import numpy as np, pandas as pd
>>> arr = np.array([1, 2, 3])
>>> ps = PureSet(arr)
>>> ps[0].shape
(3,)

>>> df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
>>> PureSet(df)[0].equals(df)
True
>>> PureMap({0: df})[0].equals(df)
True

>>> idx = pd.Index([5, 7, 9])
>>> PureSet(idx)[0].equals(idx)
True
```

---

### **Freeze/Restore: Reliable, Deep Immutability and Serialization**

```pycon
>>> x = [{'a': [1, 2]}, {'a': [3, 4]}]
>>> frozen = PureSet.freeze(x)
>>> PureSet.restore(frozen)
[{'a': [1, 2]}, {'a': [3, 4]}]
```

```pycon
>>> pm = PureMap({'k1': [1, 2]})
>>> PureMap.restore(PureMap.freeze(pm)) == pm
True
```

---

## **Advanced Features and Extensibility**

- **Rich Set Algebra (PureSet):** `|`, `&`, `-`, `^`
- **Dict-like Operations (PureMap):** all mapping protocol methods, plus strict homogeneity and freezing.
- **Slicing and Indexing:** Supports Pythonic sequence semantics.
- **Compatibility Checking:** `.compatible(other)` method.
- **Signature Inspection:** `.signature` for schema introspection.
- **Freeze/Restore API:** For both types.
- **Mixes with UserString, Counter, ChainMap, deque, array.array, memoryview, and more.**

---

## **Performance and Scalability**

- Highly optimized for construction, lookup, set/mapping algebra.
- PureSet and PureMap scale efficiently for large practical workloads.

---

## **Testing**

> ###### v1.2.250706.0: 88 tests; 0 Failures; 0 Errors; OK.

Test suite covers all PureSet and PureMap core and edge-case behaviors:

  - Edge cases for numpy, pandas, UserDict/UserList/UserString, Counter, deque, ChainMap
  - Nested, empty, custom, standard containers
  - Contract enforcement for mixed and homogeneous datasets
  - Deep serialization and "restoration" safety

See tests [here](https://github.com/gabrielmsilva00/pureset/blob/main/tests/).

---

## **License**

Released under **Apache License 2.0**. See [LICENSE](LICENSE).

---

> **PureSet and PureMap are engineered to safely power production-scale scenarios across APIs, analytics, ML, and more!**