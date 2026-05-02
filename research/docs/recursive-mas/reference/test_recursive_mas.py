#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the RecursiveMAS reference implementation.

Run with:

    python -m unittest discover -s research/docs/recursive-mas/reference \\
        -p 'test_*.py' -v

Stdlib only — no external test deps.
"""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from recursive_mas import (  # noqa: E402
    DEFAULT_FUEL,
    DEFAULT_MAX_DEPTH,
    OUTER,
    Mas,
    RecursiveMasError,
    SCHEMA_VERSION_INPUT,
    canonical_json,
    digest,
    emit_build_artifacts,
    example_mas_spec,
    load_mas,
    resolve_inner_links,
    unroll,
)


class CanonicalJsonTests(unittest.TestCase):
    def test_sorted_keys_no_whitespace(self) -> None:
        self.assertEqual(canonical_json({"b": 1, "a": 2}), '{"a":2,"b":1}')

    def test_unicode_separators_escaped(self) -> None:
        self.assertIn("\\u2028", canonical_json({"k": "x\u2028y"}))
        self.assertIn("\\u2029", canonical_json({"k": "x\u2029y"}))

    def test_digest_is_lowercase_hex(self) -> None:
        d = digest({"a": [1, 2, 3]})
        self.assertTrue(d.startswith("sha256:"))
        self.assertEqual(len(d), len("sha256:") + 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in d.split(":", 1)[1]))

    def test_byte_identical_for_reordered_inputs(self) -> None:
        a = {"a": {"x": 1, "y": 2}, "b": [1, 2]}
        b = {"b": [1, 2], "a": {"y": 2, "x": 1}}
        self.assertEqual(canonical_json(a), canonical_json(b))


class LoadMasTests(unittest.TestCase):
    def test_example_loads_and_resolves(self) -> None:
        mas = load_mas(example_mas_spec())
        resolved = resolve_inner_links(mas)
        self.assertEqual(resolved.schema_version, "recursive-mas-resolved/v0.1")
        self.assertEqual(resolved.root.mas_id, "outer.root")
        # Root has its outer surface inferred from *outer* references.
        self.assertEqual(resolved.root.outer_in_ports, ("request",))
        self.assertEqual(resolved.root.outer_out_ports, ("receipt",))
        # Sub-MAS is present and validated
        self.assertEqual(len(resolved.root.sub_bodies), 1)
        sub = resolved.root.sub_bodies[0]
        self.assertEqual(sub.mas_id, "outer.exec_loop")
        self.assertEqual(sub.outer_in_ports, ("plan",))
        self.assertEqual(sub.outer_out_ports, ("report",))
        # Shapes present
        shapes = sorted({l.shape for l in sub.links})
        self.assertEqual(
            shapes,
            ["inner_to_inner", "inner_to_self", "outer_in", "outer_out"],
        )

    def test_unknown_schema_version_rejected(self) -> None:
        spec = example_mas_spec()
        spec["schema_version"] = "recursive-mas/v9.99"
        with self.assertRaises(RecursiveMasError) as cm:
            load_mas(spec)
        self.assertEqual(cm.exception.code, "error.schema.unknown_version")

    def test_self_recurse_at_root_is_rejected(self) -> None:
        bad = {
            "schema_version": SCHEMA_VERSION_INPUT,
            "mas_id": "root.bad",
            "nodes": [
                {
                    "id": "x",
                    "kind": "self_recurse",
                    "ports": {"in": ["a"], "out": ["b"]},
                }
            ],
            "links": [],
        }
        with self.assertRaises(RecursiveMasError) as cm:
            load_mas(bad)
        self.assertEqual(cm.exception.code, "error.node.self_recurse_at_root")

    def test_duplicate_node_id_is_rejected(self) -> None:
        spec = {
            "schema_version": SCHEMA_VERSION_INPUT,
            "mas_id": "root",
            "nodes": [
                {"id": "n", "kind": "agent", "ports": {"in": ["a"], "out": ["b"]}},
                {"id": "n", "kind": "agent", "ports": {"in": ["c"], "out": ["d"]}},
            ],
            "links": [],
        }
        with self.assertRaises(RecursiveMasError) as cm:
            load_mas(spec)
        self.assertEqual(cm.exception.code, "error.node.id_collision")


class InnerLinkValidationTests(unittest.TestCase):
    def test_unknown_port_is_rejected(self) -> None:
        spec = example_mas_spec()
        # plan→exec link references a port that doesn't exist on exec.
        for l in spec["links"]:
            if l["from"]["node"] == "plan" and l["to"]["node"] == "exec":
                l["to"]["port"] = "nonexistent"
        with self.assertRaises(RecursiveMasError) as cm:
            resolve_inner_links(load_mas(spec))
        self.assertEqual(cm.exception.code, "error.inner_link.port_unknown")

    def test_outer_outer_link_is_rejected(self) -> None:
        spec = example_mas_spec()
        spec["links"].append(
            {
                "from": {"node": OUTER, "port": "request"},
                "to": {"node": OUTER, "port": "receipt"},
            }
        )
        with self.assertRaises(RecursiveMasError) as cm:
            resolve_inner_links(load_mas(spec))
        self.assertEqual(cm.exception.code, "error.inner_link.shape_invalid")

    def test_unguarded_cycle_is_rejected(self) -> None:
        spec = example_mas_spec()
        # Add a feedback link inside the sub-MAS that doesn't go through self_recurse.
        sub = spec["sub_mas"][0]
        sub["nodes"].append(
            {
                "id": "echo",
                "kind": "agent",
                "ports": {"in": ["pass"], "out": ["pass"]},
            }
        )
        # verify.pass already goes to *outer*; add verify.pass→echo.pass and echo.pass→verify.next_plan
        # which forms a cycle verify→echo→verify (via verify.next_plan).
        sub["links"].append(
            {
                "from": {"node": "verify", "port": "pass"},
                "to": {"node": "echo", "port": "pass"},
            }
        )
        sub["nodes"][1]["ports"]["in"].append("loopback")  # verify gets a loopback port
        sub["links"].append(
            {
                "from": {"node": "echo", "port": "pass"},
                "to": {"node": "verify", "port": "loopback"},
            }
        )
        # cycle: verify -> echo -> verify
        with self.assertRaises(RecursiveMasError) as cm:
            resolve_inner_links(load_mas(spec))
        self.assertEqual(cm.exception.code, "error.loop.unguarded_cycle")

    def test_self_recurse_subset_violation(self) -> None:
        spec = example_mas_spec()
        # Make self_recurse expose a port the body's outer surface doesn't have.
        sub = spec["sub_mas"][0]
        for n in sub["nodes"]:
            if n["id"] == "loop":
                n["ports"]["in"].append("ghost")
        with self.assertRaises(RecursiveMasError) as cm:
            resolve_inner_links(load_mas(spec))
        self.assertEqual(cm.exception.code, "error.sub_mas.boundary_mismatch")

    def test_unknown_sub_mas_is_rejected(self) -> None:
        spec = example_mas_spec()
        for n in spec["nodes"]:
            if n["id"] == "exec":
                n["sub_mas"] = "outer.unknown"
        spec["sub_mas"] = []
        with self.assertRaises(RecursiveMasError) as cm:
            resolve_inner_links(load_mas(spec))
        self.assertEqual(cm.exception.code, "error.sub_mas.unknown")


class UnrollTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mas = load_mas(example_mas_spec())

    def test_basic_unroll(self) -> None:
        dag = unroll(self.mas)
        self.assertEqual(dag.schema_version, "recursive-mas-unrolled/v0.1")
        self.assertTrue(dag.source_digest.startswith("sha256:"))
        # We expect a root frame and a chain of self-recursion frames terminated by a cap.
        loop_frames = [f for f in dag.frames if f.mas_id == "outer.exec_loop"]
        self.assertGreaterEqual(len(loop_frames), 2)
        terminations = [f.termination for f in loop_frames if f.termination]
        self.assertGreaterEqual(len(terminations), 1)
        self.assertTrue(
            any(t["reason"] == "loop.depth_cap_reached" for t in terminations)
            or any(t["reason"] == "loop.fuel_exhausted" for t in terminations)
            or any(t["reason"] == "loop.fixed_point_reached" for t in terminations)
        )

    def test_unroll_is_deterministic(self) -> None:
        a = canonical_json(unroll(self.mas).to_dict())
        b = canonical_json(unroll(load_mas(example_mas_spec())).to_dict())
        self.assertEqual(a, b)

    def test_depth_cap_kicks_in(self) -> None:
        # Disable fixed-point detection so the depth bound is the only termination cause.
        dag = unroll(self.mas, max_depth=1, fuel=DEFAULT_FUEL, detect_fixed_point=False)
        depth_caps = [
            f for f in dag.frames
            if f.termination and f.termination["reason"] == "loop.depth_cap_reached"
        ]
        self.assertGreaterEqual(len(depth_caps), 1)
        # max_depth=1 ⇒ depths 0 and 1 are produced; depth=2 frame is the cap.
        self.assertEqual(depth_caps[0].depth, 2)

    def test_fuel_cap_kicks_in(self) -> None:
        dag = unroll(self.mas, max_depth=99, fuel=2, detect_fixed_point=False)
        caps = [
            f for f in dag.frames
            if f.termination and f.termination["reason"] == "loop.fuel_exhausted"
        ]
        self.assertGreaterEqual(len(caps), 1)

    def test_fixed_point_detected(self) -> None:
        # The example body is structurally identical at every recursion depth,
        # so the fixed-point detector should engage at depth=1 instead of letting
        # the depth cap fire at max_depth.
        dag = unroll(self.mas, max_depth=99, fuel=99, detect_fixed_point=True)
        fps = [
            f for f in dag.frames
            if f.termination and f.termination["reason"] == "loop.fixed_point_reached"
        ]
        self.assertGreaterEqual(len(fps), 1)

    def test_no_self_recurse_means_no_recursion_frames(self) -> None:
        spec = example_mas_spec()
        # Drop the self_recurse node and the link that targets it.
        sub = spec["sub_mas"][0]
        sub["nodes"] = [n for n in sub["nodes"] if n["id"] != "loop"]
        sub["links"] = [
            l for l in sub["links"]
            if l["from"]["node"] != "loop" and l["to"]["node"] != "loop"
        ]
        mas = load_mas(spec)
        dag = unroll(mas)
        # Only depth-0 frames; no caps.
        self.assertTrue(all(f.depth == 0 for f in dag.frames))
        self.assertTrue(all(f.termination is None for f in dag.frames))

    def test_node_ids_are_uniquely_qualified(self) -> None:
        dag = unroll(self.mas)
        seen: set[str] = set()
        for f in dag.frames:
            for n in f.nodes:
                self.assertNotIn(n.id, seen, f"duplicate qualified id {n.id}")
                seen.add(n.id)

    def test_self_recurse_links_stitched_correctly(self) -> None:
        dag = unroll(self.mas, max_depth=2, fuel=99)
        d = dag.to_dict()
        stitches = {l["stitch"] for l in d["links"]}
        # Basic stitching shapes should appear.
        self.assertIn("self_recurse_in", stitches)
        # Every stitched self_recurse_in points at depth+1 frame's outer_in.
        for l in d["links"]:
            if l["stitch"] == "self_recurse_in":
                self.assertIn("__outer_in__", l["to"]["node"])

    def test_emit_build_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "RecursiveMAS"
            manifest = emit_build_artifacts(out)
            # All listed artifacts exist and digests match.
            for rec in manifest["artifacts"]:
                p = out / rec["path"]
                self.assertTrue(p.exists(), f"missing {p}")
                import hashlib
                got = hashlib.sha256(p.read_bytes()).hexdigest()
                self.assertEqual(got, rec["sha256"])
            # Manifest itself is well-formed JSON.
            json.loads((out / "manifest.json").read_text(encoding="utf-8"))


class JsonSchemaSanityTests(unittest.TestCase):
    """Light sanity checks on the JSON Schema files (parse + key fields).

    We don't depend on a third-party JSON Schema validator; instead we assert
    that the schemas are parseable and pin a couple of structural invariants.
    """

    SCHEMAS = {
        "input": HERE.parent / "inner-links.schema.json",
        "unrolled": HERE.parent / "loop-unrolling.schema.json",
    }

    def test_schemas_are_valid_json(self) -> None:
        for name, p in self.SCHEMAS.items():
            with self.subTest(schema=name):
                obj = json.loads(p.read_text(encoding="utf-8"))
                self.assertIn("$schema", obj)
                self.assertIn("title", obj)

    def test_input_schema_has_self_recurse_kind(self) -> None:
        s = json.loads(self.SCHEMAS["input"].read_text(encoding="utf-8"))
        kinds = s["$defs"]["Node"]["properties"]["kind"]["enum"]
        self.assertIn("self_recurse", kinds)
        self.assertIn("sub_mas", kinds)
        self.assertIn("agent", kinds)

    def test_unrolled_schema_has_termination_reasons(self) -> None:
        s = json.loads(self.SCHEMAS["unrolled"].read_text(encoding="utf-8"))
        # walk into the Frame definition's termination.oneOf[1].properties.reason.enum
        frame = s["$defs"]["Frame"]
        term = frame["properties"]["termination"]["oneOf"][1]
        reasons = term["properties"]["reason"]["enum"]
        self.assertIn("loop.depth_cap_reached", reasons)
        self.assertIn("loop.fuel_exhausted", reasons)
        self.assertIn("loop.fixed_point_reached", reasons)


if __name__ == "__main__":
    unittest.main()
