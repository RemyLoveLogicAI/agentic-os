<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "research/docs/recursive-mas/reference/recursive_mas.py",
  "source_hash": "00e181ae1f40d1f0d316c999aa17946651733480803d02a859ac82f2eaeef241",
  "last_updated": "2026-05-02T16:28:35.928274+00:00",
  "tokens_used": 191402,
  "complexity_score": 6,
  "estimated_review_time_minutes": 30,
  "external_dependencies": []
}
```

</details>

[Documentation Home](../../../../README.md) > [research](../../../README.md) > [docs](../../README.md) > [recursive-mas](../README.md) > [reference](./README.md) > **recursive_mas**

---

# recursive_mas.py

> **File:** `research/docs/recursive-mas/reference/recursive_mas.py`

![Complexity: Medium](https://img.shields.io/badge/Complexity-Medium-yellow) ![Review Time: 30min](https://img.shields.io/badge/Review_Time-30min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Usage Examples](#usage-examples)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

Implements end-to-end processing for RecursiveMAS specifications expressed as JSON. It defines typed dataclasses for the MAS model, validates and normalizes inner-link grammar (resolve_inner_links), and deterministically unrolls recursive agent graphs into a DAG (unroll). Outputs canonical JSON and sha256 digests for reproducible artifacts.

The module is pure standard-library Python and exposes a small CLI (validate, unroll, emit). Errors raise a structured RecursiveMasError serialized as canonical JSON. Unrolling respects depth/fuel caps and supports optional fixed-point detection to stop when bodies repeat.

## Dependencies

### Internal Dependencies

| Module | Usage |
| --- | --- |
| `__future__` | from __future__ import annotations enables postponed evaluation of annotations (used broadly in type hints across dataclasses). |
| `argparse` | Used by main() to parse CLI subcommands and options for validate, unroll and emit (ArgumentParser, subparsers, add_argument). |
| `datetime` | Imported as _dt and used in emit_build_artifacts() to generate an RFC-like timestamp for the manifest (generated_at). |
| `hashlib` | Used to compute sha256 digests for canonical JSON blobs: digest() returns 'sha256:' + hex, and emit_build_artifacts writes artifact hashes for files. |
| `json` | Used for parsing input JSON (_load_json) and serializing canonical JSON (canonical_json) with deterministic settings for hashing and output. |
| `re` | Regular expressions declared at module level (NODE_ID_RE, MAS_ID_RE, PORT_RE) used throughout validation logic (Node.from_dict, MasBody.from_dict, Endpoint.from_dict, Link.from_dict). |
| `sys` | Used by CLI handlers to write stdout and stderr and to return exit codes (in main and subcommand functions). |
| `dataclasses` | Provides @dataclass decorator and field() used to define immutable/value dataclasses (many types such as Ports, Node, MasBody, ResolvedBody, UnrolledNode, Frame, etc.) and to supply default_factory for _UnrollState lists. |
| `pathlib` | Path is used in emit_build_artifacts and CLI helpers to read/write JSON files, create directories and mirror artifacts. |
| `typing` | Used for type annotations (Any, Mapping, Optional, Sequence) across function signatures and dataclass fields. |

## 📁 Directory

This file is part of the **reference** directory. View the [directory index](_docs/research/docs/recursive-mas/reference/README.md) to see all files in this module.

## Architecture Notes

- Two-phase pipeline: first validate/normalize inner links into a ResolvedInnerLinks structure (resolve_inner_links) to ensure inner-link grammar is correct and deterministic; then unroll recursion into frames/links (unroll) using depth/fuel caps and optional fixed-point detection.
- Canonicalization and digesting: canonical_json produces deterministic encoding (sorted keys, no extraneous spaces, explicit U+2028/U+2029 escaping) used by digest() to create sha256 fingerprints; this ensures reproducible artifact generation and fixed-point comparisons.
- Error model: structured RecursiveMasError carries code/where/message and is serialized as canonical JSON on CLI errors (main catches it and writes to stderr with exit code 3).

## Usage Examples

### Validate a MAS spec for inner-link correctness

recursive_mas validate my_spec.json -> prints canonical JSON of ResolvedInnerLinks. The validator loads the JSON, constructs Mas via load_mas(), and calls resolve_inner_links(mas).

### Unroll a MAS spec into a deterministic DAG

recursive_mas unroll my_spec.json [--max-depth N] [--fuel F] [--no-fixed-point] -> prints canonical JSON of UnrolledDag. The CLI calls load_mas(), then unroll() with provided caps to produce frames, links and evidence records.

### Emit canonical build artifacts

recursive_mas emit --emit-build-artifacts outdir [--also-mirror mirrordir] -> writes example.mas.json, inner-links.example.json, loop-unrolling.example.json and manifest.json to outdir and optionally mirrors them. Uses example_mas_spec() to populate artifacts.

## Maintenance Notes

- canonical_json explicitly escapes U+2028 and U+2029 to maintain JCS-like determinism; any change to serialization must preserve these rules to keep digest compatibility.
- Fixed-point detection uses canonical_json(body.to_dict()) and compares per mas_id; changing canonicalization or to_dict ordering will affect fixed-point behavior and artifact digests.
- Limits: unroll() prefers explicit CLI overrides (max_depth, fuel), falls back to root.limits if present, otherwise uses DEFAULT_MAX_DEPTH and DEFAULT_FUEL. Negative values raise a RecursiveMasError.

---

## Navigation

**↑ Parent Directory:** [Go up](_docs/research/docs/recursive-mas/reference/README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*


---

## Functions and Classes


#### __init__

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def __init__(self, code: str, where: str, message: str) -> None
```

### Description

Initializes the instance by constructing the exception message via the superclass constructor and storing the provided code, location, and message on the instance.


This constructor formats a single string "{code} at {where}: {message}" and passes it to the superclass __init__ (presumably an Exception subclass) to set the exception's message. It then assigns the three input values to instance attributes self.code, self.where, and self.message for later inspection.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `code` | `str` | ✅ | A short identifier or code representing the error or condition.
<br>**Constraints:** Expected to be a string, Used verbatim in the formatted exception message and stored on the instance |
| `where` | `str` | ✅ | A string describing where the error occurred (e.g., function, module, or location).
<br>**Constraints:** Expected to be a string, Used verbatim in the formatted exception message and stored on the instance |
| `message` | `str` | ✅ | A human-readable message describing the error or condition.
<br>**Constraints:** Expected to be a string, Used verbatim in the formatted exception message and stored on the instance |

### Returns

**Type:** `None`

Constructors in Python do not return a value; this method returns None and initializes the instance state.


**Possible Values:**

- None

### Side Effects

> ❗ **IMPORTANT**
> This function has side effects that modify state or perform I/O operations.

- Sets instance attributes: self.code, self.where, self.message
- Calls superclass __init__ to set the exception message (mutates base exception state)

### Complexity

O(1)

### Related Functions

- `__init__` - Calls the superclass's __init__ (e.g., Exception.__init__) to initialize the base exception message

### Notes

- The formatted message passed to super().__init__ is "{code} at {where}: {message}".
- There is no validation of parameter contents; non-string types will be converted by f-string formatting or may raise if incompatible.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, str]
```

### Description

Return a dictionary containing the instance attributes code, where, and message mapped to the keys 'code', 'where', and 'message'.


The method constructs and returns a new dict literal with three entries by reading the instance attributes self.code, self.where, and self.message. It performs no validation or transformation of those attributes and simply packages their current values into the returned dictionary.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `implicit instance reference` | ✅ | Reference to the instance whose attributes code, where, and message are accessed and returned.
<br>**Constraints:** The instance must have attributes 'code', 'where', and 'message' accessible at call time, Attributes are expected to be str to match the annotated return type but not enforced by the method |

### Returns

**Type:** `dict[str, str]`

A dictionary with keys 'code', 'where', and 'message' whose values are taken directly from self.code, self.where, and self.message.


**Possible Values:**

- A dict like {'code': <self.code>, 'where': <self.where>, 'message': <self.message>}
- If attributes exist but are not strings, the returned dict will contain their actual values (violating the annotated type)

### Complexity

O(1)

### Notes

- The method does not perform any validation or type coercion; it assumes the instance attributes exist.
- If any of the attributes are missing, an AttributeError will be raised by Python at call time (not explicitly by this method).

---



#### from_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def from_dict(d: Mapping[str, Any], where: str) -> "Ports":
```

### Description

Validate a mapping describing ports and construct a Ports instance from it; raises errors for invalid shapes, names, or duplicates.


The function verifies that the input d is a Mapping, extracts 'in' and 'out' entries (defaulting to empty sequences), normalizes them to tuples, and validates each port name against a regular expression PORT_RE and type str. It also checks for duplicate names within the 'in' and 'out' lists. If all validations pass it returns a Ports object created from the two tuples.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `d` | `Mapping[str, Any]` | ✅ | A mapping expected to contain optional 'in' and 'out' entries describing port names.
<br>**Constraints:** Must be an instance of collections.abc.Mapping, 'in' and 'out' keys, if present, should be iterable (e.g., list/tuple) of port names or falsy to be treated as empty, Each port must be a str and must match the PORT_RE regular expression, No duplicate names are allowed within 'in' and within 'out' separately |
| `where` | `str` | ✅ | A location/context string used in error messages to indicate where the validation failed.
<br>**Constraints:** Should be a string (used only in error construction) |

### Returns

**Type:** `Ports`

A Ports instance constructed with two tuples: (in_ports_tuple, out_ports_tuple).


**Possible Values:**

- Ports(in_tuple, out_tuple) when d is valid
- No return if an exception is raised

### Raises

| Exception | Condition |
| --- | --- |
| `RecursiveMasError` | When d is not a Mapping (message: 'ports must be an object') |
| `RecursiveMasError` | When any port name is not a str or does not match PORT_RE (message: 'bad port name: ...') |
| `RecursiveMasError` | When there are duplicate names in the 'in' ports (message: 'duplicate ports.in') |
| `RecursiveMasError` | When there are duplicate names in the 'out' ports (message: 'duplicate ports.out') |

### Complexity

O(n) where n is total number of port names in 'in' plus 'out' (checks and set constructions are linear)

### Related Functions

- `Ports` - Constructor used to create and return the validated Ports instance
- `PORT_RE` - Regular expression used to validate individual port name strings

### Notes

