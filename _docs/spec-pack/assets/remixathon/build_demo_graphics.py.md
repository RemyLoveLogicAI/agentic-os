<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "spec-pack/assets/remixathon/build_demo_graphics.py",
  "source_hash": "8f22dc1b8ff61f0578d940a78494ed5569727eb8829fedd36c2b35155f7ccd96",
  "last_updated": "2026-05-02T17:21:47.074998+00:00",
  "tokens_used": 36940,
  "complexity_score": 3,
  "estimated_review_time_minutes": 10,
  "external_dependencies": [
    "cairosvg"
  ]
}
```

</details>

[Documentation Home](../../../README.md) > [spec-pack](../../README.md) > [assets](../README.md) > [remixathon](./README.md) > **build_demo_graphics**

---

# build_demo_graphics.py

> **File:** `spec-pack/assets/remixathon/build_demo_graphics.py`

![Complexity: Low](https://img.shields.io/badge/Complexity-Low-green) ![Review Time: 10min](https://img.shields.io/badge/Review_Time-10min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Usage Examples](#usage-examples)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This Python module programmatically composes branded SVG demonstration graphics (and PNG exports) for Agentic OS diagrams used in the Anything Remixathon. It defines small SVG helper functions and six diagram-generator functions that return complete SVG strings, then writes SVG files into demo/ and renders PNGs via cairosvg.

Layout is absolute-coordinate based and uses math for geometric positioning; visuals reuse palette constants, gradients, and a shared loop glyph provided by a local build_logos module. Running the file as __main__ triggers generation of all demo assets and prints the produced filenames and sizes.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `cairosvg` | Third-party library used to rasterize SVG to PNG. The write_and_render function calls cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=width) to produce PNG exports from the generated SVG files. (Imported via: 'import cairosvg') |

### Internal Dependencies

| Module | Usage |
| --- | --- |
| [__future__.annotations](../__future__/annotations.md) | Enables postponed evaluation of annotations so code can use list[str] and other forward-referenced/PEP563-style annotations without importing typing at runtime. (Imported via: 'from __future__ import annotations') |
| `math` | Used for geometric calculations in diagram layout: math.cos, math.sin, math.radians, and math.hypot are used to compute positions on an ellipse and unit vectors for arrow geometry (see one_loop_hero). (Imported via: 'import math') |
| [pathlib.Path](../pathlib/Path.md) | Used to compute file system paths and manage the demo output directory: ROOT = Path(__file__).resolve().parent, DEMO = ROOT / 'demo', DEMO.mkdir(...), and to write the SVG/PNG files via Path.write_text and Path.iterdir/stat. (Imported via: 'from pathlib import Path') |
| `build_logos` | Local/internal module that supplies brand palette constants (ACCENT_MAGENTA, ACCENT_VIOLET, GREY, INDIGO, INK, PAPER, WHITE) and SVG helper functions (gradient_def, loop_glyph, svg_doc). These are used throughout to keep consistent colors, gradients, a shared loop glyph, and to wrap parts into a final SVG document string. (Imported via: 'from build_logos import (...)') |

## 📁 Directory

This file is part of the **remixathon** directory. View the [directory index](_docs/spec-pack/assets/remixathon/README.md) to see all files in this module.

## Architecture Notes

- SVGs are produced by concatenating small string snippets from helper functions; layout is absolute-coordinate based (hard-coded sizes and positions) rather than using a scene graph or DOM builder.
- Separation of concerns: low-level helpers (_t, _box, _arrow_marker) create common SVG primitives, diagram functions compose these into larger documents, and write_and_render handles filesystem and rasterization (cairosvg).
- Uses internal build_logos module to centralize visual constants and reusable glyphs/gradients so all diagrams share the same brand palette and loop glyph.

## Usage Examples

### Generate all demo graphics locally

Run the file as a script (python build_demo_graphics.py). main() will create demo/ if missing, write six SVG files (agentic-os-*.svg) and render corresponding PNGs using cairosvg.svg2png with configured output widths. The script prints filenames and sizes after generation.

## Maintenance Notes

- Hardcoded fonts and exact pixel coordinates: diagrams assume availability of the specified fonts (DejaVu Sans, Inter, etc.) and fixed canvas sizes. Changing sizes requires updating many numeric constants.
- cairosvg is a runtime dependency for PNG export; running in environments without cairosvg or the required native libraries will fail at write_and_render. SVG text rendering may differ across platforms.
- build_logos is an internal dependency; changes to exported names (ACCENT_MAGENTA, loop_glyph, gradient_def, svg_doc) will break this module. Keep palette/glyph API stable or update imports accordingly.

---

## Navigation

**↑ Parent Directory:** [Go up](_docs/spec-pack/assets/remixathon/README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*


---

## Functions and Classes


#### _arrow_marker

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def _arrow_marker(mid: str = "arrow", color: str = INDIGO) -> str
```

