# RecursiveMAS — Inner Links & Loop Unrolling

Last updated: Saturday, May 2, 2026 (PDT)

This document is the canonical, TUI/CLI-only contract for RecursiveMAS — the
recursive Multi-Agent System (MAS) primitive used inside the Agentic OS
orchestration mesh.

A RecursiveMAS is a directed graph of agent nodes whose nodes may themselves
contain another MAS. The two contracts defined here are:

1. **Inner links** — typed edges that cross sub-MAS boundaries (outer↔inner)
   or stay strictly inside a sub-MAS (inner↔inner, including self-recursion).
2. **Loop unrolling** — the deterministic transformation that converts any
   self-referential or cyclic recursion into a finite, bounded execution DAG
   suitable for receipted execution and evidence capture.

All schemas and reference behavior in this spec are scoped to non-GUI
(TUI/CLI) execution paths, consistent with the existing repo norm
(`research/docs/canonical-json-spec.md`, PR #3).

---

## 1) Scope

In scope:
- Inner-link grammar, naming, and validation.
- Loop unrolling semantics: depth bound, fuel budget, fixed-point detection,
  cycle handling, deterministic frame naming.
- A canonical JSON encoding for both the input MAS and the unrolled DAG, so
  receipts and artifact digests are reproducible.
- A reference Python implementation (stdlib-only) that computes inner-link
  resolution and loop unrolling, and a stdlib-only test suite.
- Build artifacts emitted under `build-artifacts/RecursiveMAS/`.

Out of scope:
- Any runtime/execution engine. RecursiveMAS produces *plans*, not actions.
- GUI surfaces. Verification is via CLI (`python -m unittest`).
- Specific approval-gate or policy semantics — those are owned by the
  Aegis / Violet Covenant layer; RecursiveMAS only marks edges with
  capability annotations.

---

## 2) Vocabulary

| Term | Meaning |
|---|---|
| **MAS** | A directed multigraph of agent **nodes** connected by typed **links**. |
| **Sub-MAS** | A MAS embedded as a single node inside an outer MAS. |
| **Outer port** | A named entry/exit on a sub-MAS, addressed from outside as `("*outer*", port_name)` from inside the sub-MAS. |
| **Inner link** | A directed edge inside a sub-MAS or a sub-MAS boundary edge. |
| **Self-recurse node** | A `kind: "self_recurse"` node — denotes a recursive invocation of its containing sub-MAS. |
| **Frame** | One copy of a sub-MAS produced by unrolling, identified by `<mas_id>#<depth>`. |
| **Depth** | The number of self-recursion levels above a frame (root = `0`). |
| **Fuel** | A monotonically non-increasing integer budget consumed once per produced frame. |

---

## 3) Input data model

The input to RecursiveMAS is a single document (`mas_spec`) that follows the
schema in `research/docs/recursive-mas/inner-links.schema.json`.

### 3.1 Top-level document

```jsonc
{
  "schema_version": "recursive-mas/v0.1",
  "mas_id": "outer.root",
  "nodes":   [ /* see 3.2 */ ],
  "links":   [ /* see 3.3 */ ],
  "sub_mas": [ /* see 3.4, optional */ ],
  "limits": {
    "max_depth": 4,
    "fuel": 16
  }
}
```

`schema_version` MUST equal `"recursive-mas/v0.1"`. `mas_id` MUST be a
dotted lowercase identifier (`[a-z][a-z0-9_]*(\.[a-z0-9_]+)*`). `limits` is
optional; if absent, defaults are `max_depth = 4`, `fuel = 64`.

### 3.2 Nodes

A node is one of:

| `kind` | Meaning |
|---|---|
| `"agent"` | A leaf agent invocation. |
| `"sub_mas"` | An embedded sub-MAS, identified by `sub_mas` (the `mas_id` of an entry under `sub_mas[]`). |
| `"self_recurse"` | A recursion handle for the *containing* sub-MAS. Allowed only inside a `sub_mas[]` entry. |

```jsonc
{
  "id": "verify",
  "kind": "agent",
  "ports": { "in": ["evidence"], "out": ["pass", "retry"] },
  "capabilities": ["evidence.write"]   // optional, opaque to RecursiveMAS
}
```

Node IDs MUST be unique within their containing MAS. Port names MUST be
non-empty `[a-z][a-z0-9_]*`. The reserved node id `"*outer*"` denotes the
parent boundary and MUST NOT be declared explicitly.

### 3.3 Links

```jsonc
{
  "from": { "node": "act",     "port": "evidence" },
  "to":   { "node": "verify",  "port": "evidence" },
  "kind": "data",
  "guard": "ok"          // optional; opaque label
}
```

A link's `kind` is one of `"data" | "control" | "evidence"`. The `guard`
field is an opaque label used by the policy layer; RecursiveMAS only
preserves it.

### 3.4 Sub-MAS

`sub_mas[]` is a list of nested MAS bodies, each shaped exactly like the
top-level document but without `schema_version`:

```jsonc
{
  "mas_id": "outer.exec_loop",
  "nodes":  [ ... ],
  "links":  [ ... ],
  "sub_mas":[ ... ]
}
```

A sub-MAS becomes addressable via a `kind: "sub_mas"` node whose `sub_mas`
field equals its `mas_id`.

---

## 4) Inner-link grammar (normative)

An **inner link** is any link inside the body of a sub-MAS, including links
that touch the sub-MAS boundary. There are exactly four legal shapes; any
other shape MUST be rejected with `error.inner_link.shape_invalid`.

| # | Shape | `from.node` | `to.node` | Direction |
|---|---|---|---|---|
| 1 | outer→inner | `"*outer*"` | a real node id in the same sub-MAS | enters the sub-MAS |
| 2 | inner→outer | a real node id in the same sub-MAS | `"*outer*"` | leaves the sub-MAS |
| 3 | inner→inner | a real node id | a different real node id | within the sub-MAS |
| 4 | inner→self  | a real node id | a `self_recurse` node id | recursive call |

### 4.1 Port matching

For shape 1 (`outer→inner`) the link's `from.port` MUST match a port name
declared on the *enclosing* `kind: "sub_mas"` node's `ports.in`. The link's
`to.port` MUST match the target node's `ports.in`.

For shape 2 (`inner→outer`) the link's `from.port` MUST match the source
node's `ports.out`, and `to.port` MUST match the enclosing sub-MAS node's
`ports.out`.

For shapes 3 and 4 the link's `from.port` MUST be in the source node's
`ports.out` and `to.port` in the target node's `ports.in`.

### 4.2 Determinism

Within a single MAS body, links are stable-sorted by
`(from.node, from.port, to.node, to.port, kind, guard or "")` before any
canonicalization. This makes hashing of the resolved graph deterministic.

### 4.3 Capability annotation

Each resolved inner link inherits the union of its source and target
node's `capabilities`. RecursiveMAS does not interpret capabilities — it
only carries them through to receipts so the policy layer can gate on
them later.

---

## 5) Loop unrolling (normative)

### 5.1 Goal

Replace every `self_recurse` node with a finite chain of frames so the
overall plan becomes a DAG. The transformation MUST be:

- **Bounded** by `limits.max_depth` and `limits.fuel`.
- **Deterministic**: same input → byte-identical output (after
  canonical JSON).
- **Lossless for non-recursive structure**: agent nodes and inner-only
  links inside non-recursive sub-MAS bodies pass through unchanged
  (modulo frame renaming).

### 5.2 Frame identity

A frame's id is `<mas_id>#<depth>`, where `mas_id` is the sub-MAS body's
`mas_id` and `depth` is its self-recursion depth (root = `0`). Frame ids
MUST be unique across the unrolled DAG.

A node inside a frame is renamed to `<mas_id>#<depth>::<node_id>`.

### 5.3 Algorithm

Given a top-level `mas_spec` and budget `(max_depth, fuel)`:

```text
unroll(mas, depth=0, fuel):
    if depth > max_depth or fuel <= 0:
        emit a single sink node:
            id = "<mas.mas_id>#<depth>::__cap__"
            kind = "depth_cap" or "fuel_exhausted"
            ports = { in: <union of self_recurse inputs>, out: [] }
        return frame, fuel - 1

    for each node in mas.nodes:
        if node.kind == "agent":
            copy verbatim, rename id with frame prefix
        elif node.kind == "sub_mas":
            recursively unroll the referenced sub-MAS body at depth=0
            (sub-MAS is *not* the same body as the current self-recurse target)
        elif node.kind == "self_recurse":
            frame_next, fuel = unroll(mas, depth + 1, fuel - 1)
            stitch every link into this self_recurse node onto
            frame_next's outer-in ports, and every link out of this
            self_recurse node onto frame_next's outer-out ports.

    rename all link endpoints according to the renaming above.
    return frame, fuel
```

### 5.4 Cap behavior

When the budget is exhausted, the canonical sink replaces all in-edges to
the would-be next frame and emits no out-edges. The sink carries an
`evidence` annotation `loop.depth_cap_reached` or
`loop.fuel_exhausted` so receipts can record *why* the loop terminated.

### 5.5 Fixed-point detection (optional, on by default)

If two consecutive frames produce structurally identical sub-graphs after
canonicalization (i.e. `canonicalJSON(frame_d) == canonicalJSON(frame_{d-1})`
modulo frame prefixes), the unroller MAY emit a `fixed_point` sink at
depth `d` instead of continuing. The reason is recorded as
`loop.fixed_point_reached`. Fixed-point detection MUST NOT change the
output for inputs that don't reach a fixed point.

### 5.6 Cycles without `self_recurse`

A cycle in `links` that doesn't go through a `self_recurse` node is a
hard error: `error.loop.unguarded_cycle`. Recursion MUST be expressed
explicitly via a `self_recurse` node so the depth/fuel bound applies.

---

## 6) Output: unrolled DAG

The output document is described by
`research/docs/recursive-mas/loop-unrolling.schema.json`. Its top-level
shape is:

```jsonc
{
  "schema_version": "recursive-mas-unrolled/v0.1",
  "source_digest":  "sha256:<hex>",
  "limits":         { "max_depth": 4, "fuel": 16 },
  "frames": [
    {
      "frame_id":  "outer.exec_loop#0",
      "mas_id":    "outer.exec_loop",
      "depth":     0,
      "nodes":     [ /* renamed agents + caps */ ],
      "termination": null
    },
    /* ... */
    {
      "frame_id":  "outer.exec_loop#3",
      "mas_id":    "outer.exec_loop",
      "depth":     3,
      "nodes":     [ /* ... */ ],
      "termination": {
        "reason": "loop.depth_cap_reached",
        "node_id": "outer.exec_loop#3::__cap__"
      }
    }
  ],
  "links": [ /* renamed inner links + boundary stitches */ ],
  "evidence": [
    { "kind": "loop.depth_cap_reached", "frame_id": "outer.exec_loop#3" }
  ]
}
```

`source_digest` is `sha256(canonicalJSON(source_mas_spec))` per
`canonical-json-spec.md`.

### 6.1 Resolved inner-link record

`resolve_inner_links(mas)` produces a normalized record with
`schema_version = "recursive-mas-resolved/v0.1"` whose top-level shape is:

```jsonc
{
  "schema_version": "recursive-mas-resolved/v0.1",
  "source_digest":  "sha256:<hex>",
  "root": {
    "mas_id":          "outer.root",
    "outer_in_ports":  ["request"],
    "outer_out_ports": ["receipt"],
    "links": [
      {
        "from":  { "node": "ingest", "port": "parsed" },
        "to":    { "node": "plan",   "port": "parsed" },
        "kind":  "data",
        "shape": "inner_to_inner",
        "capabilities": ["plan.write", "voice.read"]
      }
      /* … */
    ],
    "sub_bodies": [ /* recursive */ ]
  }
}
```

The resolved record is intentionally lightweight and does *not* have its
own JSON Schema file (it's a derivative artifact, fully determined by the
input + reference implementation). Consumers that need a schema can derive
one from the reference implementation's `ResolvedBody` / `ResolvedLink`
dataclasses.

---

## 7) Determinism & hashing

All artifacts under `build-artifacts/RecursiveMAS/` are produced with
deterministic orderings:

- `nodes[]` sorted by `id`.
- `links[]` sorted by the tuple in §4.2.
- `frames[]` sorted by `(mas_id, depth)`.
- `evidence[]` sorted by `(frame_id, kind)`.
- All maps emitted with sorted keys.

The reference implementation MUST emit canonical JSON suitable for
sha256 hashing. The committed `manifest.json` records:

```jsonc
{
  "schema_version": "recursive-mas-manifest/v0.1",
  "generated_at":   "<RFC3339 in UTC>",
  "artifacts": [
    { "path": "inner-links.example.json",   "sha256": "<hex>", "bytes": 1234 },
    { "path": "loop-unrolling.example.json","sha256": "<hex>", "bytes": 5678 }
  ]
}
```

Note: the `generated_at` field varies between runs and is
*excluded* from any digest the manifest itself participates in. The
manifest is the only file that may carry a non-deterministic field.

---

## 8) Error contract

| Code | Meaning |
|---|---|
| `error.schema.unknown_version` | `schema_version` not recognized. |
| `error.node.id_collision` | Two nodes share an id within the same MAS body. |
| `error.node.bad_kind` | `kind` not in `{agent, sub_mas, self_recurse}`. |
| `error.node.self_recurse_at_root` | A `self_recurse` node appears at the top level (root MAS) — `self_recurse` is only legal inside `sub_mas[]` bodies. |
| `error.inner_link.shape_invalid` | Link doesn't match shapes 1–4 in §4. |
| `error.inner_link.port_unknown` | Link references a port not declared on the node. |
| `error.sub_mas.unknown` | `kind: "sub_mas"` references a `mas_id` that isn't defined in any enclosing scope. |
| `error.sub_mas.boundary_mismatch` | Outer-port set on the sub-MAS node disagrees with the in/out endpoints used by inner links. |
| `error.loop.unguarded_cycle` | Cycle in `links` without a `self_recurse` node. |
| `error.budget.invalid` | `max_depth` or `fuel` is negative or non-integer. |

Each error MUST be reported as `{"code": "...", "where": "<path>", "message": "..."}`
where `<path>` is a JSON-Pointer-style locator into the source document.

---

## 9) Reference implementation & tests

The reference implementation lives at
`research/docs/recursive-mas/reference/recursive_mas.py` and depends only
on the Python standard library. It exposes:

- `load_mas(spec: dict) -> Mas`
- `resolve_inner_links(mas: Mas) -> ResolvedInnerLinks`
- `unroll(mas: Mas, *, max_depth: int, fuel: int) -> UnrolledDag`
- `canonical_json(value) -> str`
- `digest(value) -> str` — `sha256(canonical_json(value))` lowercase hex.

Tests are at
`research/docs/recursive-mas/reference/test_recursive_mas.py` and run via:

```bash
python -m unittest discover -s research/docs/recursive-mas/reference -p 'test_*.py' -v
```

CI scope: this is a TUI/CLI-only spec; the existing repo CI (security
scanners, code review bots, image optimizer) covers diff hygiene. No new
GitHub Actions are added by this PR.

---

## 10) Build artifacts

The reference implementation produces, deterministically, the four
example artifacts committed under `build-artifacts/RecursiveMAS/`:

| Path | Purpose |
|---|---|
| `example.mas.json` | The input MAS used to generate the others. |
| `inner-links.example.json` | Resolved inner-link table after §4 validation. |
| `loop-unrolling.example.json` | Unrolled DAG for the same input under `max_depth=3, fuel=8`. |
| `manifest.json` | sha256 digests for the above. |

These artifacts are also mirrored to
`/home/workdir/artifacts/RecursiveMAS/` inside the Devin container, per
issue #16. The external sync target is
`/home/workspace/RemyLoveLogicAI/agentic-os/build-artifacts/RecursiveMAS/`.

To regenerate from a clean checkout:

```bash
python research/docs/recursive-mas/reference/recursive_mas.py \
    --emit-build-artifacts build-artifacts/RecursiveMAS \
    --also-mirror /home/workdir/artifacts/RecursiveMAS
```

---

## 11) Versioning

This document is `recursive-mas/v0.1`. Backwards-incompatible changes
bump the minor version (`v0.2`, `v0.3`, …). The schemas and the example
artifacts MUST stay in lockstep with the document version they were
generated against. A future v1.0 will cement the inner-link grammar; the
loop-unrolling algorithm may continue to gain detection passes
(structural fixed-point, capability-aware caps) without bumping major.