- The function treats falsy values for d.get('in') or d.get('out') (e.g., None or empty list) as empty sequences.
- Duplicates are checked only within each of 'in' and 'out' separately; identical names appearing once in 'in' and once in 'out' are not considered a duplicate by this code.
- Errors include the provided 'where' string to indicate context of the schema error.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, list[str]]
```

### Description

Return a dictionary with keys 'in' and 'out' where the values are lists constructed from the instance attributes self.in_ and self.out.


This method creates and returns a new dictionary with two keys: 'in' mapped to list(self.in_) and 'out' mapped to list(self.out). It uses the built-in list() constructor to convert the attributes (which may be any iterable) into concrete lists and returns that mapping directly.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `unannotated` | ✅ | The instance whose in_ and out attributes are used to build the returned dictionary.
<br>**Constraints:** self must have attributes named in_ and out that are iterable |

### Returns

**Type:** `dict[str, list[str]]`

A dictionary with two entries: 'in' -> list(self.in_) and 'out' -> list(self.out).


**Possible Values:**

- A dict like {'in': [...], 'out': [...]} where the lists contain the elements from self.in_ and self.out respectively

### Complexity

O(n) where n is the total number of elements in self.in_ plus self.out (due to list() conversions)

### Notes

- The method does not modify self.in_ or self.out; it constructs new lists from them.
- If self.in_ or self.out are already lists, list(...) will produce a shallow copy.
- If self.in_ or self.out are not present or not iterable, a AttributeError or TypeError may occur when calling this method (these exceptions are not explicitly raised in the implementation).

---



#### from_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def from_dict(d: Mapping[str, Any], where: str) -> "Node":
```

### Description

Parse and validate a mapping (typically from parsed JSON/YAML) into a Node object, enforcing required fields, types, formats, and normalizing capabilities and annotations.


Checks that the input is a Mapping and enforces required keys and formats for id, kind, ports, optional sub_mas, capabilities, and annotations. Delegates ports parsing to Ports.from_dict, ensures only 'sub_mas' kind may include a sub_mas id, normalizes capabilities and annotations, and raises RecursiveMasError with contextual where on failure.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `d` | `Mapping[str, Any]` | ✅ | A mapping representing a node (e.g., parsed JSON/YAML) containing keys like 'id', 'kind', 'ports', 'sub_mas', 'capabilities', and 'annotations'.
<br>**Constraints:** Must be an instance of collections.abc.Mapping, Must contain 'id' whose value is a string matching NODE_ID_RE, If 'kind' == 'sub_mas', 'sub_mas' must be a string matching MAS_ID_RE, If 'kind' != 'sub_mas', 'sub_mas' must be absent or None, 'kind' must be one of: 'agent', 'sub_mas', 'self_recurse', 'capabilities' if present must be a list of non-empty strings with no duplicates, 'annotations' if present must be a Mapping |
| `where` | `str` | ✅ | A string describing the location/context in the source schema for error messages (used to build error where context).
<br>**Constraints:** Must be a string; used verbatim in raised RecursiveMasError messages |

### Returns

**Type:** `"Node"`

A Node instance constructed from validated and normalized input data. The Node is created with id, kind, ports (from Ports.from_dict), sub_mas (only for kind 'sub_mas'), capabilities as a sorted tuple, and annotations as a tuple of (key, value) pairs sorted by key.


**Possible Values:**

- A Node object with validated fields on success

### Raises

| Exception | Condition |
| --- | --- |
| `RecursiveMasError` | If d is not a Mapping |
| `RecursiveMasError` | If 'id' is missing, not a string, or does not match NODE_ID_RE |
| `RecursiveMasError` | If 'kind' is not one of ('agent', 'sub_mas', 'self_recurse') |
| `RecursiveMasError` | If kind == 'sub_mas' and 'sub_mas' is missing, not a string, or does not match MAS_ID_RE |
| `RecursiveMasError` | If kind != 'sub_mas' but 'sub_mas' is provided (non-None) |
| `RecursiveMasError` | If 'capabilities' is not a list of non-empty strings or contains duplicates |
| `RecursiveMasError` | If 'annotations' is present and is not a Mapping |

### Usage Examples

#### Parsing a node mapping obtained from JSON into a Node with validation

```python
node = Node.from_dict({'id': 'node1', 'kind': 'agent', 'ports': {}, 'capabilities': ['cap1'], 'annotations': {'a': 1}}, '/mas')
```

Demonstrates calling from_dict with a mapping; it validates fields, delegates ports parsing, and returns a Node with sorted capabilities and annotations.

### Complexity

O(n log n) where n is number of capabilities+annotations entries due to sorting; other checks are O(1) per field

### Related Functions

- `Ports.from_dict` - Called by from_dict to parse/validate the 'ports' sub-object
- `Node (constructor)` - from_dict returns an instance constructed via the Node constructor

### Notes

- Capabilities are normalized into a sorted tuple and duplicates are rejected (duplicate detection via set length comparison).
- Annotations are converted into a tuple of (key, value) pairs sorted by key; keys are coerced to str.
- The function relies on external regexes NODE_ID_RE and MAS_ID_RE for id validation and on Ports.from_dict for port validation.
- Error messages include contextual 'where' strings; the function does not perform any I/O or mutate input mappings.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, Any]
```

### Description

Construct and return a dictionary representation of the instance by reading several attributes and converting some of them into serializable forms.


Builds a dict with keys 'id', 'kind', and 'ports' (using self.ports.to_dict()). Conditionally includes 'sub_mas', 'capabilities' (as a list), and 'annotations' (converted via a comprehension) only if those attributes are truthy, then returns the result.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `implicit instance parameter` | ✅ | Reference to the instance whose attributes (id, kind, ports, sub_mas, capabilities, annotations) are used to build the output dictionary.
<br>**Constraints:** self must have attributes id, kind, and ports, self.ports must have a to_dict() method, If present, self.annotations must be iterable of (key, value) pairs for the dict comprehension to work |

### Returns

**Type:** `dict[str, Any]`

A dictionary containing at least 'id', 'kind', and 'ports', and optionally 'sub_mas', 'capabilities', and 'annotations' if those attributes are truthy on the instance.


**Possible Values:**

- A dict with keys 'id', 'kind', 'ports' and optionally 'sub_mas', 'capabilities', 'annotations'.
- The 'ports' value is the result of self.ports.to_dict().
- 'capabilities' appears as a list if present.
- 'annotations' appears as a dict if present.

### Complexity

O(1)

### Notes

- This implementation calls self.ports.to_dict(); any side effects or complexity of that call are not visible in this function.
- The annotations handling uses {k: v for k, v in self.annotations}, so self.annotations must be an iterable producing (key, value) pairs (e.g., a list of tuples); it is not treated as a mapping directly.
- capabilities are converted to a list with list(self.capabilities) — if capabilities is already a list this creates a shallow copy.

---



#### from_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def from_dict(d: Mapping[str, Any], where: str) -> "Endpoint":
```

### Description

Validate a mapping describing an endpoint and return an Endpoint instance; raise RecursiveMasError if the input shape or values are invalid.


The function first checks that the provided d is a Mapping and raises RecursiveMasError if not. It then extracts 'node' and 'port' from the mapping, validates that 'node' is a string and either equals OUTER or matches NODE_ID_RE, and validates that 'port' is a string that matches PORT_RE; if validations pass it constructs and returns an Endpoint(node, port).

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `d` | `Mapping[str, Any]` | ✅ | A mapping (typically a dict-like object) expected to contain keys 'node' and 'port' describing an endpoint.
<br>**Constraints:** Must be an instance of collections.abc.Mapping, Must contain 'node' value that is a str and either equals OUTER or matches NODE_ID_RE, Must contain 'port' value that is a str and matches PORT_RE |
| `where` | `str` | ✅ | A location/context string used in error messages when raising RecursiveMasError.
<br>**Constraints:** Must be a string (used only for error reporting) |

### Returns

**Type:** `Endpoint`

An Endpoint object constructed with the validated node and port values from the mapping.


**Possible Values:**

- Endpoint(node, port) — when input is valid

### Raises

| Exception | Condition |
| --- | --- |
| `RecursiveMasError` | If d is not a Mapping (error.schema.shape) with message 'endpoint must be an object' |
| `RecursiveMasError` | If node is not a str or is not equal to OUTER and does not match NODE_ID_RE (error.schema.shape, message includes bad endpoint.node) |
| `RecursiveMasError` | If port is not a str or does not match PORT_RE (error.schema.shape, message includes bad endpoint.port) |

### Complexity

O(1)

### Related Functions

- `Endpoint` - Constructed/returned by this function (Endpoint(node, port))

### Notes

- Validation relies on module-level constants OUTER, NODE_ID_RE, and PORT_RE; the function uses d.get so missing keys become None and will fail type/regex checks.
- The 'where' parameter is only used to populate RecursiveMasError to indicate the error location/context.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, str]
```

### Description

Return a dictionary with the object's 'node' and 'port' attribute values.


This method constructs and returns a new dict literal with two keys: 'node' and 'port'. It retrieves values directly from self.node and self.port and places them into the returned dictionary. There is no additional processing, validation, or mutation of state.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `implicit instance parameter` | ✅ | Reference to the instance whose node and port attributes will be read
<br>**Constraints:** The instance must have attributes named 'node' and 'port' accessible at call time |

### Returns

**Type:** `dict[str, str]`

A dictionary with exactly two entries: {'node': self.node, 'port': self.port}


**Possible Values:**

- A dict mapping 'node' to the value of self.node and 'port' to the value of self.port

### Raises

| Exception | Condition |
| --- | --- |
| `AttributeError` | If the instance does not have 'node' or 'port' attributes (accessing them will raise AttributeError) |

### Complexity

O(1)

### Notes

- The method returns the attribute values as-is; it does not copy, validate, or convert types.
- If self.node or self.port are not strings, the returned dict value types may differ from the annotated dict[str, str].

---



#### from_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def from_dict(d: Mapping[str, Any], where: str) -> "Link"
```

### Description

Constructs and returns a Link object from a dictionary representation, validating shape and specific fields.


Validates that d is a Mapping, parses the 'from' and 'to' endpoint sub-objects via Endpoint.from_dict (using empty dict if missing), and reads an optional 'kind' (defaulting to 'data') and optional 'guard'. It returns a new Link constructed from the parsed endpoints, kind, and guard, and raises RecursiveMasError on validation failures with location-aware messages.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `d` | `Mapping[str, Any]` | ✅ | A mapping (typically a dict) containing the serialized Link data; expected keys include 'from', 'to', optional 'kind', and optional 'guard'.
<br>**Constraints:** Must be an instance of collections.abc.Mapping, 'from' and 'to' sub-objects are processed via Endpoint.from_dict (defaults to empty dict if missing), 'kind' if present must be one of 'data', 'control', or 'evidence' (defaults to 'data'), 'guard' if present must be a non-empty string |
| `where` | `str` | ✅ | A string describing the location/context used in error messages to indicate where validation failed.
<br>**Constraints:** Provided value is used only in error messages; no validation is performed on its contents in this function |

### Returns

**Type:** `"Link"`

A Link instance constructed from the parsed 'from' and 'to' Endpoints, the validated kind, and the optional guard string.


**Possible Values:**

- A Link object created as Link(f_endpoint, t_endpoint, kind, guard)

### Raises

| Exception | Condition |
| --- | --- |
| `RecursiveMasError` | If d is not a Mapping (raises with code 'error.schema.shape' and message 'link must be an object') |
| `RecursiveMasError` | If 'kind' is present and not one of 'data', 'control', or 'evidence' (raises with code 'error.schema.shape' and message indicating bad link.kind) |
| `RecursiveMasError` | If 'guard' is present and is not a non-empty string (raises with code 'error.schema.shape' and message indicating bad link.guard) |

### Complexity

O(1)

### Related Functions