### Description

Return an SVG <marker> element string that defines a triangular arrowhead using the provided id and fill color.


The function constructs and returns a single string containing an SVG <marker> element. It uses Python f-strings to interpolate the provided mid and color values into the marker attributes and the embedded <path> element that draws a triangular arrowhead (path "M 0 0 L 10 5 L 0 10 z").

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `mid` = `arrow` | `str` | ❌ | The id attribute to assign to the generated <marker> element.
<br>**Constraints:** Should be a valid XML/SVG id string (no spaces), If duplicated in the final SVG, it may collide with other element ids |
| `color` = `INDIGO` | `str` | ❌ | Fill color string to use for the arrowhead path (interpolated into the fill attribute).
<br>**Constraints:** Expected to be a valid SVG/CSS color string (e.g., color name, hex, rgb()), The symbol INDIGO must be defined in the module scope where this function is used |

### Returns

**Type:** `str`

A single string containing a complete SVG <marker> element with a triangular path configured as an arrowhead, using the provided id and color.


**Possible Values:**

- A string like '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="INDIGO"/></marker>' with mid and color substituted

### Complexity

O(1)

### Notes

- The function relies on the name INDIGO being defined in the module; if INDIGO is not defined, a NameError will occur at call time.
- The returned string is intended to be inserted into an SVG document; callers are responsible for placing it inside an appropriate <defs> section or using it where <marker> elements are valid.
- No escaping is performed on mid or color; ensure values do not break SVG/XML structure.

---



#### one_loop_hero

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def one_loop_hero() -> str
```

### Description

Constructs and returns an SVG document string that renders a composed 'One Loop' hero graphic used in the demo assets.


Builds a full 1920x1080 SVG scene by assembling a list of SVG fragment strings: title, subtitle, labeled pill, six stage boxes arranged on an ellipse, connecting arrows, a central loop glyph, and footer labels. It relies on helper render functions (gradient_def, _arrow_marker, _t, _box, loop_glyph) and wraps fragments with svg_doc to produce the final serialized SVG string.

### Returns

**Type:** `str`

An SVG document serialized as a string representing the assembled 'One Loop' hero graphic.


**Possible Values:**

- A valid SVG markup string (typical successful return).

### Usage Examples

#### Generate the SVG for rendering or writing to a file

```python
svg = one_loop_hero()
# then write svg to a file or embed in HTML
```

Demonstrates calling the function to obtain the SVG string to be saved or displayed; the function itself does not perform any file I/O.

### Complexity

O(1)

### Related Functions

- `loop_glyph` - Called by one_loop_hero to produce the central loop graphic element.
- `svg_doc` - Called by one_loop_hero to wrap assembled SVG fragments into a complete SVG document string.

### Notes

- The function relies on module-level constants (e.g., INDIGO, ACCENT_MAGENTA, INK, GREY, WHITE, PAPER) and helper functions (gradient_def, _arrow_marker, _t, _box, loop_glyph, svg_doc) which must be defined in the same module or imported.
- Positions for six stage boxes are computed on an ellipse centered horizontally at y=590 with Rx=540 and Ry=340, and arrows are computed to start/stop just outside rounded rectangle edges using simple rectangle intersection math.
- No explicit error handling is present; any exceptions would originate from called helper functions or standard library calls (e.g., math functions).

---



#### nine_layers

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def nine_layers() -> str
```

### Description

Constructs and returns an SVG document (string) that renders a titled graphic called 'Nine Layers' composed of nine stacked labeled boxes with badges and descriptive text.


Builds the SVG by concatenating fragment strings into a document. It defines canvas dimensions, creates header and footer text, and iterates over a hard-coded list of nine layer tuples to append rectangles, colored number badges, and two text lines per layer using helper functions (gradient_def, _t, _box). Finally it returns the assembled SVG string via svg_doc(W, H, content).

### Returns

**Type:** `str`

