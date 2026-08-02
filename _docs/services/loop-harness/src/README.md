<details><summary>Directory Metadata (for smart change detection)</summary>

```json
{
  "doc_type": "directory_index",
  "directory_path": "_docs/services/loop-harness/src",
  "directory_hash": "d179614a8359c8b66175aecc01dc5094a6985520cb67938bdd32dcba8451b01b",
  "file_count": 16,
  "file_hashes": {
    "classify.ts": "3e7c03ac4fb195b2",
    "cli.ts": "f4bd94d19e137223",
    "config.ts": "ed36f5dcb963cc40",
    "daemon.ts": "1918516a3f9082ed",
    "digest.ts": "a512302d2d15d15b",
    "distribution.ts": "54b90e6863e4389b",
    "exec.ts": "120124370b1b2469",
    "index.ts": "fb7fc3215a9495a2",
    "ledger.ts": "da3c4954b41f1792",
    "loop.ts": "d478c3ddce2a9bdc",
    "phases.ts": "5d193445b6087358",
    "staging.ts": "70d402cc55daac9c",
    "state.ts": "d077fac8f330452b",
    "stateStore.ts": "6a21b6be047dd5fe",
    "storage.ts": "8703405290261e3e",
    "types.ts": "5cc9b4d4f4707bcd"
  }
}
```

</details>

[Documentation Home](../../../README.md) > [services](../../README.md) > [loop-harness](../README.md) > [src](./README.md) > **src**

---

# 📁 src

> **Purpose:** TypeScript implementation and public API surface for the loop-harness service, including filesystem-backed utilities, lifecycle helpers, and a CLI/daemon entry points.
> 

![Organization: Flat](https://img.shields.io/badge/Organization-Flat-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [All Files](#all-files)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)

---

## Overview

This directory implements the loop-harness service in TypeScript. At the root level it contains modules that provide core type definitions (types.ts), configuration handling (config.ts), time/phase utilities (phases.ts, state.ts), filesystem helpers for storage, staging, distribution and ledger management (storage.ts, staging.ts, distribution.ts, ledger.ts), digesting and workspace walking utilities (digest.ts), execution and subprocess-related helpers (exec.ts), and higher-level orchestrators that tie these pieces together (loop.ts, daemon.ts). There is also a public API barrel (index.ts) that re-exports functionality for consumers, a small CLI orchestration layer (cli.ts), and classification/type dependency utilities (classify.ts). Each file purpose is focused and narrowly scoped according to the filenames and descriptions listed in the module index.

Taken together these modules form a cohesive local loop harness: low-level filesystem primitives (storage, ledger, staging) support digesting and distribution tasks; execution and state/store modules (exec.ts, stateStore.ts, state.ts) provide mechanisms for running and persisting execution state; loop.ts composes these utilities into a small set of top-level helper functions; daemon.ts and cli.ts provide runtime entry points for background or command-driven use. index.ts exposes a single import surface so other packages or applications can consume the harness functionality from one location. This directory is therefore the implementation and entry surface for driving a software objective from current to ideal state within the larger system.


### File Organization

Files are organized by responsibility rather than nested feature folders: type definitions, configuration, low-level filesystem utilities, execution/state management, composition helpers, and public entry points are all at the directory root so that related modules can import each other directly and the public barrel (index.ts) can re-export them from one place.

## 📂 All Files

| File | Type |
| --- | --- |
| [classify.ts](./classify.ts.md) | 📘 TypeScript |
| [cli.ts](./cli.ts.md) | 📘 TypeScript |
| [config.ts](./config.ts.md) | 📘 TypeScript |
| [daemon.ts](./daemon.ts.md) | 📘 TypeScript |
| [digest.ts](./digest.ts.md) | 📘 TypeScript |
| [distribution.ts](./distribution.ts.md) | 📘 TypeScript |
| [exec.ts](./exec.ts.md) | 📘 TypeScript |
| [index.ts](./index.ts.md) | 📘 TypeScript |
| [ledger.ts](./ledger.ts.md) | 📘 TypeScript |
| [loop.ts](./loop.ts.md) | 📘 TypeScript |
| [phases.ts](./phases.ts.md) | 📘 TypeScript |
| [staging.ts](./staging.ts.md) | 📘 TypeScript |
| [state.ts](./state.ts.md) | 📘 TypeScript |
| [stateStore.ts](./stateStore.ts.md) | 📘 TypeScript |
| [storage.ts](./storage.ts.md) | 📘 TypeScript |
| [types.ts](./types.ts.md) | 📘 TypeScript |

## Dependencies

### Internal Dependencies

| Dependency | Usage |
| --- | --- |
| [local module exports (re-exports via index.ts)](../local module exports (re-exports via index/ts).md) | index.ts re-exports internal modules in this directory to form the package public API consumed by other packages. |

## Architecture Notes

- A single directory-level public barrel (index.ts) centralizes exports so consumers import from one place.
- Low-level filesystem primitives (storage, ledger, staging, distribution) are separated from orchestration/composition (loop.ts, daemon.ts) to keep responsibilities clear.
- Types are centralized in types.ts to drive consistent type-level dependencies across modules.

---

## Navigation

**↑ Parent Directory:** [Go up](../README.md)

---

*Generated by Woden Docbot*