- `Endpoint.from_dict` - Called by this function to parse the 'from' and 'to' endpoint sub-objects
- `Link` - Constructor used to create the returned Link instance

### Notes

- If 'from' or 'to' keys are missing in d, Endpoint.from_dict is called with an empty dict and the same where suffix (i.e., f"{where}/from" or f"{where}/to").
- The 'kind' field defaults to 'data' when absent.
- The function embeds the provided 'where' into error locations to help locate the offending part of input data.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, Any]:
```

### Description

Constructs and returns a dictionary representation of the object's select attributes: 'from', 'to', 'kind', and optionally 'guard'.


The method creates a new dict with keys 'from', 'to', and 'kind'. It populates 'from' and 'to' by calling to_dict() on the self.from_ and self.to attributes, and copies the value of self.kind directly. If self.guard is not None, the method adds a 'guard' key with that value. Finally, it returns the assembled dictionary.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `implicit instance parameter` | ✅ | The instance whose attributes (from_, to, kind, guard) are read to build the dictionary representation.
<br>**Constraints:** self.from_ must have a to_dict() method that returns a dict-like value, self.to must have a to_dict() method that returns a dict-like value, self.kind should be serializable into the resulting dict (e.g., JSON-serializable if needed), self.guard may be any value; if it is None it will be omitted |

### Returns

**Type:** `dict[str, Any]`

A dictionary containing serialized sub-objects and scalar attributes of the instance. Always contains 'from', 'to', and 'kind'. Contains 'guard' only if self.guard is not None.


**Possible Values:**

- {"from": <dict>, "to": <dict>, "kind": <Any>}
- {"from": <dict>, "to": <dict>, "kind": <Any>, "guard": <Any>}

### Complexity

O(1)

### Related Functions

- `from_.to_dict` - Called by this method to serialize the 'from' sub-object
- `to.to_dict` - Called by this method to serialize the 'to' sub-object

### Notes

- This method does not mutate the instance; it only reads attributes and constructs a new dict.
- It assumes self.from_ and self.to implement a to_dict() method; if they do not, an AttributeError will occur at runtime.
- The key name for the source attribute is 'from' in the output, while the instance attribute is named from_ to avoid using the reserved word 'from'.

---



#### sort_key

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def sort_key(self) -> tuple[str, str, str, str, str, str]:
```

### Description

Return a 6-tuple composed of specific attributes from self (from_.node, from_.port, to.node, to.port, kind, guard or empty string).


The method constructs and returns a tuple of six string values taken directly from the instance: the node and port of self.from_, the node and port of self.to, the instance's kind, and the guard attribute (or an empty string if guard is falsy). The implementation performs no mutation or I/O; it simply reads attributes and returns them in a fixed ordering useful for sorting or comparisons.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `implicit instance` | ✅ | The instance from which attributes are read: expects attributes from_.node, from_.port, to.node, to.port, kind, and guard.
<br>**Constraints:** self.from_ must expose attributes 'node' and 'port', self.to must expose attributes 'node' and 'port', self.kind must be present, self.guard may be None or a string; falsy guard will be coerced to empty string in the returned tuple |

### Returns

**Type:** `tuple[str, str, str, str, str, str]`

A 6-tuple of strings: (from_.node, from_.port, to.node, to.port, kind, guard_or_empty). If guard is falsy (e.g., None or empty), the last element is an empty string.


**Possible Values:**

- ('nodeA', 'port1', 'nodeB', 'port2', 'some_kind', 'some_guard')
- ('nodeA', 'port1', 'nodeB', 'port2', 'some_kind', '')

### Complexity

O(1)

### Notes

- The method does not validate types of the attributes; it assumes the attributes exist and are usable as strings.
- The guard attribute is normalized to an empty string when falsy to ensure a consistent tuple element type.

---



#### from_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def from_dict(d: Mapping[str, Any], where: str, *, allow_self_recurse: bool) -> "MasBody"
```

### Description

Parse and validate a dictionary representation of a MasBody and construct a MasBody instance, performing schema and consistency checks.


Validate that d is a mapping, extract and verify mas_id, and build nodes, links, and sub_mas by delegating to Node.from_dict, Link.from_dict, and MasBody.from_dict. Enforce uniqueness and self-recurse constraints, validate optional limits, and return a MasBody instance or raise on errors.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `d` | `Mapping[str, Any]` | ✅ | The source dictionary expected to represent a MasBody JSON/object structure.
<br>**Constraints:** Must be a Mapping; otherwise raises RecursiveMasError('error.schema.shape'), Must contain 'mas_id' that is a str and matches MAS_ID_RE |
| `where` | `str` | ✅ | A string describing the location/context in the document for use in error messages.
<br>**Constraints:** Used verbatim to construct error 'where' paths in raised RecursiveMasError exceptions |
| `allow_self_recurse` | `bool` | ✅ | Keyword-only flag that permits nodes of kind 'self_recurse' when True; disallowed at root when False.
<br>**Constraints:** If False, any node with n.kind == 'self_recurse' causes a RecursiveMasError('error.node.self_recurse_at_root'), When parsing sub_mas, the function calls MasBody.from_dict(..., allow_self_recurse=True) regardless |

### Returns

**Type:** `MasBody`

A MasBody instance constructed from the validated contents of the input mapping, with fields mas_id, nodes (tuple of Node), links (tuple of Link), sub_mas (tuple of MasBody), and optional limits as a (max_depth, fuel) tuple or None.


**Possible Values:**

- A MasBody object populated from d
- No return (function raises RecursiveMasError on validation failures)

### Raises

| Exception | Condition |
| --- | --- |
| `RecursiveMasError` | If d is not a Mapping (error.schema.shape) |
| `RecursiveMasError` | If mas_id is missing, not a str, or does not match MAS_ID_RE (bad mas_id) |
| `RecursiveMasError` | If two nodes have the same id (error.node.id_collision) |
| `RecursiveMasError` | If a node has kind 'self_recurse' but allow_self_recurse is False (error.node.self_recurse_at_root) |
| `RecursiveMasError` | If two sub_mas have the same mas_id within this scope (error.schema.shape) |
| `RecursiveMasError` | If limits.max_depth is present and is not a non-negative int (error.budget.invalid) |
| `RecursiveMasError` | If limits.fuel is present and is not a non-negative int (error.budget.invalid) |

### Usage Examples

#### Parsing a MasBody dictionary at the document root

```python
MasBody.from_dict(data_dict, "/root", allow_self_recurse=False)
```

Parses data_dict as a root MasBody, disallowing nodes with kind 'self_recurse' at this level; raises RecursiveMasError on validation errors.

### Complexity

O(n) where n is the total number of nodes + links + sub_mas processed (includes recursive parsing of sub_mas)

### Related Functions

- `Node.from_dict` - Called by this function to parse each node entry
- `Link.from_dict` - Called by this function to parse each link entry

### Notes

- Sub-mas bodies are parsed with allow_self_recurse=True regardless of the caller's allow_self_recurse, enabling 'self_recurse' only inside sub_mas.
- Defaults for limits components use DEFAULT_MAX_DEPTH and DEFAULT_FUEL when keys are missing; those constants are referenced in the function but not defined in this snippet.
- The function constructs tuples for nodes, links, and sub_mas and returns them in the MasBody constructor.
- This implementation performs no I/O and does not mutate external state; it may recursively call MasBody.from_dict for nested sub_mas.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, Any]
```

### Description

Construct and return a dictionary representation of the instance by serializing its mas_id, nodes, links, and optional sub_mas and limits attributes.


Builds and returns a dict with the instance's mas_id plus serialized nodes and links. Nodes are sorted by node.id and links by link.sort_key() before calling their to_dict() methods. If present, sub_mas is added as a list of serialized sub-MAS sorted by mas_id, and limits is added as a dict with max_depth and fuel from the two-element limits tuple.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `Any (instance of the enclosing class)` | ✅ | The instance whose attributes (mas_id, nodes, links, optional sub_mas and limits) are serialized into a dict.
<br>**Constraints:** self must have attribute mas_id, self.nodes must be an iterable of objects with attribute id and a to_dict() method, self.links must be an iterable of objects with a sort_key() method and a to_dict() method, if present, self.sub_mas must be an iterable of objects with mas_id and to_dict(), if present, self.limits must be indexable with at least two elements (limits[0], limits[1]) |

### Returns

**Type:** `dict[str, Any]`

A dictionary representing the instance, containing keys: mas_id, nodes (list of node dicts), links (list of link dicts), and optionally sub_mas (list of sub-MAS dicts) and limits (dict with max_depth and fuel).


**Possible Values:**

- A dict with keys: 'mas_id', 'nodes', 'links'.
- Additionally, if self.sub_mas is truthy, includes key 'sub_mas' with a list of serialized sub-MAS.
- Additionally, if self.limits is not None, includes key 'limits' with {'max_depth': limits[0], 'fuel': limits[1]}.

### Complexity

O(N log N) where N is the number of items being sorted (nodes, links, and optionally sub_mas); serialization cost of nested to_dict calls adds to this.

### Notes

- Nodes are sorted using the attribute n.id; links are sorted using l.sort_key(). If those attributes/methods are absent on elements, a runtime AttributeError will occur.
- limits is expected to be an indexable with at least two elements; the function does not validate types beyond indexing.
- The method delegates serialization of nested elements to their to_dict() methods; it performs no deep validation or mutation.

---



#### from_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def from_dict(d: Mapping[str, Any]) -> "Mas":
```

### Description

Validate that the input is a Mapping representing a MAS specification, check the schema_version, delegate body parsing to MasBody.from_dict, and return a Mas instance constructed from the parsed data.


The function first ensures the provided argument is a Mapping and raises RecursiveMasError if not. It then extracts the schema_version key and verifies it equals SCHEMA_VERSION_INPUT, raising RecursiveMasError for mismatches. Finally it calls MasBody.from_dict(d, "/", allow_self_recurse=False) to produce the root body and returns a Mas object constructed with the schema_version and parsed root.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `d` | `Mapping[str, Any]` | ✅ | A mapping (typically a dict-like object) expected to contain the MAS specification including a 'schema_version' key and other fields consumed by MasBody.from_dict.
<br>**Constraints:** Must be an instance of collections.abc.Mapping (checked with isinstance), Must contain a 'schema_version' entry whose value equals SCHEMA_VERSION_INPUT (otherwise an error is raised) |

### Returns

**Type:** `Mas`

A Mas instance constructed from the validated schema_version and the parsed body returned by MasBody.from_dict.


**Possible Values:**

- A Mas object with fields schema_version set to the input schema version and root set to the MasBody parsed result
- No return when an exception is raised

### Raises

| Exception | Condition |
| --- | --- |
| `RecursiveMasError` | Raised if d is not a Mapping (message 'MAS spec must be an object'). |
| `RecursiveMasError` | Raised if the 'schema_version' value in d does not equal SCHEMA_VERSION_INPUT (message indicates unknown version and the received value). |

### Complexity

O(1)

### Related Functions

- `MasBody.from_dict` - Called by this function to parse the body portion of the MAS spec (delegation).
- `Mas (constructor)` - Used to construct and return the resulting Mas instance from schema_version and parsed body.

### Notes

- The function only checks that d is a Mapping and that d.get('schema_version') equals SCHEMA_VERSION_INPUT; it relies on MasBody.from_dict to validate and parse the remainder of the structure.
- Error messages and exact error codes come from RecursiveMasError initializations in the function.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, Any]
```