An SVG document serialized as a string representing the composed 'Nine Layers' graphic.


**Possible Values:**

- A string containing valid SVG markup when helper functions (gradient_def, _t, _box, svg_doc) and constants are defined and behave as expected
- An error or exception propagation if helper functions raise

### Complexity

O(n) where n is the number of layers iterated (here n=9), due to the loop that appends fragments per layer

### Related Functions

- `gradient_def` - Called by nine_layers to produce a <defs> gradient fragment used in the SVG
- `svg_doc` - Called by nine_layers to wrap and return the final SVG document string from concatenated parts

### Notes

- Function depends on external helper functions (_t, _box, gradient_def, svg_doc) and color/name constants (PAPER, INK, GREY, ACCENT_MAGENTA, ACCENT_VIOLET, INDIGO, WHITE) which must be defined in the module for correct output.
- The layer list is hard-coded; modifying displayed layers requires editing the function's layers list.
- No file I/O or network calls are performed; the function only builds and returns a string.

---



#### governance_gate

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def governance_gate() -> str
```

### Description

Constructs and returns an SVG document (as a string) that visually represents a 'Governance Gate' diagram by assembling SVG fragments and helper-generated elements.


The function defines canvas dimensions and incrementally builds a list of SVG fragment strings (parts) representing shapes, text, arrows, and labels. It uses local helper functions and constants (e.g., _arrow_marker, _box, _t, svg_doc, color constants) to produce SVG fragments, concatenates them, and returns the final SVG document string via svg_doc(W, H, ...).

### Returns

**Type:** `str`

A complete SVG document serialized as a string representing the Governance Gate graphic.


**Possible Values:**

- A string containing the SVG XML document with width 1600 and height 900
- Potentially raises an error (propagated) if any called helper (e.g., _arrow_marker, _t, _box, svg_doc) raises

### Complexity

O(1)

### Related Functions

- `_arrow_marker` - Called by governance_gate to generate SVG marker definitions for arrow endpoints.
- `svg_doc` - Called by governance_gate to wrap concatenated SVG parts into a complete SVG document string returned to the caller.

### Notes

- This function relies on external helper functions and constants (_arrow_marker, _t, _box, svg_doc, INDIGO, ACCENT_MAGENTA, PAPER, INK, GREY, WHITE) which are expected to be defined elsewhere in the module or imported; any exceptions from those helpers will propagate out of governance_gate.
- No file I/O, logging, network calls, or global state mutations occur directly inside this function; it only builds and returns a string.
- Arrow-line creation is done via a nested local helper 'line' which returns SVG fragments and optionally places an inline label using _t.

---



#### line

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def line(x1: float, y1: float, x2: float, y2: float, color: str, marker: str, label: str=None, label_y: float=None) -> str
```

### Description

Constructs and returns an SVG <line> element string (with stroke attributes and marker) and optionally appends an SVG text element centered on the line as a label.


