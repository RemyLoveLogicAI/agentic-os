#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RecursiveMAS reference implementation.

Inner-link resolution and loop unrolling for the Agentic OS RecursiveMAS
primitive, as defined in `research/docs/recursive-mas-spec.md`.

Pure Python standard library only. CLI entrypoint at the bottom.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

SCHEMA_VERSION_INPUT = "recursive-mas/v0.1"
SCHEMA_VERSION_RESOLVED = "recursive-mas-resolved/v0.1"
SCHEMA_VERSION_UNROLLED = "recursive-mas-unrolled/v0.1"
SCHEMA_VERSION_MANIFEST = "recursive-mas-manifest/v0.1"

NODE_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
MAS_ID_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)*$")
PORT_RE = re.compile(r"^[a-z][a-z0-9_]*$")

OUTER = "*outer*"

DEFAULT_MAX_DEPTH = 4
DEFAULT_FUEL = 64


# --------------------------------------------------------------------------- #
# Errors
# --------------------------------------------------------------------------- #


class RecursiveMasError(Exception):
    """Structured error surfaced by RecursiveMAS validation/unrolling."""

    def __init__(self, code: str, where: str, message: str) -> None:
        super().__init__(f"{code} at {where}: {message}")
        self.code = code
        self.where = where
        self.message = message

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "where": self.where, "message": self.message}


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Ports:
    in_: tuple[str, ...]
    out: tuple[str, ...]

    @staticmethod
    def from_dict(d: Mapping[str, Any], where: str) -> "Ports":
        if not isinstance(d, Mapping):
            raise RecursiveMasError("error.schema.shape", where, "ports must be an object")
        in_ = tuple(d.get("in", ()) or ())
        out = tuple(d.get("out", ()) or ())
        for p in in_ + out:
            if not isinstance(p, str) or not PORT_RE.match(p):
                raise RecursiveMasError("error.schema.shape", where, f"bad port name: {p!r}")
        if len(set(in_)) != len(in_):
            raise RecursiveMasError("error.schema.shape", where, "duplicate ports.in")
        if len(set(out)) != len(out):
            raise RecursiveMasError("error.schema.shape", where, "duplicate ports.out")
        return Ports(in_, out)

    def to_dict(self) -> dict[str, list[str]]:
        return {"in": list(self.in_), "out": list(self.out)}


@dataclass(frozen=True)
class Node:
    id: str
    kind: str  # "agent" | "sub_mas" | "self_recurse"
    ports: Ports
    sub_mas: Optional[str] = None
    capabilities: tuple[str, ...] = ()
    annotations: tuple[tuple[str, Any], ...] = ()  # canonicalized as sorted dict

    @staticmethod
    def from_dict(d: Mapping[str, Any], where: str) -> "Node":
        if not isinstance(d, Mapping):
            raise RecursiveMasError("error.schema.shape", where, "node must be an object")
        nid = d.get("id")
        if not isinstance(nid, str) or not NODE_ID_RE.match(nid):
            raise RecursiveMasError("error.schema.shape", where, f"bad node id: {nid!r}")
        kind = d.get("kind")
        if kind not in ("agent", "sub_mas", "self_recurse"):
            raise RecursiveMasError(
                "error.node.bad_kind", f"{where}/id={nid}", f"unknown kind {kind!r}"
            )
        ports = Ports.from_dict(d.get("ports", {}), f"{where}/id={nid}/ports")
        sub_mas = d.get("sub_mas")
        if kind == "sub_mas":
            if not isinstance(sub_mas, str) or not MAS_ID_RE.match(sub_mas):
                raise RecursiveMasError(
                    "error.schema.shape",
                    f"{where}/id={nid}",
                    f"sub_mas node missing/invalid sub_mas: {sub_mas!r}",
                )
        else:
            if sub_mas is not None:
                raise RecursiveMasError(
                    "error.schema.shape",
                    f"{where}/id={nid}",
                    f"only sub_mas nodes may carry sub_mas; got {sub_mas!r}",
                )
        caps = d.get("capabilities")
        if caps is None:
            caps = []
        if not isinstance(caps, list) or not all(isinstance(c, str) and c for c in caps):
            raise RecursiveMasError(
                "error.schema.shape",
                f"{where}/id={nid}",
                "capabilities must be a list of non-empty strings",
            )
        if len(set(caps)) != len(caps):
            raise RecursiveMasError(
                "error.schema.shape", f"{where}/id={nid}", "duplicate capabilities"
            )
        annotations = d.get("annotations")
        if annotations is None:
            annotations = {}
        if not isinstance(annotations, Mapping):
            raise RecursiveMasError(
                "error.schema.shape", f"{where}/id={nid}", "annotations must be an object"
            )
        ann_t = tuple(sorted(((str(k), v) for k, v in annotations.items()), key=lambda kv: kv[0]))
        return Node(
            id=nid,
            kind=kind,
            ports=ports,
            sub_mas=sub_mas if kind == "sub_mas" else None,
            capabilities=tuple(sorted(caps)),
            annotations=ann_t,
        )

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"id": self.id, "kind": self.kind, "ports": self.ports.to_dict()}
        if self.sub_mas:
            out["sub_mas"] = self.sub_mas
        if self.capabilities:
            out["capabilities"] = list(self.capabilities)
        if self.annotations:
            out["annotations"] = {k: v for k, v in self.annotations}
        return out