### Description

Construct and return a dictionary containing the object's schema_version and the contents of self.root.to_dict().


This method builds and returns a new dict starting with {'schema_version': self.schema_version} and then updates it with the mapping returned by self.root.to_dict(). Keys from self.root.to_dict() overwrite any existing keys, including 'schema_version'.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `implicit instance parameter` | ✅ | Reference to the instance on which the method is called; used to access self.schema_version and self.root
<br>**Constraints:** self must have attributes 'schema_version' and 'root', self.root must expose a callable to_dict() method that returns a dict[str, Any] |

### Returns

**Type:** `dict[str, Any]`

A dictionary containing at least the key 'schema_version' and all key/value pairs returned by self.root.to_dict(); values from self.root.to_dict() override existing keys in the result.


**Possible Values:**

- A dictionary with merged keys from {'schema_version': self.schema_version} and the dict returned by self.root.to_dict()
- If self.root.to_dict() returns an empty dict, the result will be {'schema_version': self.schema_version}

### Complexity

O(1)

### Related Functions

- `root.to_dict` - Called by this method; its returned mapping is merged into the result

### Notes

- The method returns a new dictionary and does not mutate self or self.root.
- If the dictionary returned by self.root.to_dict() contains a 'schema_version' key, it will overwrite the value set from self.schema_version due to dict.update behavior.

---



#### _canon_replace

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _canon_replace(s: str) -> str
```

### Description

Return the input string with Unicode characters U+2028 and U+2029 replaced by the two-character escape sequences "\\u2028" and "\\u2029" respectively.


The function calls str.replace twice in a chained manner: first replacing any line separator character (U+2028) with the four-character sequence backslash-u-2-0-2-8, then replacing any paragraph separator character (U+2029) with backslash-u-2-0-2-9. It operates by returning a new string and does not mutate the input.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `s` | `str` | ✅ | Input string to process; characters U+2028 and U+2029 within this string will be replaced with their escaped forms.
<br>**Constraints:** Must be a str (object with a replace method that accepts two string arguments) |

### Returns

**Type:** `str`

A new string where occurrences of the Unicode characters U+2028 and U+2029 have been replaced by the literal sequences "\\u2028" and "\\u2029".


**Possible Values:**

- The original string unchanged if it contains neither U+2028 nor U+2029
- A string with one or both characters replaced by their respective escape sequences

### Complexity

O(n)

### Notes

- The function performs two replace operations in sequence; if performance is critical for very large strings, a single-pass implementation could be more efficient but is not used here.
- The function returns a new string and does not modify the input argument.

---



#### canonical_json

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def canonical_json(value: Any) -> str
```

### Description

Serialize a Python value to a deterministic JSON string suitable for hashing by calling json.dumps with specific options and then applying _canon_replace to the resulting string.


This function uses json.dumps with ensure_ascii=False, sort_keys=True, separators=(",", ":"), and allow_nan=False to produce a compact, key-sorted JSON representation. After serialization it returns the result of passing that JSON string to _canon_replace (presumably for additional escaping of characters like U+2028/U+2029).

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` | `Any` | ✅ | The Python value to serialize to JSON (e.g., dict, list, str, int, float, bool, None) .
<br>**Constraints:** Must be serializable by json.dumps using the stdlib JSON encoder, Must not contain NaN or Infinity when allow_nan=False (will cause an error) |

### Returns

**Type:** `str`

A deterministic JSON-encoded string produced by json.dumps with the specified options, then transformed by _canon_replace.


**Possible Values:**

- A compact JSON string with sorted object keys and no extraneous whitespace
- Any string returned by _canon_replace when applied to the json.dumps output

### Raises

| Exception | Condition |
| --- | --- |
| `TypeError` | Raised by json.dumps if value contains objects not serializable by the default JSON encoder. |
| `ValueError` | Raised by json.dumps if value contains NaN or Infinity and allow_nan=False. |

### Complexity

O(n) where n is the size of the serialized JSON output

### Related Functions

- `_canon_replace` - Called by canonical_json to perform additional string-level replacements/escaping after json.dumps

### Notes

- The function sets ensure_ascii=False so non-ASCII characters are preserved in the output; callers expecting ASCII-only should post-process accordingly.
- Determinism is achieved by sort_keys=True and compact separators; final output depends on the behavior of _canon_replace as well.
- Behavior for non-serializable types or NaN/Infinity follows the underlying json.dumps semantics.

---



#### digest

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def digest(value: Any) -> str
```

### Description

Returns a string consisting of the literal prefix 'sha256:' followed by the hex-encoded SHA-256 digest of the UTF-8 encoding of canonical_json(value).


Serializes the input with canonical_json(value) to obtain a deterministic JSON string, encodes that string as UTF-8, and computes its SHA-256 hash using hashlib.sha256. The function returns the hex digest prefixed with 'sha256:'. Determinism depends on canonical_json producing stable output.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `value` | `Any` | ✅ | The Python object to be serialized and hashed. It is passed to canonical_json to produce a deterministic JSON string representation.
<br>**Constraints:** Must be an input that canonical_json can accept and serialize deterministically, The result of canonical_json(value) must be encodable to UTF-8 |

### Returns

**Type:** `str`

A string of the form 'sha256:' + <hexadecimal SHA-256 digest> where the digest is computed over the UTF-8 bytes of canonical_json(value).


**Possible Values:**

- A string like 'sha256:3a7bd3e2360a...'(64 hex characters after the prefix) for valid inputs
- If canonical_json(value) returns an empty string, returns 'sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' (the SHA-256 of empty input) prefixed with 'sha256:'

### Complexity

O(n) where n is the size of the serialized canonical_json(value) (time to serialize and hash); memory proportional to serialized size

### Related Functions

- `canonical_json` - Called by digest to produce a deterministic JSON string representation of the input before hashing
- `hashlib.sha256` - Used by digest to compute the SHA-256 hash of the UTF-8 encoded canonical JSON

### Notes

- The function prepends the literal prefix 'sha256:' to the hex digest.
- Determinism of the output depends entirely on canonical_json producing a stable canonical serialization for equal inputs.
- No explicit error handling is present; any exceptions from canonical_json or string encoding will propagate to the caller.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, Any]:
```

### Description

Construct and return a dictionary representation of the instance by reading several attributes and conditionally including some fields.


The method builds a dict with keys 'from', 'to', 'kind', and 'shape' where the 'from' and 'to' values are produced by calling to_dict() on the corresponding attributes (self.from_ and self.to). It conditionally adds a 'guard' key when self.guard is not None and a 'capabilities' key when self.capabilities is truthy, converting capabilities to a list. Finally it returns the constructed dict.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `inferred instance` | ✅ | The instance whose attributes (from_, to, kind, shape, guard, capabilities) are read to produce the dictionary.
<br>**Constraints:** self.from_ must have a to_dict() method, self.to must have a to_dict() method, self.capabilities, if present, should be iterable to be converted to list |

### Returns

**Type:** `dict[str, Any]`

A dictionary with at least the keys 'from', 'to', 'kind', and 'shape'; optionally 'guard' and 'capabilities' depending on attribute values.


**Possible Values:**

- A dict containing 'from' (result of self.from_.to_dict()), 'to' (result of self.to.to_dict()), 'kind', and 'shape'.
- If self.guard is not None, the dict also includes 'guard' with the guard value.
- If self.capabilities is truthy, the dict also includes 'capabilities' as a list converted from self.capabilities.

### Complexity

O(1)

### Related Functions

- `from_.to_dict` - Called by this method to obtain the serialized representation of the 'from' attribute
- `to.to_dict` - Called by this method to obtain the serialized representation of the 'to' attribute

### Notes

- The method does not mutate the instance; it only reads attributes and constructs a new dict.
- Capabilities are explicitly converted to a list to ensure JSON-serializable sequence types if they were a set or other iterable.
- The method assumes self.from_ and self.to implement a to_dict() method; no checks are performed.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, Any]
```

### Description

Constructs and returns a dictionary representation of the instance by reading specific attributes and converting collections to lists and nested objects via their to_dict() methods.


This instance method builds and returns a dict with keys 'mas_id', 'outer_in_ports', 'outer_out_ports', 'links', and 'sub_bodies'. It converts the outer_in_ports and outer_out_ports attributes into lists, and maps each element of self.links and self.sub_bodies to its own to_dict() result to produce nested serializable structures.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `self` | ✅ | The instance whose attributes are being serialized into a dictionary.
<br>**Constraints:** Instance must have attributes: mas_id, outer_in_ports, outer_out_ports, links, sub_bodies, Elements in links and sub_bodies must implement a to_dict() method |

### Returns

**Type:** `dict[str, Any]`

A dictionary containing the instance's mas_id, lists for outer_in_ports and outer_out_ports, and lists of dictionaries for links and sub_bodies produced by calling to_dict() on each contained object.


**Possible Values:**

- A dict with keys: 'mas_id', 'outer_in_ports', 'outer_out_ports', 'links', 'sub_bodies'
- 'outer_in_ports' and 'outer_out_ports' are lists converted from the corresponding attributes
- 'links' and 'sub_bodies' are lists of dict objects produced by l.to_dict() and b.to_dict() respectively

### Raises

| Exception | Condition |
| --- | --- |
| `AttributeError` | If the instance does not have one of the expected attributes (mas_id, outer_in_ports, outer_out_ports, links, sub_bodies) accessed by the method |
| `Exception` | Any exception raised by calling l.to_dict() for elements of self.links or b.to_dict() for elements of self.sub_bodies will propagate |

### Complexity

O(n) where n is len(self.links) + len(self.sub_bodies); converting the outer port collections to lists is O(m) where m is number of ports

### Related Functions

- `to_dict (on link objects)` - This method calls l.to_dict() for each element in self.links to produce the 'links' list
- `to_dict (on sub-body objects)` - This method calls b.to_dict() for each element in self.sub_bodies to produce the 'sub_bodies' list

### Notes

- The method does not mutate the instance; it constructs new lists and a new dict.
- Any exceptions from nested to_dict() calls are not caught here and will propagate to the caller.
- The exact types of elements in outer_in_ports and outer_out_ports are not transformed other than being converted to lists.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, Any]
```

### Description

Return a dictionary representation containing the object's schema_version, source_digest, and the root converted to a dictionary.


This method builds and returns a new dict with three keys: 'schema_version' and 'source_digest' taken directly from the instance attributes, and 'root' produced by calling self.root.to_dict(). The implementation performs no validation or mutation; it constructs and returns the mapping directly.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `implicit instance parameter` | ✅ | The instance whose attributes (schema_version, source_digest, root) are used to build the returned dictionary.
<br>**Constraints:** self must have attributes 'schema_version', 'source_digest', and 'root', self.root must provide a to_dict() method |

### Returns

**Type:** `dict[str, Any]`

A dictionary with keys 'schema_version', 'source_digest', and 'root'. The 'root' value is the result of calling self.root.to_dict().


**Possible Values:**

- A mapping like {'schema_version': <value>, 'source_digest': <value>, 'root': <dict>}
- If attributes exist but contain None, those None values will appear in the returned dict

### Complexity

O(1)

### Related Functions

- `root.to_dict` - called by this method to obtain the dictionary representation of the root attribute

### Notes

- This method assumes self.root implements a to_dict() method and does not guard against AttributeError if not present.
- No deep-copying is performed; the returned dict references values returned by self.root.to_dict().

---



#### _node_index

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _node_index(body: MasBody) -> dict[str, Node]
```