Builds an SVG <line> element from two endpoints, stroke color, fixed stroke width, and a marker reference. If label is provided, computes a midpoint (using label_y when given or a default offset) and appends an SVG text element produced by a helper _t(...). Returns the concatenated SVG string.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `x1` | `float` | ✅ | The x-coordinate of the start point of the line.
<br>**Constraints:** Numeric value (int or float) expected for coordinate arithmetic |
| `y1` | `float` | ✅ | The y-coordinate of the start point of the line.
<br>**Constraints:** Numeric value (int or float) expected for coordinate arithmetic |
| `x2` | `float` | ✅ | The x-coordinate of the end point of the line.
<br>**Constraints:** Numeric value (int or float) expected for coordinate arithmetic |
| `y2` | `float` | ✅ | The y-coordinate of the end point of the line.
<br>**Constraints:** Numeric value (int or float) expected for coordinate arithmetic |
| `color` | `str` | ✅ | Stroke color used for the line and (if present) the label text fill.
<br>**Constraints:** String suitable for SVG stroke/fill (e.g., color name, hex code) |
| `marker` | `str` | ✅ | Identifier (without the '#') used to form the marker-end URL reference for the line (becomes url(#marker)).
<br>**Constraints:** String used as an SVG marker id; the referenced marker must exist in the SVG document to render |
| `label` = `None` | `str | None` | ❌ | Optional text to render centered on the line; if omitted no text element is appended.
<br>**Constraints:** If provided, will be passed to helper _t(...) to produce an SVG text element |
| `label_y` = `None` | `float | None` | ❌ | Optional override for the vertical position of the label; if None, a default (midpoint minus 8) is used.
<br>**Constraints:** Numeric value if provided; otherwise computed from y1 and y2 |

### Returns

**Type:** `str`

A string containing the SVG <line> element and, if label is provided, the SVG text element produced by _t concatenated together.


**Possible Values:**

- A string like '<line x1="..." y1="..." x2="..." y2="..." stroke="..." stroke-width="3" marker-end="url(#marker)"/>'
- The same line string plus additional SVG text markup returned by _t(...) when label is provided

### Complexity

O(1)

### Related Functions

- `_t` - Called by line to produce the SVG text element for the label

### Notes

- The function assumes a helper function _t(...) is defined in scope and returns an SVG text element string.
- The produced marker-end attribute references url(#marker) — the marker id should exist in the overall SVG for visual markers to appear.
- There are no explicit type checks; passing non-numeric types for coordinates may raise TypeError during arithmetic.

---



#### system_contract

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def system_contract() -> str
```

### Description

Constructs and returns an SVG document (as a string) that renders a three-column "System Contract" graphic describing Input → Processing → Output.


Builds an SVG by assembling fragments (definitions, background, title, three boxed columns with titles and bullets, connector arrows, footer) into a list of strings. It uses helper functions and constants to produce SVG pieces, concatenates them, and wraps the result with svg_doc(W, H, content) to return the final SVG string.

### Returns

**Type:** `str`

An SVG document serialized as a string representing the constructed graphic.


**Possible Values:**

- A string containing SVG markup sized 1600x900 with the composed graphic
- An SVG string produced by svg_doc(...) incorporating the concatenated parts

### Complexity

O(1)

### Related Functions

- `_arrow_marker` - Called by system_contract to produce an SVG marker definition used for arrow endpoints
- `svg_doc` - Called by system_contract to wrap the assembled SVG fragments into a complete SVG document string

### Notes

- The function relies on external helper functions and constants (e.g., _t, _box, _arrow_marker, svg_doc, INDIGO, PAPER, WHITE, INK, GREY, ACCENT_VIOLET, ACCENT_MAGENTA). If any are missing or behave differently, the output will be affected.
- No input validation or error handling is present; any exceptions would originate from the helper functions called or from formatting operations.
- The function constructs fixed layout values (width, height, column sizes and positions) and returns a complete SVG with those hard-coded dimensions.

---



#### three_gaps

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def three_gaps() -> str
```

### Description

Construct and return an SVG document (as a string) that renders a three-row graphic comparing 'GAP' items to 'AGENTIC OS' fixes.


The function builds a list of SVG fragment strings representing a full SVG image of width 1600 and height 900. It appends header text and then iterates over a fixed list of three rows, creating left 'gap' boxes, a connector arrow, and right 'fix' boxes for each row by calling helper functions (_box, _t) and finally wraps the concatenated fragments with svg_doc to produce the final SVG string.

### Returns

**Type:** `str`

An SVG document serialized as a string representing the composed graphic.


**Possible Values:**

- A valid SVG string containing <rect>, <path> and text elements composing the described layout
- Possibly raises a runtime error if referenced globals or helper functions (e.g., svg_doc, _t, _box, constants) are missing

### Complexity

O(1)

### Related Functions

- `_t` - Called by three_gaps to produce text SVG fragments (text rendering helper)
- `svg_doc` - Called by three_gaps to wrap the concatenated SVG fragments into a final SVG document string

### Notes

- The function references globals/constants such as PAPER, INK, ACCENT_MAGENTA, INDIGO and helper functions _box, _t, svg_doc; if any are undefined at runtime, the function will raise a NameError.
- Layout is driven by a fixed rows list of three entries; changing the rows list or constants will alter the output.
- No explicit error handling is present; this function assumes helper functions return valid SVG fragments and svg_doc produces the final SVG string.

---



#### evidence_flow

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def evidence_flow() -> str
```

### Description

Constructs and returns an SVG document (as a string) that visualizes an 'Evidence + Memory Loop' diagram.


Builds an SVG image by concatenating fragments in a parts list. It sets canvas dimensions and definitions, adds background, title and subtitle, creates five labeled rectangular nodes with connecting arrows, and draws a curved feedback path from the 'Memory' node back to the first 'Action' node before wrapping everything with svg_doc and returning the string.

### Returns

**Type:** `str`

An SVG document serialized as a string representing the constructed diagram.


**Possible Values:**

- A non-empty SVG string containing <svg>... content produced by svg_doc
- Potentially an error if required helper functions or constants are undefined (not raised explicitly by this function)

### Complexity

O(1)

### Related Functions

- `_arrow_marker` - Called by evidence_flow to produce SVG <marker> definitions for arrows
- `svg_doc` - Called by evidence_flow to wrap the assembled SVG fragments into a complete document string

### Notes

- Function depends on several helper functions (_arrow_marker, _t, _box, svg_doc) and constants (W, H are local; color constants like INDIGO, ACCENT_MAGENTA, etc. are referenced) that must be defined elsewhere in the module.
- The layout parameters (positions, box sizes, gaps) are hard-coded; the diagram will always contain five nodes as implemented.
- No explicit error handling is present; missing helpers or constants will raise NameError at runtime but are not handled here.

---



#### write_and_render

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def write_and_render(name: str, content: str, *, width: int) -> None
```

### Description

Writes SVG content to a file named {name}.svg under DEMO and invokes cairosvg.svg2png to render a PNG {name}.png at the specified width.


The function constructs paths for an SVG and PNG file under a global DEMO path, writes the provided SVG content to the SVG path using Path.write_text, and then calls cairosvg.svg2png with the SVG file URL, an output file path for the PNG, and the requested output_width. It performs no return value and relies on the DEMO Path and cairosvg being defined/imported elsewhere in the module.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | ✅ | Base filename (without extension) used to build the SVG and PNG filenames under DEMO; final files are {name}.svg and {name}.png.
 |
| `content` | `str` | ✅ | The SVG document content to write into the .svg file.
 |
| `width` | `int` | ✅ | Keyword-only integer specifying the output PNG width (passed to cairosvg.svg2png as output_width).
 |

### Returns

**Type:** `None`

This function does not return a value; it returns None implicitly after performing its I/O actions.


**Possible Values:**

- None

### Side Effects

> ❗ **IMPORTANT**
> This function has side effects that modify state or perform I/O operations.

- Writes an SVG file to the filesystem at DEMO / f"{name}.svg" using Path.write_text
- Creates a PNG file at DEMO / f"{name}.png" by calling cairosvg.svg2png (which performs file I/O and image rendering)

### Complexity

O(1)

### Notes

- Relies on a module-level DEMO Path object and an imported cairosvg.svg2png function; those must be defined/imported elsewhere in the file.
- This function will overwrite existing files with the same names without warning.
- Any exceptions raised will be those propagated from Path.write_text or cairosvg.svg2png (no explicit exception handling in this function).

---



#### main

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```python
def main() -> None
```

### Description

Calls helper generators to render demo assets and then prints a listing of files in the DEMO directory with their sizes.


The function calls write_and_render repeatedly with specific asset names and generator functions (one_loop_hero, nine_layers, governance_gate, system_contract, three_gaps, evidence_flow) to produce demonstration graphics. After rendering, it lists files in the DEMO directory (sorted) and prints each filename with its size in bytes; it does not return a value.

### Returns

**Type:** `None`

This function does not return a value; it returns None implicitly.


**Possible Values:**

- None

### Side Effects

> ❗ **IMPORTANT**
> This function has side effects that modify state or perform I/O operations.

- Calls write_and_render(...) multiple times (invokes external rendering/writing logic)
- Calls the generator functions one_loop_hero(), nine_layers(), governance_gate(), system_contract(), three_gaps(), evidence_flow()
- Reads the filesystem by iterating DEMO.iterdir() and calling entry.stat().st_size to obtain file sizes
- Writes formatted output to stdout via print()

### Complexity

O(m log m) where m is the number of entries in the DEMO directory (due to sorting); rendering calls are a fixed number of invocations.

### Related Functions

- `write_and_render` - Called by main to perform the actual writing/rendering work for each named asset
- `one_loop_hero / nine_layers / governance_gate / system_contract / three_gaps / evidence_flow` - Generator/helper functions called by main to produce content passed to write_and_render

### Notes

- No exceptions are raised explicitly in this function; exceptions thrown by write_and_render or the generator functions or filesystem operations will propagate.
- The function assumes DEMO is defined in the module scope and is iterable via iterdir().
- Formatting of printed file name and size uses a fixed width for the name (50 characters) and right-aligned byte count.

---