@dataclass(frozen=True)
class Endpoint:
    node: str
    port: str

    @staticmethod
    def from_dict(d: Mapping[str, Any], where: str) -> "Endpoint":
        if not isinstance(d, Mapping):
            raise RecursiveMasError("error.schema.shape", where, "endpoint must be an object")
        node = d.get("node")
        port = d.get("port")
        if not isinstance(node, str) or not (node == OUTER or NODE_ID_RE.match(node)):
            raise RecursiveMasError(
                "error.schema.shape", where, f"bad endpoint.node: {node!r}"
            )
        if not isinstance(port, str) or not PORT_RE.match(port):
            raise RecursiveMasError(
                "error.schema.shape", where, f"bad endpoint.port: {port!r}"
            )
        return Endpoint(node, port)

    def to_dict(self) -> dict[str, str]:
        return {"node": self.node, "port": self.port}


@dataclass(frozen=True)
class Link:
    from_: Endpoint
    to: Endpoint
    kind: str = "data"  # "data" | "control" | "evidence"
    guard: Optional[str] = None

    @staticmethod
    def from_dict(d: Mapping[str, Any], where: str) -> "Link":
        if not isinstance(d, Mapping):
            raise RecursiveMasError("error.schema.shape", where, "link must be an object")
        f = Endpoint.from_dict(d.get("from", {}), f"{where}/from")
        t = Endpoint.from_dict(d.get("to", {}), f"{where}/to")
        kind = d.get("kind", "data")
        if kind not in ("data", "control", "evidence"):
            raise RecursiveMasError(
                "error.schema.shape", where, f"bad link.kind: {kind!r}"
            )
        guard = d.get("guard")
        if guard is not None and (not isinstance(guard, str) or not guard):
            raise RecursiveMasError(
                "error.schema.shape", where, f"bad link.guard: {guard!r}"
            )
        return Link(f, t, kind, guard)

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "from": self.from_.to_dict(),
            "to": self.to.to_dict(),
            "kind": self.kind,
        }
        if self.guard is not None:
            out["guard"] = self.guard
        return out

    def sort_key(self) -> tuple[str, str, str, str, str, str]:
        return (
            self.from_.node,
            self.from_.port,
            self.to.node,
            self.to.port,
            self.kind,
            self.guard or "",
        )


@dataclass(frozen=True)
class MasBody:
    mas_id: str
    nodes: tuple[Node, ...]
    links: tuple[Link, ...]
    sub_mas: tuple["MasBody", ...] = ()
    limits: Optional[tuple[int, int]] = None  # (max_depth, fuel) override

    @staticmethod
    def from_dict(d: Mapping[str, Any], where: str, *, allow_self_recurse: bool) -> "MasBody":
        if not isinstance(d, Mapping):
            raise RecursiveMasError("error.schema.shape", where, "MasBody must be an object")
        mas_id = d.get("mas_id")
        if not isinstance(mas_id, str) or not MAS_ID_RE.match(mas_id):
            raise RecursiveMasError("error.schema.shape", where, f"bad mas_id: {mas_id!r}")
        raw_nodes = d.get("nodes", []) or []
        nodes = tuple(
            Node.from_dict(n, f"{where}/nodes[{i}]") for i, n in enumerate(raw_nodes)
        )
        ids: set[str] = set()
        for n in nodes:
            if n.id in ids:
                raise RecursiveMasError(
                    "error.node.id_collision", f"{where}/nodes/id={n.id}", "duplicate node id"
                )
            ids.add(n.id)
            if n.kind == "self_recurse" and not allow_self_recurse:
                raise RecursiveMasError(
                    "error.node.self_recurse_at_root",
                    f"{where}/nodes/id={n.id}",
                    "self_recurse is only allowed inside sub_mas[] bodies",
                )
        raw_links = d.get("links", []) or []
        links = tuple(
            Link.from_dict(l, f"{where}/links[{i}]") for i, l in enumerate(raw_links)
        )
        raw_sub = d.get("sub_mas", []) or []
        sub_mas = tuple(
            MasBody.from_dict(b, f"{where}/sub_mas[{i}]", allow_self_recurse=True)
            for i, b in enumerate(raw_sub)
        )
        seen_sub: set[str] = set()
        for b in sub_mas:
            if b.mas_id in seen_sub:
                raise RecursiveMasError(
                    "error.schema.shape",
                    f"{where}/sub_mas/mas_id={b.mas_id}",
                    "duplicate sub_mas mas_id within scope",
                )
            seen_sub.add(b.mas_id)
        limits = None
        raw_limits = d.get("limits")
        if raw_limits is not None:
            md = raw_limits.get("max_depth", DEFAULT_MAX_DEPTH)
            fl = raw_limits.get("fuel", DEFAULT_FUEL)
            if not isinstance(md, int) or md < 0:
                raise RecursiveMasError(
                    "error.budget.invalid", f"{where}/limits/max_depth", f"got {md!r}"
                )
            if not isinstance(fl, int) or fl < 0:
                raise RecursiveMasError(
                    "error.budget.invalid", f"{where}/limits/fuel", f"got {fl!r}"
                )
            limits = (md, fl)
        return MasBody(mas_id=mas_id, nodes=nodes, links=links, sub_mas=sub_mas, limits=limits)

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "mas_id": self.mas_id,
            "nodes": [n.to_dict() for n in sorted(self.nodes, key=lambda n: n.id)],
            "links": [l.to_dict() for l in sorted(self.links, key=lambda l: l.sort_key())],
        }
        if self.sub_mas:
            out["sub_mas"] = [b.to_dict() for b in sorted(self.sub_mas, key=lambda b: b.mas_id)]
        if self.limits is not None:
            out["limits"] = {"max_depth": self.limits[0], "fuel": self.limits[1]}
        return out