### Description

Constructs and returns a dictionary mapping each node's id to the node object from the provided MasBody instance.


The function iterates over body.nodes and builds a dictionary comprehension where each key is n.id and each value is the node object n. It relies solely on the iterable body.nodes and the presence of an id attribute on each node; there is no additional processing or mutation.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `MasBody` | ✅ | The MasBody instance whose .nodes iterable will be used to build the index.
<br>**Constraints:** body must have an attribute `nodes` that is iterable, Each element in body.nodes must have an attribute `id` usable as a dictionary key (hashable) |

### Returns

**Type:** `dict[str, Node]`

A dictionary mapping node id (n.id) to the node object n for every node in body.nodes.


**Possible Values:**

- An empty dict if body.nodes is empty
- A dict with one entry per node in body.nodes; later nodes with duplicate ids will overwrite earlier ones

### Complexity

O(n)

### Notes

- If multiple nodes share the same id, the last one encountered in body.nodes will be stored in the resulting dictionary, overriding previous entries.
- If body lacks a .nodes attribute or nodes contain items without an id attribute, the function will raise the corresponding AttributeError at runtime (not explicitly handled).

---



#### _check_no_unguarded_cycle

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _check_no_unguarded_cycle(body: MasBody, where: str) -> None
```

### Description

Check that the directed graph in body.links has no directed cycle composed entirely of nodes that are not 'self_recurse'; raise RecursiveMasError if found.


Build an adjacency map from body.nodes and body.links while excluding links touching OUTER, touching any 'self_recurse' node, or referencing missing nodes. Perform DFS with coloring (0=unseen, 1=on stack, 2=done) to detect back-edges; on detection raise RecursiveMasError with a path including the provided where string.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `MasBody` | ✅ | An object containing nodes and links describing the graph. Expects body.nodes iterable of nodes with id and kind, and body.links iterable of links with from_.node and to.node.
<br>**Constraints:** body.nodes must be iterable and each node must have an 'id' attribute and a 'kind' attribute, body.links must be iterable and each link must have 'from_.node' and 'to.node' attributes, Nodes referenced by links should be present in the index returned by _node_index(body) to be considered when building adjacency |
| `where` | `str` | ✅ | A string used to construct the error path included in the raised RecursiveMasError when an unguarded cycle is detected.
<br>**Constraints:** Should be a human-readable path or identifier used for error reporting |

### Returns

**Type:** `None`

This function does not return a value; it completes silently if no unguarded cycle is found.


**Possible Values:**

- None (normal completion)
- Raises RecursiveMasError on detection of an unguarded cycle

### Raises

| Exception | Condition |
| --- | --- |
| `RecursiveMasError` | Raised when a directed back-edge (cycle) is found during DFS among nodes that are not 'self_recurse' and that do not involve the OUTER sentinel, with message indicating the where path and the edge u->v |

### Complexity

O(N + E) where N is the number of nodes and E is the number of considered links (edges)

### Related Functions

- `_node_index` - Called by this function to produce a mapping of node ids to node objects used when building the adjacency map

### Notes

- Links are ignored when either endpoint equals OUTER, when either endpoint is a 'self_recurse' node, or when endpoints are not present in the node index; only the remaining links participate in cycle detection.
- Cycle detection uses standard DFS coloring: encountering a node with color 1 signals a back-edge and triggers the error.
- The error path message includes the provided 'where' string followed by '/cycle/{u}->{v}' to indicate the offending edge.

---



#### dfs

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def dfs(u: str) -> None
```

### Description

Performs a depth-first traversal from node u, marking visitation state and detecting back-edges that indicate unguarded cycles.


Marks node u as 'visiting' (color 1), iterates its adjacency list via an external adj mapping, and recurses into unvisited neighbors. If a neighbor is already 'visiting' (color 1) a RecursiveMasError is raised to signal a cycle; after processing neighbors u is marked 'visited' (color 2).

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `u` | `str` | ✅ | The starting node identifier for this DFS step; used as a key into external color and adj mappings.
<br>**Constraints:** Must be a hashable key (annotated as str), Expected to be present or valid as a key in the external data structures used by the traversal |

### Returns

**Type:** `None`

Does not return a value; completes after marking visitation state and recursing as needed. Implicitly returns None.


**Possible Values:**

- None

### Raises

| Exception | Condition |
| --- | --- |
| `RecursiveMasError` | Raised when an edge u->v is found where v is currently in visiting state (color == 1), indicating a cycle without a self_recurse boundary. The exception includes an error code, a path using the external 'where' variable, and a message. |

### Side Effects

> ❗ **IMPORTANT**
> This function has side effects that modify state or perform I/O operations.

- Mutates the external mapping 'color' by setting color[u] = 1 at start and color[u] = 2 on completion
- Recursively calls dfs, causing further mutations to 'color' for other nodes

### Complexity

O(V + E) in the size of the reachable subgraph (visits each node and edge at most once)

### Related Functions

- `RecursiveMasError` - Exception class raised by this function when an unguarded cycle (back-edge) is detected

### Notes

- This function depends on external mutable variables: color (dict-like), adj (dict-like), and where (string) for error path construction.
- There is no explicit base-case return; unvisited neighbors are recursed into and nodes are marked visited after processing neighbors.
- The function assumes color.get(..., 0) semantics where 0 means unvisited, 1 means visiting (on recursion stack), and 2 means visited.

---



#### _outer_surface

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _outer_surface(body: MasBody, enclosing: Optional[Node]) -> tuple[tuple[str, ...], tuple[str, ...]]
```

### Description

Return two sorted tuples of unique port-name strings representing outer-facing 'in' and 'out' ports for a body, using an enclosing node's ports if provided.


If enclosing is provided, the function returns sorted tuples taken directly from enclosing.ports.in_ and enclosing.ports.out. If enclosing is None, it scans body.links and collects port names where link.from_.node == OUTER into the in set and where link.to.node == OUTER into the out set. Duplicates are removed with sets and results are returned as deterministic tuple(sorted(...)).

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | `MasBody` | ✅ | The MAS body whose links are inspected when enclosing is None; expected to have an iterable 'links' attribute where each link has 'from_.node', 'from_.port', 'to.node', and 'to.port'.
<br>**Constraints:** Must provide an object with a 'links' iterable when enclosing is None, Links' endpoints must expose 'node' and 'port' attributes |
| `enclosing` | `Optional[Node]` | ✅ | An optional enclosing Node; when provided, its ports.in_ and ports.out are used directly instead of inspecting body.links.
<br>**Constraints:** May be None; if not None, must have 'ports.in_' and 'ports.out' iterables, Ports iterables should contain strings (port names) for correct sorting and return types |

### Returns

**Type:** `tuple[tuple[str, ...], tuple[str, ...]]`

A pair of tuples: (in_ports, out_ports). Each tuple contains sorted unique port name strings. When enclosing is provided, those ports come from enclosing.ports.in_ and enclosing.ports.out; otherwise they are derived from links connected to the OUTER sentinel.


**Possible Values:**

- ({sorted tuple of enclosing.ports.in_}, {sorted tuple of enclosing.ports.out}) when enclosing is not None
- ({sorted tuple of port names where link.from_.node == OUTER}, {sorted tuple of port names where link.to.node == OUTER}) when enclosing is None
- ((), ()) when no matching ports are found

### Complexity

O(n) where n is the number of links in body.links (iteration and set insertions dominate); O(1) if enclosing is provided.

### Notes

- The function refers to a sentinel named OUTER; behavior depends on that constant's identity.
- Duplicates are removed by using sets before sorting, so returned tuples contain unique port names.
- If enclosing is provided, the function does not inspect body.links at all.

---



#### resolve_inner_links

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def resolve_inner_links(mas: Mas) -> ResolvedInnerLinks
```

### Description

Compute a digest of the MAS source dictionary, resolve the root body using _resolve_body, and return a ResolvedInnerLinks record containing the schema version, source digest, and resolved root.


This function calls mas.to_dict() and passes that dictionary to digest(...) to produce a source digest. It then calls _resolve_body on mas.root with enclosing_sub_mas_node=None and where="" to obtain a normalized/validated root structure. Finally it constructs and returns a ResolvedInnerLinks instance populated with SCHEMA_VERSION_RESOLVED, the computed digest, and the resolved root.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `mas` | `Mas` | ✅ | The MAS object whose inner links should be resolved; used to produce a source dictionary and to obtain its root node.
<br>**Constraints:** Must provide a to_dict() method that returns a serializable mapping, Must have an attribute 'root' expected by _resolve_body |

### Returns

**Type:** `ResolvedInnerLinks`

A ResolvedInnerLinks dataclass/record containing schema_version, source_digest (digest of mas.to_dict()), and root (result of _resolve_body).


**Possible Values:**

- A ResolvedInnerLinks instance with schema_version=SCHEMA_VERSION_RESOLVED, source_digest set to digest(mas.to_dict()), and root set to the value returned from _resolve_body

### Complexity

O(n) — dominated by mas.to_dict() and the traversal performed by _resolve_body

### Related Functions

- `digest` - Called by resolve_inner_links to compute a source digest from mas.to_dict()
- `_resolve_body` - Called by resolve_inner_links to resolve and normalize the MAS root node

### Notes

- The function itself performs no visible I/O or mutations; it delegates work to mas.to_dict(), digest, and _resolve_body.
- Any exceptions raised would originate from mas.to_dict(), digest, or _resolve_body; this function contains no explicit error handling.
- SCHEMA_VERSION_RESOLVED and ResolvedInnerLinks must be defined in the same module or imported for this function to succeed.

---



#### load_mas

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def load_mas(spec: Mapping[str, Any]) -> Mas
```

### Description

Call Mas.from_dict with the provided spec mapping and return its result.


This function is a thin wrapper that forwards the spec argument to the Mas.from_dict classmethod and returns whatever that call returns. There is no additional processing, validation, or transformation performed in this function; it immediately returns the result of Mas.from_dict(spec).

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spec` | `Mapping[str, Any]` | ✅ | A mapping (dictionary-like) containing the raw MAS specification to be converted into a Mas instance.
<br>**Constraints:** Must be a Mapping with string keys and arbitrary values as expected by Mas.from_dict, This function does not validate the contents; Mas.from_dict is responsible for any validation |

### Returns

**Type:** `Mas`

The Mas instance produced by Mas.from_dict when called with spec.


**Possible Values:**

