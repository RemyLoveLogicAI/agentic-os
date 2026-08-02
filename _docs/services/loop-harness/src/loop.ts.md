<!-- METADATA: {"source_path": "services/loop-harness/src/loop.ts", "source_sha": "", "extraction_quality": "regex_fallback", "model": "gpt-5-mini", "generated_at": "2026-07-18T20:50:57Z", "doc_type": "file"} -->
<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "services/loop-harness/src/loop.ts",
  "source_hash": "da926318cae6399d2369558135d09958ca58bf36573aace7b72f2b41a33ab391",
  "last_updated": "2026-07-18T20:50:57.822805+00:00",
  "tokens_used": 2373,
  "complexity_score": 2,
  "estimated_review_time_minutes": 11,
  "external_dependencies": [
    "import { randomUUID } from \"node:crypto\";",
    "import { join } from \"node:path\";",
    "import type { ExecutionState, Project, LoopConfig } from \"./types.js\";",
    "import { DEFAULT_LOOP_CONFIG } from \"./types.js\";",
    "import type { StoragePaths } from \"./storage.js\";",
    "import type { AnyLedger } from \"./ledger.js\";",
    "import { Ledger } from \"./ledger.js\";",
    "import { ensureStorage } from \"./storage.js\";",
    "import { digestWorkspace } from \"./digest.js\";",
    "import { stageWorkspace } from \"./staging.js\";",
    "import { publishDistribution } from \"./distribution.js\";",
    "import { planPhase, buildPhase, verifyPhase, type PhaseDeps } from \"./phases.js\";",
    "import { StateStore, type AnyStateStore } from \"./stateStore.js\";",
    "import {"
  ]
}
```

</details>

[Documentation Home](../../../README.md) > [services](../../README.md) > [loop-harness](../README.md) > [src](./README.md) > **loop**

---

# loop.ts

> **File:** `services/loop-harness/src/loop.ts`

![Complexity: Low](https://img.shields.io/badge/Complexity-Low-green) ![Review Time: 11min](https://img.shields.io/badge/Review_Time-11min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This TypeScript module ties together several pieces of a loop-harness system by importing utilities for workspace digesting, staging, distribution, storage, and ledger management, and by exposing a small set of top-level helper functions. The file does not declare classes but provides four module-level functions (progressKey, resolveConfig, logLastPhase, logCaptured) that appear intended to coordinate configuration resolution, progress tracking keys, and logging of phase or captured results. The module relies on typed imports for ExecutionState, Project, LoopConfig, and StoragePaths and wires in a default loop configuration as well as phase-specific functions (planPhase, buildPhase, verifyPhase).

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `import { randomUUID } from "node:crypto";` | import { randomUUID } from "node:crypto"; |
| `import { join } from "node:path";` | import { join } from "node:path"; |
| `import type { ExecutionState, Project, LoopConfig } from "./types.js";` | import type { ExecutionState, Project, LoopConfig } from "./types.js"; |
| `import { DEFAULT_LOOP_CONFIG } from "./types.js";` | import { DEFAULT_LOOP_CONFIG } from "./types.js"; |
| `import type { StoragePaths } from "./storage.js";` | import type { StoragePaths } from "./storage.js"; |
| `import type { AnyLedger } from "./ledger.js";` | import type { AnyLedger } from "./ledger.js"; |
| `import { Ledger } from "./ledger.js";` | import { Ledger } from "./ledger.js"; |
| `import { ensureStorage } from "./storage.js";` | import { ensureStorage } from "./storage.js"; |
| `import { digestWorkspace } from "./digest.js";` | import { digestWorkspace } from "./digest.js"; |
| `import { stageWorkspace } from "./staging.js";` | import { stageWorkspace } from "./staging.js"; |
| `import { publishDistribution } from "./distribution.js";` | import { publishDistribution } from "./distribution.js"; |
| `import { planPhase, buildPhase, verifyPhase, type PhaseDeps } from "./phases.js";` | import { planPhase, buildPhase, verifyPhase, type PhaseDeps } from "./phases.js"; |
| `import { StateStore, type AnyStateStore } from "./stateStore.js";` | import { StateStore, type AnyStateStore } from "./stateStore.js"; |
| `import {` | import { |

## 📁 Directory

This file is part of the **src** directory. View the [directory index](_docs/services/loop-harness/src/README.md) to see all files in this module.

## Architecture Notes

- Composes functionality by importing small focused modules (digest, staging, distribution, storage, ledger, phases).
- Uses typed imports to express domain types (ExecutionState, Project, LoopConfig, StoragePaths, AnyLedger).
- Relies on Node standard library utilities (node:crypto randomUUID and node:path join) for identifiers and path manipulation.
- Implements a small set of module-level helper functions rather than classes.
- Documentation generated from regex-based extraction for TypeScript; class/function detection is best-effort.

## Maintenance Notes

- Generate or derive a stable progress key for an execution using progressKey.
- Resolve and normalize loop configuration values via resolveConfig, using DEFAULT_LOOP_CONFIG as a baseline.
- Log the most recent phase outcome using logLastPhase to report phase-level progress or state.
- Log captured outputs or artifacts with logCaptured to surface results produced by the loop.

---

## Navigation

**↑ Parent Directory:** [Go up](_docs/services/loop-harness/src/README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*


---

## Functions and Classes


#### progressKey

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```typescript
def progressKey(state):
```

### Description

Compute and return a key that represents the current progress derived from the provided state object.

Compute and return a key that represents the current progress derived from the provided state object. This key is intended for identifying or indexing progress within the loop harness logic.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Unknown` | ✅ | Parameter state |

### Complexity

Not analyzed

---



#### resolveConfig

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```typescript
def resolveConfig(input?):
```

### Description

Resolves and produces the final, normalized runtime configuration for the loop harness.

Resolves and produces the final, normalized runtime configuration for the loop harness. It takes any provided partial or override input, merges it with defaults, and returns the resolved configuration ready for use.


input? is an optional parameter that can supply a partial configuration or overrides; when omitted the function will produce a configuration based solely on built-in defaults and environment-derived values.

Returns the fully resolved configuration object with defaults applied and overrides merged in.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `input?` | `Unknown` | ✅ | Parameter input? |

### Complexity

Not analyzed

---



#### logLastPhase

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```typescript
def logLastPhase(ledger, state):
```

### Description

Logs information about the most recent phase of the loop using the provided ledger and current state.

Logs information about the most recent phase of the loop using the provided ledger and current state. It collects or formats relevant details from the ledger and state and emits them to the configured logging/output mechanism.


Returns nothing (void); its purpose is side-effect logging rather than producing a value.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `ledger` | `Unknown` | ✅ | Parameter ledger |
| `state` | `Unknown` | ✅ | Parameter state |

### Complexity

Not analyzed

---



#### logCaptured

![Type: Sync](https://img.shields.io/badge/Type-Sync-green)

### Signature

```typescript
def logCaptured(ledger, state):
```

### Description

Logs information about items that have been captured from a ledger within the loop harness, using the provided ledger and the current state to produce diagnostic or audit output.

Logs information about items that have been captured from a ledger within the loop harness, using the provided ledger and the current state to produce diagnostic or audit output. It coordinates the recording or printing of captured data so the loop can report what was observed or processed.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `ledger` | `Unknown` | ✅ | Parameter ledger |
| `state` | `Unknown` | ✅ | Parameter state |

### Complexity

Not analyzed

---