@dataclass(frozen=True)
class Mas:
    schema_version: str
    root: MasBody

    @staticmethod
    def from_dict(d: Mapping[str, Any]) -> "Mas":
        if not isinstance(d, Mapping):
            raise RecursiveMasError("error.schema.shape", "/", "MAS spec must be an object")
        sv = d.get("schema_version")
        if sv != SCHEMA_VERSION_INPUT:
            raise RecursiveMasError(
                "error.schema.unknown_version", "/schema_version", f"got {sv!r}"
            )
        body = MasBody.from_dict(d, "/", allow_self_recurse=False)
        return Mas(schema_version=sv, root=body)

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"schema_version": self.schema_version}
        out.update(self.root.to_dict())
        return out


# --------------------------------------------------------------------------- #
# Canonical JSON & digesting
# --------------------------------------------------------------------------- #


def _canon_replace(s: str) -> str:
    return s.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def canonical_json(value: Any) -> str:
    """Deterministic JSON encoding suitable for sha256 hashing.

    Approximates RFC 8785 (JCS) for the value shapes used by RecursiveMAS:
    sorted object keys, no extraneous whitespace, ensure_ascii=False, and
    explicit U+2028/U+2029 escaping. See research/docs/canonical-json-spec.md.
    """
    s = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return _canon_replace(s)


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# Inner-link resolution
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ResolvedLink:
    from_: Endpoint
    to: Endpoint
    kind: str
    guard: Optional[str]
    capabilities: tuple[str, ...]
    shape: str  # "outer_in" | "outer_out" | "inner_to_inner" | "inner_to_self"

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "from": self.from_.to_dict(),
            "to": self.to.to_dict(),
            "kind": self.kind,
            "shape": self.shape,
        }
        if self.guard is not None:
            out["guard"] = self.guard
        if self.capabilities:
            out["capabilities"] = list(self.capabilities)
        return out


@dataclass(frozen=True)
class ResolvedBody:
    mas_id: str
    outer_in_ports: tuple[str, ...]
    outer_out_ports: tuple[str, ...]
    links: tuple[ResolvedLink, ...]
    sub_bodies: tuple["ResolvedBody", ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mas_id": self.mas_id,
            "outer_in_ports": list(self.outer_in_ports),
            "outer_out_ports": list(self.outer_out_ports),
            "links": [l.to_dict() for l in self.links],
            "sub_bodies": [b.to_dict() for b in self.sub_bodies],
        }


@dataclass(frozen=True)
class ResolvedInnerLinks:
    schema_version: str
    source_digest: str
    root: ResolvedBody

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "source_digest": self.source_digest,
            "root": self.root.to_dict(),
        }


def _node_index(body: MasBody) -> dict[str, Node]:
    return {n.id: n for n in body.nodes}


def _check_no_unguarded_cycle(body: MasBody, where: str) -> None:
    """Reject cycles in `links` that don't pass through a self_recurse node."""
    by_id = _node_index(body)
    self_ids = {n.id for n in body.nodes if n.kind == "self_recurse"}
    adj: dict[str, set[str]] = {n.id: set() for n in body.nodes}
    for l in body.links:
        if l.from_.node == OUTER or l.to.node == OUTER:
            continue
        if l.from_.node in self_ids or l.to.node in self_ids:
            continue
        if l.from_.node not in by_id or l.to.node not in by_id:
            continue
        adj[l.from_.node].add(l.to.node)
    color: dict[str, int] = {}  # 0 unseen, 1 stack, 2 done

    def dfs(u: str) -> None:
        color[u] = 1
        for v in adj.get(u, ()):
            c = color.get(v, 0)
            if c == 1:
                raise RecursiveMasError(
                    "error.loop.unguarded_cycle",
                    f"{where}/cycle/{u}->{v}",
                    "cycle without a self_recurse boundary",
                )
            if c == 0:
                dfs(v)
        color[u] = 2

    for n in body.nodes:
        if color.get(n.id, 0) == 0:
            dfs(n.id)