- An instance of Mas constructed from the provided spec
- If Mas.from_dict raises an exception, this function will not return (the exception propagates)

### Complexity

O(1)

### Related Functions

- `Mas.from_dict` - The function directly calls this classmethod to produce and return the Mas instance

### Notes

- This function performs no validation itself; any parsing, validation, or errors originate from Mas.from_dict.
- Because it simply forwards to Mas.from_dict, any exceptions or side effects performed by that method will be observable when calling load_mas.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, Any]
```

### Description

Constructs and returns a dictionary representation of the instance containing its id, kind, ports, and optional capabilities and annotations.


Creates a dict with keys 'id', 'kind', and 'ports' (using self.ports.to_dict()). If self.capabilities is truthy it adds a 'capabilities' list. If self.annotations is truthy it adds an 'annotations' dict built from its (key, value) pairs. Returns the assembled dict.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `instance of the class containing this method` | ✅ | Reference to the instance whose state is being converted to a dict. The method reads self.id, self.kind, self.ports, self.capabilities, and self.annotations.
<br>**Constraints:** self.ports must have a to_dict() method, self.annotations, if truthy, must be iterable of (key, value) pairs, self.capabilities, if truthy, must be iterable (will be converted to list) |

### Returns

**Type:** `dict[str, Any]`

A dictionary containing at minimum the keys 'id', 'kind', and 'ports'. Conditionally includes 'capabilities' (as a list) and 'annotations' (as a dict) if those attributes are present/truthy on the instance.


**Possible Values:**

- {'id': ..., 'kind': ..., 'ports': ...}
- {'id': ..., 'kind': ..., 'ports': ..., 'capabilities': [...]}
- {'id': ..., 'kind': ..., 'ports': ..., 'annotations': {...}}
- {'id': ..., 'kind': ..., 'ports': ..., 'capabilities': [...], 'annotations': {...}}

### Complexity

O(n) where n is the combined size of self.capabilities and self.annotations (calling self.ports.to_dict() may add its own cost)

### Related Functions

- `ports.to_dict` - Called by this method to obtain a serializable representation of the ports attribute

### Notes

- The method does not modify any attributes on self; it only reads them and constructs a new dict.
- self.annotations is converted using a dict comprehension over its items; it must therefore be iterable yielding (key, value) pairs.
- self.capabilities is converted to a list only when truthy; falsy values (e.g., empty set) will not produce the 'capabilities' key.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, Any]
```

### Description

Serialize selected attributes of the instance into a dictionary, calling to_dict() on the 'from_' and 'to' attributes and conditionally including 'guard' and 'capabilities'.


The method builds and returns a dictionary with keys 'from', 'to', 'kind', and 'stitch' populated from the instance. It calls to_dict() on the instance attributes self.from_ and self.to; if self.guard is not None it adds a 'guard' key; if self.capabilities is truthy it adds a 'capabilities' key with a list conversion of that attribute.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `implicit instance reference` | ✅ | Reference to the instance whose attributes are being serialized. The implementation expects the instance to have attributes: from_ (with a to_dict method), to (with a to_dict method), kind, stitch, guard, and capabilities.
<br>**Constraints:** self.from_ must have a to_dict() method that returns a serializable value, self.to must have a to_dict() method that returns a serializable value, self.capabilities, if present and truthy, must be iterable (will be converted with list()), No attribute validation is performed here; missing attributes will raise AttributeError externally |

### Returns

**Type:** `dict[str, Any]`

A dictionary representing the instance with keys: 'from' (result of self.from_.to_dict()), 'to' (result of self.to.to_dict()), 'kind', 'stitch', and optionally 'guard' and 'capabilities'.


**Possible Values:**

- A dict containing at minimum the keys 'from', 'to', 'kind', and 'stitch' if those attributes exist
- If self.guard is not None, the dict includes a 'guard' key with the guard value
- If self.capabilities is truthy, the dict includes a 'capabilities' key containing a list(self.capabilities)

### Complexity

O(1)

### Notes

- The method invokes to_dict() on self.from_ and self.to; any exceptions from those calls propagate out.
- Capabilities are explicitly converted to a list to ensure a concrete sequence is serialized.
- No defensive copying is performed for values other than capabilities; returned dict references the values produced by attribute accesses and nested to_dict() calls.

---



#### sort_key

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def sort_key(self) -> tuple[str, ...]
```

### Description

Return a tuple of string values derived from the instance's from_, to, kind, stitch, and guard attributes for use as a sort or comparison key.


The method constructs and returns a fixed-order tuple containing: self.from_.node, self.from_.port, self.to.node, self.to.port, self.kind, self.stitch, and self.guard (or an empty string when guard is falsy). It performs no validation or mutation; it simply accesses attributes and returns a tuple of strings (guard coerced to an empty string when falsy).

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `implicit instance parameter` | ✅ | The instance whose attributes (from_, to, kind, stitch, guard) are read to build the sort key tuple.
<br>**Constraints:** self must have attributes: from_ and to, each with .node and .port attributes, self must have attributes: kind and stitch (expected to be str or convertible to str), self.guard may be falsy; when falsy the method will use an empty string |

### Returns

**Type:** `tuple[str, ...]`

A tuple of strings representing a deterministic sort key: (from_.node, from_.port, to.node, to.port, kind, stitch, guard_or_empty_string).


**Possible Values:**

- Tuples where each element is the string value of the corresponding attribute
- The final element is '' when self.guard is falsy (None, empty string, etc.)

### Complexity

O(1)

### Notes

- No type coercion beyond the guard fallback; if non-string attribute values exist they will be returned as-is and may cause sorting inconsistencies.
- The method relies on attribute access; AttributeError will occur if expected attributes are missing (not explicitly handled).
- The guard field is normalized to an empty string when falsy to ensure tuple length and element types are consistent.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, Any]
```

### Description

Return a dictionary representation of the instance containing frame_id, mas_id, depth, a sorted list of node dictionaries, and termination.


This method builds and returns a dict literal with five keys: 'frame_id', 'mas_id', 'depth', 'nodes', and 'termination'. The 'nodes' value is produced by sorting self.nodes by each node's id attribute and calling to_dict() on each node to produce a list of node dictionaries. Other fields are copied directly from the instance attributes.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `instance` | ✅ | The instance whose attributes are being serialized to a dictionary.
<br>**Constraints:** self must have attributes: frame_id, mas_id, depth, nodes, and termination, Each element in self.nodes must have an 'id' attribute and a 'to_dict()' method |

### Returns

**Type:** `dict[str, Any]`

A dictionary mapping the instance's frame_id, mas_id, depth, termination, and a list of node dictionaries (sorted by node.id).


**Possible Values:**

- A dict with keys: 'frame_id', 'mas_id', 'depth', 'nodes', 'termination'.
- The 'nodes' key contains a list of dicts returned by each node's to_dict() in ascending order of node.id.

### Complexity

O(n log n) — dominated by sorting the nodes list by node.id (n = number of nodes).

### Related Functions

- `Node.to_dict` - Called by this method to serialize each node in self.nodes into a dictionary.
- `sorted` - Built-in function used here to order nodes by their id before serialization.

### Notes

- The method assumes each node in self.nodes has an 'id' attribute and a 'to_dict()' method; otherwise an AttributeError will occur at runtime.
- The order of nodes in the returned 'nodes' list is deterministic and sorted ascending by node.id.
- Other attributes (frame_id, mas_id, depth, termination) are included as-is without transformation.

---



#### to_dict

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def to_dict(self) -> dict[str, Any]
```

### Description

Return a dictionary representation of the instance, composing several instance attributes into a serializable mapping.


Builds and returns a serializable dict from the instance attributes. It unpacks limits into max_depth and fuel, converts frames and links by calling their to_dict() methods, and produces deterministic ordering by sorting frames (by mas_id, depth), links (by sort_key()), and evidence (by frame_id, kind).

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `self` | `instance of the containing class (no explicit type annotation in signature)` | ✅ | The instance whose attributes are read to build the dictionary representation.
<br>**Constraints:** self must have attributes: schema_version, source_digest, limits (indexable with at least two elements), frames (iterable of objects with mas_id, depth and a to_dict() method), links (iterable of objects with sort_key() and a to_dict() method), and evidence (iterable of dict-like objects with keys 'frame_id' and 'kind'). |

### Returns

**Type:** `dict[str, Any]`

A dictionary with the following keys: schema_version (from self.schema_version), source_digest (from self.source_digest), limits (a dict with keys max_depth and fuel taken from self.limits[0] and self.limits[1]), frames (a list of frame dicts), links (a list of link dicts), and evidence (a sorted list of evidence entries).


**Possible Values:**

- A dict with keys: 'schema_version', 'source_digest', 'limits', 'frames', 'links', 'evidence'.
- frames is a list produced by [f.to_dict() ...] sorted by (f.mas_id, f.depth).
- links is a list produced by [l.to_dict() ...] sorted by l.sort_key().
- evidence is a list of the original evidence entries sorted by (frame_id, kind).

### Complexity

O(n log n) for sorting the frames/links/evidence (where n is the size of each respective collection); overall linearithmic in the largest collection.

### Notes

- The method assumes self.limits is indexable and contains at least two elements (limits[0] and limits[1]).
- Frames and links are converted by calling their to_dict() methods; those methods must exist and return serializable objects.
- Evidence entries are expected to be dict-like objects with keys 'frame_id' and 'kind' for sorting.

---



#### _frame_id

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _frame_id(mas_id: str, depth: int) -> str
```

### Description

Return a string that concatenates the mas_id and depth separated by a '#' character.


This function constructs and returns a formatted identifier by interpolating the provided mas_id and depth into an f-string with a '#' separator. The implementation is a single expression that returns f"{mas_id}#{depth}" without performing any validation or side effects.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `mas_id` | `str` | ✅ | The base identifier part to appear before the '#' separator in the resulting string.
<br>**Constraints:** Expected to be a string (annotation only; not enforced at runtime). |
| `depth` | `int` | ✅ | The numeric depth to appear after the '#' separator in the resulting string.
<br>**Constraints:** Expected to be an integer (annotation only; not enforced at runtime). |

### Returns

**Type:** `str`

A string formed by concatenating mas_id, the character '#', and the string representation of depth.


**Possible Values:**

- If mas_id='agent' and depth=2 -> 'agent#2'
- If mas_id='' and depth=0 -> '#0'

### Complexity

O(1)

### Notes

- The function performs no validation: it relies on the caller to provide appropriate types.
- Because it uses an f-string, non-string arguments will be converted to their string representation at runtime.

---



