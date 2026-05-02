# RecursiveMAS — build artifacts

This directory holds the canonical, deterministic artifacts produced by the
RecursiveMAS reference implementation for the example MAS defined in
`research/docs/recursive-mas/reference/recursive_mas.py::example_mas_spec()`.

It is the in-repo mirror of the issue-#16 sync target
`/home/workspace/RemyLoveLogicAI/agentic-os/build-artifacts/RecursiveMAS/`.

| File | Purpose |
|---|---|
| `example.mas.json` | The input `mas_spec` (canonical JSON). |
| `inner-links.example.json` | The fully-resolved inner-link table for the example, as produced by `resolve_inner_links()`. |
| `loop-unrolling.example.json` | The unrolled DAG for the example under `max_depth=3, fuel=8`, with fixed-point detection enabled. |
| `manifest.json` | sha256 digests, byte sizes, and `source_digest` for the three artifacts above. |

All three artifact files are byte-deterministic: regenerating them from a
clean checkout produces identical bytes. The manifest is deterministic
modulo its `generated_at` timestamp, which is informational only and
excluded from any digest the manifest itself participates in.

## Reproducing

From the repo root:

```bash
python3 research/docs/recursive-mas/reference/recursive_mas.py \
    emit \
    --emit-build-artifacts build-artifacts/RecursiveMAS \
    --also-mirror /home/workdir/artifacts/RecursiveMAS
```

The `--also-mirror` flag duplicates the artifacts to the Devin-container
output path expected by issue #16.

## Validating

Both schemas in `research/docs/recursive-mas/` are JSON-Schema-2020-12
documents. To validate the example artifacts against them:

```bash
python3 - <<'PY'
import json, jsonschema
from pathlib import Path
root = Path(".")
input_schema    = json.loads((root/"research/docs/recursive-mas/inner-links.schema.json").read_text())
unrolled_schema = json.loads((root/"research/docs/recursive-mas/loop-unrolling.schema.json").read_text())
example_mas     = json.loads((root/"build-artifacts/RecursiveMAS/example.mas.json").read_text())
unrolled        = json.loads((root/"build-artifacts/RecursiveMAS/loop-unrolling.example.json").read_text())
jsonschema.validate(example_mas, input_schema)
jsonschema.validate(unrolled,    unrolled_schema)
print("OK")
PY
```

(`jsonschema` is the only optional dependency; the reference implementation
and its tests are pure stdlib.)