def _outer_surface(body: MasBody, enclosing: Optional[Node]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if enclosing is not None:
        return tuple(sorted(enclosing.ports.in_)), tuple(sorted(enclosing.ports.out))
    in_, out = set(), set()
    for l in body.links:
        if l.from_.node == OUTER:
            in_.add(l.from_.port)
        if l.to.node == OUTER:
            out.add(l.to.port)
    return tuple(sorted(in_)), tuple(sorted(out))


def _resolve_body(
    body: MasBody, *, enclosing_sub_mas_node: Optional[Node], where: str
) -> ResolvedBody:
    """Validate inner-link grammar and produce a ResolvedBody."""
    by_id = _node_index(body)
    outer_in_ports, outer_out_ports = _outer_surface(body, enclosing_sub_mas_node)
    outer_in_set = set(outer_in_ports)
    outer_out_set = set(outer_out_ports)

    # Subset constraint for self_recurse nodes:
    # self_recurse.ports.in ⊆ outer_in surface, .out ⊆ outer_out surface.
    for n in body.nodes:
        if n.kind == "self_recurse":
            for p in n.ports.in_:
                if p not in outer_in_set:
                    raise RecursiveMasError(
                        "error.sub_mas.boundary_mismatch",
                        f"{where}/nodes/id={n.id}/ports/in",
                        f"self_recurse port {p!r} not in body's outer-in surface "
                        f"({sorted(outer_in_set)})",
                    )
            for p in n.ports.out:
                if p not in outer_out_set:
                    raise RecursiveMasError(
                        "error.sub_mas.boundary_mismatch",
                        f"{where}/nodes/id={n.id}/ports/out",
                        f"self_recurse port {p!r} not in body's outer-out surface "
                        f"({sorted(outer_out_set)})",
                    )

    resolved_links: list[ResolvedLink] = []
    for i, l in enumerate(body.links):
        loc = f"{where}/links[{i}]"
        f, t = l.from_, l.to
        if f.node == OUTER and t.node == OUTER:
            raise RecursiveMasError(
                "error.inner_link.shape_invalid", loc, "outer→outer link is not allowed"
            )
        if f.node == OUTER:
            tgt = by_id.get(t.node)
            if tgt is None:
                raise RecursiveMasError(
                    "error.inner_link.shape_invalid", loc, f"unknown to.node: {t.node!r}"
                )
            if f.port not in outer_in_set:
                raise RecursiveMasError(
                    "error.sub_mas.boundary_mismatch",
                    loc,
                    f"outer-in port {f.port!r} not declared on enclosing sub_mas surface",
                )
            if t.port not in tgt.ports.in_:
                raise RecursiveMasError(
                    "error.inner_link.port_unknown", loc, f"to.port {t.port!r} not in {t.node}.ports.in"
                )
            shape = "outer_in"
            caps = tgt.capabilities
        elif t.node == OUTER:
            src = by_id.get(f.node)
            if src is None:
                raise RecursiveMasError(
                    "error.inner_link.shape_invalid", loc, f"unknown from.node: {f.node!r}"
                )
            if t.port not in outer_out_set:
                raise RecursiveMasError(
                    "error.sub_mas.boundary_mismatch",
                    loc,
                    f"outer-out port {t.port!r} not declared on enclosing sub_mas surface",
                )
            if f.port not in src.ports.out:
                raise RecursiveMasError(
                    "error.inner_link.port_unknown", loc, f"from.port {f.port!r} not in {f.node}.ports.out"
                )
            shape = "outer_out"
            caps = src.capabilities
        else:
            src = by_id.get(f.node)
            tgt = by_id.get(t.node)
            if src is None or tgt is None:
                raise RecursiveMasError(
                    "error.inner_link.shape_invalid",
                    loc,
                    f"unknown endpoint(s): from.node={f.node!r}, to.node={t.node!r}",
                )
            if f.port not in src.ports.out:
                raise RecursiveMasError(
                    "error.inner_link.port_unknown", loc, f"from.port {f.port!r} not in {f.node}.ports.out"
                )
            if t.port not in tgt.ports.in_:
                raise RecursiveMasError(
                    "error.inner_link.port_unknown", loc, f"to.port {t.port!r} not in {t.node}.ports.in"
                )
            shape = "inner_to_self" if tgt.kind == "self_recurse" else "inner_to_inner"
            caps = tuple(sorted(set(src.capabilities) | set(tgt.capabilities)))
        resolved_links.append(
            ResolvedLink(
                from_=f, to=t, kind=l.kind, guard=l.guard, capabilities=caps, shape=shape
            )
        )

    sub_resolved: list[ResolvedBody] = []
    sub_index = {b.mas_id: b for b in body.sub_mas}
    for sub in body.sub_mas:
        encl: Optional[Node] = None
        for n in body.nodes:
            if n.kind == "sub_mas" and n.sub_mas == sub.mas_id:
                encl = n
                break
        sub_resolved.append(
            _resolve_body(sub, enclosing_sub_mas_node=encl, where=f"{where}/sub_mas/{sub.mas_id}")
        )

    for n in body.nodes:
        if n.kind == "sub_mas" and n.sub_mas not in sub_index:
            raise RecursiveMasError(
                "error.sub_mas.unknown",
                f"{where}/nodes/id={n.id}",
                f"sub_mas {n.sub_mas!r} not declared in this body's sub_mas[]",
            )

    _check_no_unguarded_cycle(body, where)

    return ResolvedBody(
        mas_id=body.mas_id,
        outer_in_ports=outer_in_ports,
        outer_out_ports=outer_out_ports,
        links=tuple(
            sorted(
                resolved_links,
                key=lambda r: (r.from_.node, r.from_.port, r.to.node, r.to.port, r.kind, r.guard or ""),
            )
        ),
        sub_bodies=tuple(sorted(sub_resolved, key=lambda b: b.mas_id)),
    )


def resolve_inner_links(mas: Mas) -> ResolvedInnerLinks:
    """Validate every inner link in the MAS and return a normalized record."""
    src_dig = digest(mas.to_dict())
    root_resolved = _resolve_body(mas.root, enclosing_sub_mas_node=None, where="")
    return ResolvedInnerLinks(
        schema_version=SCHEMA_VERSION_RESOLVED,
        source_digest=src_dig,
        root=root_resolved,
    )


def load_mas(spec: Mapping[str, Any]) -> Mas:
    """Parse and validate a raw mas_spec dict; returns a Mas."""
    return Mas.from_dict(spec)


# --------------------------------------------------------------------------- #
# Loop unrolling
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class UnrolledNode:
    id: str
    kind: str  # "agent" | "depth_cap" | "fuel_exhausted" | "fixed_point"
    ports: Ports
    capabilities: tuple[str, ...] = ()
    annotations: tuple[tuple[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"id": self.id, "kind": self.kind, "ports": self.ports.to_dict()}
        if self.capabilities:
            out["capabilities"] = list(self.capabilities)
        if self.annotations:
            out["annotations"] = {k: v for k, v in self.annotations}
        return out


@dataclass(frozen=True)
class UnrolledLink:
    from_: Endpoint
    to: Endpoint
    kind: str
    stitch: str  # "none" | "self_recurse_in" | "self_recurse_out" | "outer_in" | "outer_out"
    guard: Optional[str] = None
    capabilities: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "from": self.from_.to_dict(),
            "to": self.to.to_dict(),
            "kind": self.kind,
            "stitch": self.stitch,
        }
        if self.guard is not None:
            out["guard"] = self.guard
        if self.capabilities:
            out["capabilities"] = list(self.capabilities)
        return out

    def sort_key(self) -> tuple[str, ...]:
        return (
            self.from_.node,
            self.from_.port,
            self.to.node,
            self.to.port,
            self.kind,
            self.stitch,
            self.guard or "",
        )


@dataclass(frozen=True)
class Frame:
    frame_id: str
    mas_id: str
    depth: int
    nodes: tuple[UnrolledNode, ...]
    termination: Optional[dict[str, str]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "mas_id": self.mas_id,
            "depth": self.depth,
            "nodes": [n.to_dict() for n in sorted(self.nodes, key=lambda n: n.id)],
            "termination": self.termination,
        }


@dataclass(frozen=True)
class UnrolledDag:
    schema_version: str
    source_digest: str
    limits: tuple[int, int]
    frames: tuple[Frame, ...]
    links: tuple[UnrolledLink, ...]
    evidence: tuple[dict[str, str], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "source_digest": self.source_digest,
            "limits": {"max_depth": self.limits[0], "fuel": self.limits[1]},
            "frames": [f.to_dict() for f in sorted(self.frames, key=lambda f: (f.mas_id, f.depth))],
            "links": [l.to_dict() for l in sorted(self.links, key=lambda l: l.sort_key())],
            "evidence": [
                e for e in sorted(self.evidence, key=lambda e: (e["frame_id"], e["kind"]))
            ],
        }


def _frame_id(parent_path: str, mas_id: str, depth: int) -> str:
    """Globally-unique frame id.

    Format:
      <mas_id>#<depth>                                   (root frame, no parent)
      <parent_frame_id>::<mas_id>#<depth>                (nested or recursive frame)

    For self-recursion the parent_path is the *enclosing* sub-MAS frame id
    (i.e. unchanged across self-recursion of the same body), so depths
    increment but the lexical prefix stays put. For non-recursive sub-MAS
    descent the parent_path is the calling frame's id, which guarantees that
    two cousin scopes that happen to share a `mas_id` get distinct frame ids.
    """
    base = f"{mas_id}#{depth}"
    if not parent_path:
        return base
    return f"{parent_path}::{base}"


def _qual(frame_id: str, node_id: str) -> str:
    return f"{frame_id}::{node_id}"


def _outer_in_id(frame_id: str) -> str:
    return _qual(frame_id, "__outer_in__")


def _outer_out_id(frame_id: str) -> str:
    return _qual(frame_id, "__outer_out__")


def _cap_id(frame_id: str) -> str:
    return _qual(frame_id, "__cap__")


@dataclass
class _UnrollState:
    fuel: int
    max_depth: int
    fixed_point: bool
    frames: list[Frame] = field(default_factory=list)
    links: list[UnrolledLink] = field(default_factory=list)
    evidence: list[dict[str, str]] = field(default_factory=list)
    # Fixed-point key: (parent_path, mas_id) → canonical body bytes.
    canon_by_scope: dict[tuple[str, str], str] = field(default_factory=dict)


def _virtual_outer(frame_id: str, in_ports: Sequence[str], out_ports: Sequence[str]) -> tuple[UnrolledNode, UnrolledNode]:
    oi = UnrolledNode(
        id=_outer_in_id(frame_id),
        kind="agent",
        ports=Ports(in_=tuple(in_ports), out=tuple(in_ports)),
        annotations=(("virtual", "outer_in"),),
    )
    oo = UnrolledNode(
        id=_outer_out_id(frame_id),
        kind="agent",
        ports=Ports(in_=tuple(out_ports), out=tuple(out_ports)),
        annotations=(("virtual", "outer_out"),),
    )
    return oi, oo


def _emit_cap_frame(
    *,
    body: MasBody,
    state: _UnrollState,
    depth: int,
    parent_path: str,
    outer_in_ports: tuple[str, ...],
    outer_out_ports: tuple[str, ...],
    reason: str,
    kind: str,
) -> str:
    fid = _frame_id(parent_path, body.mas_id, depth)
    cap_node = UnrolledNode(
        id=_cap_id(fid),
        kind=kind,
        ports=Ports(in_=outer_in_ports, out=()),
        annotations=(("reason", reason),),
    )
    oi, oo = _virtual_outer(fid, outer_in_ports, outer_out_ports)
    state.frames.append(
        Frame(
            frame_id=fid,
            mas_id=body.mas_id,
            depth=depth,
            nodes=(cap_node, oi, oo),
            termination={"reason": reason, "node_id": cap_node.id},
        )
    )
    state.evidence.append({"kind": reason, "frame_id": fid})
    for p in outer_in_ports:
        state.links.append(
            UnrolledLink(
                from_=Endpoint(oi.id, p),
                to=Endpoint(cap_node.id, p),
                kind="control",
                stitch="outer_in",
            )
        )
    return fid


def _unroll_body(
    body: MasBody,
    *,
    state: _UnrollState,
    depth: int,
    parent_path: str,
    enclosing_sub_mas_node: Optional[Node],
    sub_lookup: dict[str, MasBody],
) -> str:
    """Unroll a single MasBody at depth `depth`. Returns the frame_id created.

    `parent_path` is the lexical chain of enclosing sub-MAS frame ids; it
    guarantees that two cousin scopes that share a `mas_id` get globally
    distinct frame ids. Self-recursion preserves `parent_path` (the recursive
    call lives in the same lexical position) and only bumps `depth`.

    Mutates `state` to append nodes/links/frames/evidence.
    """
    outer_in_ports, outer_out_ports = _outer_surface(body, enclosing_sub_mas_node)

    # Cap conditions
    if depth > state.max_depth:
        return _emit_cap_frame(
            body=body, state=state, depth=depth, parent_path=parent_path,
            outer_in_ports=outer_in_ports, outer_out_ports=outer_out_ports,
            reason="loop.depth_cap_reached", kind="depth_cap",
        )
    if state.fuel <= 0:
        return _emit_cap_frame(
            body=body, state=state, depth=depth, parent_path=parent_path,
            outer_in_ports=outer_in_ports, outer_out_ports=outer_out_ports,
            reason="loop.fuel_exhausted", kind="fuel_exhausted",
        )

    state.fuel -= 1

    # Detect a fixed-point: same body at the same lexical scope, byte-identical,
    # already seen at a lower depth. Keying by (parent_path, mas_id) prevents
    # two cousin scopes that share a mas_id from confusing each other.
    body_canon = canonical_json(body.to_dict())
    scope_key = (parent_path, body.mas_id)
    if state.fixed_point and depth >= 1:
        prior = state.canon_by_scope.get(scope_key)
        if prior is not None and prior == body_canon:
            return _emit_cap_frame(
                body=body, state=state, depth=depth, parent_path=parent_path,
                outer_in_ports=outer_in_ports, outer_out_ports=outer_out_ports,
                reason="loop.fixed_point_reached", kind="fixed_point",
            )
    state.canon_by_scope[scope_key] = body_canon

    # Local scope: merge sub_lookup with this body's sub_mas[] (lexical inner shadows outer).
    local_lookup = dict(sub_lookup)
    for sb in body.sub_mas:
        local_lookup[sb.mas_id] = sb

    fid = _frame_id(parent_path, body.mas_id, depth)

    # Emit boundary virtual nodes for this frame.
    oi, oo = _virtual_outer(fid, outer_in_ports, outer_out_ports)
    frame_nodes: list[UnrolledNode] = [oi, oo]

    sub_frame_id_by_node: dict[str, str] = {}
    self_frame_id_by_node: dict[str, str] = {}
    for n in body.nodes:
        if n.kind == "agent":
            frame_nodes.append(
                UnrolledNode(
                    id=_qual(fid, n.id),
                    kind="agent",
                    ports=n.ports,
                    capabilities=n.capabilities,
                    annotations=n.annotations,
                )
            )
        elif n.kind == "sub_mas":
            child_body = local_lookup.get(n.sub_mas or "")
            if child_body is None:
                raise RecursiveMasError(
                    "error.sub_mas.unknown",
                    f"{body.mas_id}/nodes/id={n.id}",
                    f"sub_mas {n.sub_mas!r} not in scope",
                )
            child_fid = _unroll_body(
                child_body,
                state=state,
                depth=0,
                parent_path=f"{fid}::{n.id}",
                enclosing_sub_mas_node=n,
                sub_lookup=local_lookup,
            )
            sub_frame_id_by_node[n.id] = child_fid
        elif n.kind == "self_recurse":
            # Self-recursion stays inside the same lexical position, so it
            # MUST inherit the enclosing sub-MAS node (and therefore the
            # advertised outer port surface). Falling back to None here would
            # let `_outer_surface` infer a smaller surface from `*outer*`
            # references in `body.links`, dropping any advertised-but-unused
            # ports and producing incorrect DAG stitching.
            child_fid = _unroll_body(
                body,
                state=state,
                depth=depth + 1,
                parent_path=parent_path,
                enclosing_sub_mas_node=enclosing_sub_mas_node,
                sub_lookup=local_lookup,
            )
            self_frame_id_by_node[n.id] = child_fid
        else:  # pragma: no cover - validated upstream
            raise RecursiveMasError(
                "error.node.bad_kind", f"{body.mas_id}/nodes/id={n.id}", n.kind
            )

    state.frames.append(
        Frame(
            frame_id=fid, mas_id=body.mas_id, depth=depth,
            nodes=tuple(frame_nodes), termination=None,
        )
    )

    # Second pass: rewrite links using the qualified ids and stitch boundaries.
    by_id = _node_index(body)
    self_frame_fid = _frame_id(parent_path, body.mas_id, depth + 1)
    for l in body.links:
        f, t = l.from_, l.to
        src_caps: set[str] = set()
        tgt_caps: set[str] = set()

        if f.node == OUTER:
            from_node_id = _outer_in_id(fid)
            from_port = f.port
            stitch_in = "outer_in"
        else:
            src = by_id[f.node]
            src_caps = set(src.capabilities)
            if src.kind == "self_recurse":
                from_node_id = _outer_out_id(self_frame_fid)
                from_port = f.port
                stitch_in = "self_recurse_out"
            elif src.kind == "sub_mas":
                child_fid = sub_frame_id_by_node[src.id]
                from_node_id = _outer_out_id(child_fid)
                from_port = f.port
                stitch_in = "outer_out"
            else:
                from_node_id = _qual(fid, src.id)
                from_port = f.port
                stitch_in = "none"

        if t.node == OUTER:
            to_node_id = _outer_out_id(fid)
            to_port = t.port
            stitch_out = "outer_out"
        else:
            tgt = by_id[t.node]
            tgt_caps = set(tgt.capabilities)
            if tgt.kind == "self_recurse":
                to_node_id = _outer_in_id(self_frame_fid)
                to_port = t.port
                stitch_out = "self_recurse_in"
            elif tgt.kind == "sub_mas":
                child_fid = sub_frame_id_by_node[tgt.id]
                to_node_id = _outer_in_id(child_fid)
                to_port = t.port
                stitch_out = "outer_in"
            else:
                to_node_id = _qual(fid, tgt.id)
                to_port = t.port
                stitch_out = "none"

        if stitch_in != "none" and stitch_out == "none":
            stitch = stitch_in
        elif stitch_out != "none" and stitch_in == "none":
            stitch = stitch_out
        elif stitch_in == "none" and stitch_out == "none":
            stitch = "none"
        else:
            stitch = stitch_out

        caps = tuple(sorted(src_caps | tgt_caps))
        state.links.append(
            UnrolledLink(
                from_=Endpoint(from_node_id, from_port),
                to=Endpoint(to_node_id, to_port),
                kind=l.kind,
                stitch=stitch,
                guard=l.guard,
                capabilities=caps,
            )
        )

    return fid


def unroll(
    mas: Mas,
    *,
    max_depth: Optional[int] = None,
    fuel: Optional[int] = None,
    detect_fixed_point: bool = True,
) -> UnrolledDag:
    """Produce a deterministic unrolled DAG from a validated MAS.

    `max_depth` and `fuel` override the spec's `limits` if provided.
    """
    # Validate up front so unrolling never silently masks invalid inner links.
    resolve_inner_links(mas)

    md = max_depth if max_depth is not None else (mas.root.limits[0] if mas.root.limits else DEFAULT_MAX_DEPTH)
    fl = fuel if fuel is not None else (mas.root.limits[1] if mas.root.limits else DEFAULT_FUEL)
    if md < 0 or fl < 0:
        raise RecursiveMasError("error.budget.invalid", "/limits", f"max_depth={md}, fuel={fl}")

    state = _UnrollState(fuel=fl, max_depth=md, fixed_point=detect_fixed_point)
    _unroll_body(
        mas.root,
        state=state,
        depth=0,
        parent_path="",
        enclosing_sub_mas_node=None,
        sub_lookup={},
    )
    return UnrolledDag(
        schema_version=SCHEMA_VERSION_UNROLLED,
        source_digest=digest(mas.to_dict()),
        limits=(md, fl),
        frames=tuple(state.frames),
        links=tuple(state.links),
        evidence=tuple(state.evidence),
    )


# --------------------------------------------------------------------------- #
# Build artifacts
# --------------------------------------------------------------------------- #


def example_mas_spec() -> dict[str, Any]:
    """Canonical example used to populate build-artifacts/RecursiveMAS/."""
    return {
        "schema_version": SCHEMA_VERSION_INPUT,
        "mas_id": "outer.root",
        "limits": {"max_depth": 3, "fuel": 8},
        "nodes": [
            {
                "id": "ingest",
                "kind": "agent",
                "ports": {"in": ["request"], "out": ["parsed"]},
                "capabilities": ["voice.read"],
            },
            {
                "id": "plan",
                "kind": "agent",
                "ports": {"in": ["parsed"], "out": ["plan"]},
                "capabilities": ["plan.write"],
            },
            {
                "id": "exec",
                "kind": "sub_mas",
                "sub_mas": "outer.exec_loop",
                "ports": {"in": ["plan"], "out": ["report"]},
            },
            {
                "id": "publish",
                "kind": "agent",
                "ports": {"in": ["report"], "out": ["receipt"]},
                "capabilities": ["evidence.write"],
            },
        ],
        "links": [
            {
                "from": {"node": "*outer*", "port": "request"},
                "to": {"node": "ingest", "port": "request"},
            },
            {
                "from": {"node": "ingest", "port": "parsed"},
                "to": {"node": "plan", "port": "parsed"},
            },
            {
                "from": {"node": "plan", "port": "plan"},
                "to": {"node": "exec", "port": "plan"},
            },
            {
                "from": {"node": "exec", "port": "report"},
                "to": {"node": "publish", "port": "report"},
            },
            {
                "from": {"node": "publish", "port": "receipt"},
                "to": {"node": "*outer*", "port": "receipt"},
            },
        ],
        "sub_mas": [
            {
                "mas_id": "outer.exec_loop",
                "nodes": [
                    {
                        "id": "act",
                        "kind": "agent",
                        "ports": {"in": ["plan"], "out": ["evidence", "next_plan"]},
                        "capabilities": ["exec.run"],
                    },
                    {
                        "id": "verify",
                        "kind": "agent",
                        "ports": {"in": ["evidence", "next_plan"], "out": ["pass", "retry"]},
                        "capabilities": ["evidence.read"],
                    },
                    {
                        "id": "loop",
                        "kind": "self_recurse",
                        "ports": {"in": ["plan"], "out": ["report"]},
                    },
                ],
                "links": [
                    {
                        "from": {"node": "*outer*", "port": "plan"},
                        "to": {"node": "act", "port": "plan"},
                    },
                    {
                        "from": {"node": "act", "port": "evidence"},
                        "to": {"node": "verify", "port": "evidence"},
                    },
                    {
                        "from": {"node": "act", "port": "next_plan"},
                        "to": {"node": "verify", "port": "next_plan"},
                    },
                    {
                        "from": {"node": "verify", "port": "pass"},
                        "to": {"node": "*outer*", "port": "report"},
                    },
                    {
                        "from": {"node": "verify", "port": "retry"},
                        "to": {"node": "loop", "port": "plan"},
                        "guard": "retry",
                    },
                    {
                        "from": {"node": "loop", "port": "report"},
                        "to": {"node": "*outer*", "port": "report"},
                    },
                ],
            }
        ],
    }


def emit_build_artifacts(out_dir: Path) -> dict[str, Any]:
    """Emit the canonical build artifacts under `out_dir`. Returns the manifest."""
    out_dir.mkdir(parents=True, exist_ok=True)
    spec_dict = example_mas_spec()
    mas = load_mas(spec_dict)
    resolved = resolve_inner_links(mas)
    dag = unroll(mas, detect_fixed_point=True)

    files = {
        "example.mas.json": canonical_json(mas.to_dict()),
        "inner-links.example.json": canonical_json(resolved.to_dict()),
        "loop-unrolling.example.json": canonical_json(dag.to_dict()),
    }
    artifact_records: list[dict[str, Any]] = []
    for name, body in sorted(files.items()):
        b = body.encode("utf-8")
        (out_dir / name).write_bytes(b)
        artifact_records.append(
            {
                "path": name,
                "sha256": hashlib.sha256(b).hexdigest(),
                "bytes": len(b),
            }
        )

    manifest = {
        "schema_version": SCHEMA_VERSION_MANIFEST,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_digest": digest(mas.to_dict()),
        "limits": {"max_depth": dag.limits[0], "fuel": dag.limits[1]},
        "artifacts": artifact_records,
    }
    (out_dir / "manifest.json").write_bytes(canonical_json(manifest).encode("utf-8"))
    return manifest


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _cmd_validate(args: argparse.Namespace) -> int:
    spec = _load_json(Path(args.input))
    mas = load_mas(spec)
    resolved = resolve_inner_links(mas)
    sys.stdout.write(canonical_json(resolved.to_dict()) + "\n")
    return 0


def _cmd_unroll(args: argparse.Namespace) -> int:
    spec = _load_json(Path(args.input))
    mas = load_mas(spec)
    dag = unroll(
        mas,
        max_depth=args.max_depth,
        fuel=args.fuel,
        detect_fixed_point=not args.no_fixed_point,
    )
    sys.stdout.write(canonical_json(dag.to_dict()) + "\n")
    return 0


def _cmd_emit(args: argparse.Namespace) -> int:
    out_dir = Path(args.emit_build_artifacts)
    manifest = emit_build_artifacts(out_dir)
    if args.also_mirror:
        mirror = Path(args.also_mirror)
        mirror.mkdir(parents=True, exist_ok=True)
        for f in out_dir.iterdir():
            if f.is_file():
                (mirror / f.name).write_bytes(f.read_bytes())
        (mirror / "manifest.json").write_bytes(
            (out_dir / "manifest.json").read_bytes()
        )
    sys.stdout.write(canonical_json(manifest) + "\n")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="recursive_mas",
        description="RecursiveMAS reference: validate inner links and unroll loops.",
    )
    sub = p.add_subparsers(dest="cmd")

    v = sub.add_parser("validate", help="resolve inner links of a mas_spec JSON file")
    v.add_argument("input")
    v.set_defaults(func=_cmd_validate)

    u = sub.add_parser("unroll", help="unroll a mas_spec JSON file into a DAG")
    u.add_argument("input")
    u.add_argument("--max-depth", type=int, default=None)
    u.add_argument("--fuel", type=int, default=None)
    u.add_argument("--no-fixed-point", action="store_true")
    u.set_defaults(func=_cmd_unroll)

    e = sub.add_parser(
        "emit", help="emit canonical build artifacts under the given directory"
    )
    e.add_argument("--emit-build-artifacts", required=True, dest="emit_build_artifacts")
    e.add_argument(
        "--also-mirror",
        default=None,
        help="also copy artifacts to this directory (e.g. /home/workdir/artifacts/RecursiveMAS)",
    )
    e.set_defaults(func=_cmd_emit)

    args = p.parse_args(argv)
    if args.cmd is None:
        p.print_help()
        return 2
    try:
        return int(args.func(args))
    except RecursiveMasError as err:
        sys.stderr.write(canonical_json(err.to_dict()) + "\n")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