#### _qual

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _qual(mas_id: str, depth: int, node_id: str) -> str
```

### Description

Returns a qualified identifier string by concatenating the result of _frame_id(mas_id, depth), a literal '::' separator, and the node_id.


This function constructs and returns a single string using an f-string: it calls _frame_id with mas_id and depth and appends '::' plus the node_id. The implementation performs no validation, mutation, I/O, or other side effects; it simply composes and returns the formatted string.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `mas_id` | `str` | ✅ | An identifier passed through to _frame_id to form the left portion of the qualified string.
<br>**Constraints:** Must be a value acceptable to _frame_id when combined with depth |
| `depth` | `int` | ✅ | An integer depth value passed through to _frame_id to form the left portion of the qualified string.
<br>**Constraints:** Must be a value acceptable to _frame_id when combined with mas_id |
| `node_id` | `str` | ✅ | The node identifier used as the right portion of the qualified string after the '::' separator.
<br>**Constraints:** Should be a string; no internal validation is performed |

### Returns

**Type:** `str`

A string composed of the value returned by _frame_id(mas_id, depth), followed by '::', followed by node_id.


**Possible Values:**

- Any string produced by f"{_frame_id(mas_id, depth)}::{node_id}", e.g. '<frame_id>::<node_id>'

### Complexity

O(1)

### Related Functions

- `_frame_id` - Called by _qual to produce the left-hand portion of the qualified identifier

### Notes

- The function relies on _frame_id but does not inspect or validate its return value; any exceptions from _frame_id will propagate.
- No trimming or escaping of node_id is performed; callers must ensure node_id does not contain the literal separator if that is undesirable.

---



#### _outer_in_id

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _outer_in_id(mas_id: str, depth: int) -> str
```

### Description

Returns the result of calling _qual with the provided mas_id, depth, and the literal string "__outer_in__".


This function is a thin wrapper that delegates its work to another function named _qual. It simply forwards the mas_id and depth arguments along with the fixed tag "__outer_in__" to _qual and returns whatever string _qual produces.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `mas_id` | `str` | ✅ | An identifier value that is forwarded to the _qual function.
<br>**Constraints:** No validation performed in this function; expected to be a str as annotated |
| `depth` | `int` | ✅ | A depth value that is forwarded to the _qual function.
<br>**Constraints:** No validation performed in this function; expected to be an int as annotated |

### Returns

**Type:** `str`

The string value returned by calling _qual(mas_id, depth, "__outer_in__").


**Possible Values:**

- Any string value that _qual returns when invoked with (mas_id, depth, "__outer_in__")

### Complexity

O(1)

### Related Functions

- `_qual` - Called by; this function forwards its arguments and a fixed tag to _qual and returns its result.

### Notes

- This function performs no validation and does not modify state; it is purely a passthrough to _qual with a fixed third argument "__outer_in__".
- Behavior and possible returned string values depend entirely on the implementation of _qual, which is not shown here.

---



#### _outer_out_id

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _outer_out_id(mas_id: str, depth: int) -> str
```

### Description

Returns the result of calling the helper function _qual with mas_id, depth, and the literal string "__outer_out__".


This function is a simple wrapper that delegates to another function named _qual. It forwards the two provided arguments (mas_id and depth) and a fixed third argument "__outer_out__" to _qual and returns whatever _qual returns.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `mas_id` | `str` | ✅ | First argument forwarded to _qual; likely an identifier string.
 |
| `depth` | `int` | ✅ | Second argument forwarded to _qual; likely a numeric depth value.
 |

### Returns

**Type:** `str`

The string returned by calling _qual(mas_id, depth, "__outer_out__").


**Possible Values:**

- Any string value that _qual produces when called with the provided mas_id, depth, and the literal "__outer_out__"

### Complexity

O(1)

### Related Functions

- `_qual` - Called by this function; this wrapper forwards arguments to _qual with a fixed third parameter

### Notes

- This function performs no validation or mutation; it simply delegates to _qual with a constant third argument "__outer_out__".
- Any behavior, exceptions, or side effects depend entirely on the implementation of _qual.

---



#### _cap_id

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _cap_id(mas_id: str, depth: int) -> str
```

### Description

Returns the result of calling the helper function _qual with the provided mas_id and depth and the literal string "__cap__" as the third argument.


This function is a thin wrapper that forwards its two parameters and a fixed third parameter "__cap__" to another function named _qual and immediately returns that result. There is no additional processing, validation, or branching in this implementation; its sole action is the call and return.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `mas_id` | `str` | ✅ | An identifier string that is passed through to _qual.
 |
| `depth` | `int` | ✅ | An integer depth value that is passed through to _qual.
 |

### Returns

**Type:** `str`

The string value returned by calling _qual(mas_id, depth, "__cap__").


**Possible Values:**

- Any string value that _qual returns when invoked with (mas_id, depth, "__cap__")

### Complexity

O(1)

### Related Functions

- `_qual` - Calls _qual with (mas_id, depth, "__cap__") and returns its result

### Notes

- This implementation shows no validation or error handling; any exceptions would come from the called function _qual.
- The function is a simple forwarding wrapper that hardcodes the third argument to "__cap__".

---



#### _virtual_outer

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _virtual_outer(mas_id: str, depth: int, in_ports: Sequence[str], out_ports: Sequence[str]) -> tuple[UnrolledNode, UnrolledNode]
```

### Description

Constructs two UnrolledNode instances representing a virtual outer input and a virtual outer output using provided identifiers and port lists.


Creates two UnrolledNode objects: an outer input ('oi') and an outer output ('oo'). It computes node ids via helper functions _outer_in_id and _outer_out_id, wraps the provided port sequences into Ports (converted to tuples), annotates each node with a ('virtual', ...) tag, and returns the pair (oi, oo).

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `mas_id` | `str` | ✅ | Identifier used to build the node ids via _outer_in_id and _outer_out_id.
<br>**Constraints:** Must be a string, Used as-is by _outer_in_id/_outer_out_id (no validation in this function) |
| `depth` | `int` | ✅ | Depth value used to build the node ids via _outer_in_id and _outer_out_id.
<br>**Constraints:** Must be an integer, Used as-is by _outer_in_id/_outer_out_id (no validation in this function) |
| `in_ports` | `Sequence[str]` | ✅ | Sequence of port names to use for the input-side Ports of the outer input node (also reused as output ports for that node in this implementation).
<br>**Constraints:** Each element should be a string, Will be converted to a tuple when constructing Ports |
| `out_ports` | `Sequence[str]` | ✅ | Sequence of port names to use for the input and output Ports of the outer output node.
<br>**Constraints:** Each element should be a string, Will be converted to a tuple when constructing Ports |

### Returns

**Type:** `tuple[UnrolledNode, UnrolledNode]`

A tuple (oi, oo) where oi is the constructed outer-in UnrolledNode and oo is the constructed outer-out UnrolledNode.


**Possible Values:**

- A tuple containing two UnrolledNode instances initialized as shown in the implementation

### Complexity

O(1)

### Related Functions

- `_outer_in_id` - Called to generate the id for the outer-in UnrolledNode
- `_outer_out_id` - Called to generate the id for the outer-out UnrolledNode

### Notes

- The function converts the provided in_ports and out_ports to tuples before passing them to Ports.
- The in_ports sequence is used for both the in_ and out fields of the outer-in node in this implementation.
- No validation is performed on mas_id, depth, or the port sequences; any required validation must be handled by callers or the helper functions.

---



#### example_mas_spec

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def example_mas_spec() -> dict[str, Any]
```

### Description

Returns a canonical nested dictionary describing a recursive multi-agent system (MAS) specification used to populate build artifacts.


Constructs and returns a literal Python dictionary encoding a full example MAS specification. The returned structure includes top-level fields such as schema_version, mas_id, limits, nodes, links, and a sub_mas list containing a nested MAS. The function performs no I/O or validation and simply returns the hard-coded example structure.

### Returns

**Type:** `dict[str, Any]`

A dictionary representing a canonical example MAS specification. The dictionary includes keys: schema_version, mas_id, limits, nodes, links, and sub_mas with nested node and link definitions.


**Possible Values:**

- A dictionary with the exact structure shown in the function: schema_version set to SCHEMA_VERSION_INPUT and other fields populated as the canonical example.
- Always returns the same literal example structure (no variants at runtime).

### Complexity

O(1)

### Notes

- The function references SCHEMA_VERSION_INPUT; that constant must be defined in the module for the returned dictionary to include the intended schema_version value.
- This is a pure factory that returns a literal example; it performs no validation on the structure it returns.
- Because the function returns a nested mutable dictionary, callers that mutate the returned value will change their local copy; the function does not protect against caller-side mutation.

---



#### emit_build_artifacts

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def emit_build_artifacts(out_dir: Path) -> dict[str, Any]
```

### Description

Create canonical build artifact files in the specified output directory and return a manifest describing those artifacts.


Creates the output directory if needed, builds an example MAS spec, resolves inner links, and unrolls loops to produce three canonical JSON artifact bodies. Writes each artifact and a manifest.json with metadata (paths, sha256, sizes, generation time, source digest, and limits) and returns the manifest dict.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `out_dir` | `Path` | ✅ | Filesystem directory path where the artifact files and manifest.json will be written.
<br>**Constraints:** Must be a writable path on the host filesystem, If non-existent, the function will create it (parents=True) |

### Returns

**Type:** `dict[str, Any]`

A manifest dictionary describing the generated artifacts, generation time, schema version, source digest, and limits.


**Possible Values:**

- A dict containing keys: 'schema_version', 'generated_at', 'source_digest', 'limits', and 'artifacts' describing the produced files

### Raises

| Exception | Condition |
| --- | --- |
| `OSError` | If directory creation or file writes fail due to filesystem errors or permission issues (raised by Path.mkdir or Path.write_bytes). |
| `Exception` | Any exception propagated from helper functions (e.g., example_mas_spec, load_mas, resolve_inner_links, unroll, canonical_json, digest) will propagate out of emit_build_artifacts. |

### Side Effects

> ❗ **IMPORTANT**
> This function has side effects that modify state or perform I/O operations.

- Creates the output directory on the filesystem (out_dir.mkdir with parents=True)
- Writes multiple files to disk under out_dir: 'example.mas.json', 'inner-links.example.json', 'loop-unrolling.example.json', and 'manifest.json'
- Computes SHA-256 digests of the written artifact bytes (via hashlib.sha256)

### Usage Examples

#### Generate canonical build artifacts into a target directory

```python
manifest = emit_build_artifacts(Path('/tmp/mas_artifacts'))
```

Creates the directory /tmp/mas_artifacts if needed, writes three example JSON artifacts and manifest.json, and returns the manifest dict describing them.

### Complexity

O(total_size_of_artifacts) - time and space scale roughly with the total size of the serialized artifact JSON bodies

### Related Functions

- `example_mas_spec` - Called by emit_build_artifacts to obtain the initial MAS specification dictionary
- `unroll` - Called by emit_build_artifacts to produce the unrolled DAG (used to extract limits and a serialized artifact)

### Notes

- The function relies on several helpers (example_mas_spec, load_mas, resolve_inner_links, unroll, canonical_json, digest) and constants (SCHEMA_VERSION_MANIFEST, _dt) defined elsewhere in the module.
- Timestamps in the manifest use UTC and are formatted as YYYY-MM-DDTHH:MM:SSZ.
- The manifest includes limits taken from dag.limits[0] and dag.limits[1]; callers should ensure the unroll call produces a dag with a 'limits' attribute of at least length 2.

---



#### _load_json

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _load_json(path: Path) -> Any
```

### Description

Read the text contents of the given Path using UTF-8 and parse it with json.loads, returning the resulting Python object.


The function calls path.read_text(encoding="utf-8") to obtain the file contents as a string, then passes that string to json.loads to parse JSON and return the parsed Python value. It performs no additional validation or transformation and allows any exceptions raised by read_text or json.loads to propagate to the caller.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `path` | `Path` | ✅ | A pathlib.Path (or compatible object) pointing to a file whose contents are JSON text.
<br>**Constraints:** Must be a path that path.read_text(encoding='utf-8') can read, Contents must be valid JSON parsable by json.loads |

### Returns

**Type:** `Any`

The Python object produced by json.loads from the file's UTF-8 text (e.g., dict, list, str, int, float, bool, or None).


**Possible Values:**

- dict (JSON object)
- list (JSON array)
- str (JSON string)
- int or float (JSON number)
- bool (true/false)
- None (null)

### Raises

| Exception | Condition |
| --- | --- |
| `FileNotFoundError` | If the path does not exist when path.read_text is called. |
| `PermissionError` | If the file cannot be read due to filesystem permissions. |
| `UnicodeDecodeError` | If the file contents cannot be decoded as UTF-8. |
| `json.JSONDecodeError` | If the file contents are not valid JSON according to json.loads. |

### Side Effects

> ❗ **IMPORTANT**
> This function has side effects that modify state or perform I/O operations.

- Performs file I/O: reads file contents from the filesystem using Path.read_text

### Complexity

O(n) where n is the number of bytes in the file (time proportional to reading and parsing the file)

### Related Functions

- `json.loads` - Called by this function to parse the JSON text
- `Path.read_text` - Called by this function to read the file contents using UTF-8 encoding

### Notes

- The function uses UTF-8 decoding explicitly; files with a different encoding may raise UnicodeDecodeError.
- No error handling is performed; callers should handle or allow propagation of IO and JSON parsing exceptions.
- The function does not open the file using an explicit file object; it relies on Path.read_text which handles opening and closing.

---



#### _cmd_validate

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _cmd_validate(args: argparse.Namespace) -> int
```

### Description

Loads a specification from args.input, resolves inner links in the loaded MAS, writes the canonical JSON representation of the resolved MAS to standard output, and returns 0.


The function constructs a Path from args.input and passes it to _load_json to obtain a spec object. It then creates a MAS object via load_mas(spec), resolves inner links using resolve_inner_links(mas), converts the resolved object to a dictionary, serializes it using canonical_json, writes the resulting JSON string plus a newline to stdout, and finally returns integer 0.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `args` | `argparse.Namespace` | ✅ | An argparse Namespace expected to contain an attribute 'input' referencing the input source (used to create a Path).
<br>**Constraints:** Must have attribute 'input' that is a valid value for pathlib.Path() (e.g., a path-like string or Path object). |

### Returns

**Type:** `int`

Always returns the integer 0 to indicate successful completion.


**Possible Values:**

- 0

### Side Effects

> ❗ **IMPORTANT**
> This function has side effects that modify state or perform I/O operations.

- Writes the canonical JSON representation of the resolved MAS followed by a newline to standard output via sys.stdout.write

### Complexity

O(1)

### Related Functions

- `load_mas` - Called by _cmd_validate to construct a MAS object from the loaded specification
- `resolve_inner_links` - Called by _cmd_validate to resolve inner links in the MAS before serialization

### Notes

- The function calls helper functions (_load_json, load_mas, resolve_inner_links, canonical_json) whose behaviors (including I/O and exceptions) are not shown here; any exceptions raised by those functions will propagate unless handled by callers.
- This function itself does not catch exceptions and relies on the called functions to perform their own validation and error handling.

---



#### _cmd_unroll

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _cmd_unroll(args: argparse.Namespace) -> int
```

### Description

Loads a MAS specification from a JSON input, unrolls it into a DAG, writes the canonical JSON representation of the DAG to standard output, and returns 0.


Reads a JSON spec via _load_json(Path(args.input)), constructs a MAS with load_mas(spec), and calls unroll(...) using args.max_depth, args.fuel, and detect_fixed_point = not args.no_fixed_point. It serializes the resulting DAG with canonical_json, writes it to stdout (with a newline), and returns 0.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `args` | `argparse.Namespace` | ✅ | Namespace expected to contain attributes used by the command: input (path to JSON spec), max_depth, fuel, and no_fixed_point.
<br>**Constraints:** args must have attribute 'input' (path-like string or object accepted by Path), args must have attribute 'max_depth' (value passed to unroll), args must have attribute 'fuel' (value passed to unroll), args must have attribute 'no_fixed_point' (boolean; used to set detect_fixed_point = not args.no_fixed_point) |

### Returns

**Type:** `int`

Always returns integer 0 on normal completion.


**Possible Values:**

- 0

### Side Effects

> ❗ **IMPORTANT**
> This function has side effects that modify state or perform I/O operations.

- Reads/parses an input specification via _load_json(Path(args.input)) (file I/O performed by that helper)
- Calls load_mas(...) and unroll(...), which may have their own side effects (not inspected here)
- Writes the serialized DAG JSON to standard output (sys.stdout.write)

### Complexity

O(n) — dominated by the cost of unroll() and serialization, where n corresponds to the size of the MAS / resulting DAG

### Related Functions

- `_load_json` - Called by this function to read/parse the input JSON specification
- `unroll` - Called by this function to transform the MAS into an unrolled DAG

### Notes

- The function performs no internal exception handling; any exceptions raised by _load_json, load_mas, unroll, dag.to_dict(), or canonical_json will propagate to the caller.
- detect_fixed_point passed to unroll is the negation of args.no_fixed_point.
- The function always returns 0; it uses return value as an exit/status code convention rather than signaling errors.

---



#### _cmd_emit

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _cmd_emit(args: argparse.Namespace) -> int
```

### Description

Run emit_build_artifacts using args.emit_build_artifacts, optionally mirror emitted files, write canonical JSON manifest to stdout, and return 0.


Convert args.emit_build_artifacts to a Path and call emit_build_artifacts(out_dir) to produce a manifest. If args.also_mirror is truthy, create the mirror directory and copy regular files and manifest.json from out_dir into it. Finally write the canonical JSON manifest plus a newline to stdout and return 0.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `args` | `argparse.Namespace` | ✅ | Namespace containing command-line options; the function reads args.emit_build_artifacts (path-like) and args.also_mirror (optional path-like or falsy).
<br>**Constraints:** Must have attribute 'emit_build_artifacts' that is interpretable as a filesystem path (string or Path-like)., May have attribute 'also_mirror'; if present and truthy, it must be interpretable as a filesystem path. |

### Returns

**Type:** `int`

Always returns integer 0 on normal completion.


**Possible Values:**

- 0

### Raises

| Exception | Condition |
| --- | --- |
| `AttributeError` | If args lacks the required attributes 'emit_build_artifacts' or code attempts to access missing attributes. |
| `OSError` | Any filesystem operation can raise OSError (e.g., Path.mkdir, read_bytes, write_bytes) if there are permission issues, non-existent paths, or other I/O errors. |
| `Any exception raised by emit_build_artifacts` | If the called emit_build_artifacts(out_dir) function raises an exception, it will propagate. |

### Side Effects

> ❗ **IMPORTANT**
> This function has side effects that modify state or perform I/O operations.

- Calls emit_build_artifacts(out_dir) which may have its own side effects.
- Creates directories on the filesystem via Path.mkdir for the mirror directory (if args.also_mirror is truthy).
- Reads files from the out_dir using Path.iterdir and read_bytes.
- Writes files into the mirror directory using Path.write_bytes (copies files and manifest.json).
- Writes canonical JSON of the manifest to standard output (sys.stdout.write).

### Usage Examples

#### CLI handler invoking artifact emission and mirroring

```python
ns = argparse.Namespace(emit_build_artifacts='build/out', also_mirror='build/mirror')
_cmd_emit(ns)
```

Demonstrates calling _cmd_emit with a namespace that directs emitted artifacts to 'build/out' and mirrors them into 'build/mirror'. The manifest is printed to stdout and the function returns 0.

### Complexity

O(n) where n is the number of entries in out_dir.iterdir() because the function iterates over files to mirror them (dominant cost).

### Related Functions

- `emit_build_artifacts` - Called by _cmd_emit to produce the manifest and populate the output directory.
- `canonical_json` - Called by _cmd_emit to serialize the manifest into canonical JSON written to stdout.

### Notes

- The function assumes emit_build_artifacts returns an object serializable by canonical_json and that there is a manifest.json file at out_dir/manifest.json when mirroring.
- If args.also_mirror is provided but out_dir does not contain the expected files, read_bytes/write_bytes will raise I/O exceptions.
- The function always returns 0 on completion; it does not return non-zero exit codes for error conditions — exceptions will propagate instead.

---



#### main

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def main(argv: Optional[Sequence[str]] = None) -> int
```

### Description

Parse command-line arguments, select and invoke a subcommand handler, and return an exit code.


Builds an argparse parser with validate, unroll, and emit subcommands, assigns handler functions via set_defaults(func=...), and parses argv. If no subcommand is given the help is printed and the function returns 2. It calls args.func(args) and returns its result cast to int; if a RecursiveMasError is raised, a canonical JSON is written to stderr and the function returns 3.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `argv` = `None` | `Optional[Sequence[str]]` | ❌ | Optional sequence of command-line arguments to parse. If None, argparse reads from sys.argv.
<br>**Constraints:** If provided, must be a sequence of strings representing CLI arguments, Elements should be parseable by argparse according to the configured subcommands |

### Returns

**Type:** `int`

An integer exit code from the invoked handler or fixed codes for help/error.


**Possible Values:**

- int(args.func(args)) — result of the selected subcommand handler cast to int
- 2 — returned when no subcommand was supplied and help was printed
- 3 — returned when a RecursiveMasError is caught and its canonical JSON is written to stderr

### Raises

| Exception | Condition |
| --- | --- |
| `Any exception` | Propagated if raised by argparse operations or by the selected subcommand handler (except RecursiveMasError which is caught). |

### Side Effects

> ❗ **IMPORTANT**
> This function has side effects that modify state or perform I/O operations.

- Creates and configures an argparse.ArgumentParser and subparsers (affects process I/O behavior)
- May write help text to stdout when no subcommand is provided
- Invokes the selected subcommand handler via args.func(args) — that handler may perform additional side effects (file I/O, network, etc.)
- Writes canonical JSON error output to stderr when a RecursiveMasError is caught

### Complexity

O(1)

### Related Functions

- `_cmd_validate` - Configured as handler for the 'validate' subcommand; called via args.func when that subcommand is selected
- `_cmd_unroll` - Configured as handler for the 'unroll' subcommand; called via args.func when that subcommand is selected

### Notes

- This function expects the configured handler functions to accept a single argument (the parsed args) and to return a value convertible to int.
- RecursiveMasError is handled specially: its to_dict() is serialized with canonical_json() and written to stderr; other exceptions are not caught here and will propagate.
- When argv is None, argparse uses the process' sys.argv. The function does not itself perform validation beyond argparse configuration.

---


