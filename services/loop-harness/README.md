# Loop Harness

A local daemon/worker harness that drives software from **CURRENT STATE** to a testable **IDEAL STATE** through a bounded recursive execution loop.

It maps Remy's systems directly:

| Source primitive | Harness implementation |
|---|---|
| PAI `OBSERVE → THINK → PLAN` | `Planner(state) → Plan`, with the objective and all prior failures |
| PAI `BUILD → EXECUTE` | Apply the plan, run repair commands, then run `buildCommand` |
| PAI `VERIFY` | Run `verifyCommand`; only exit code `0` is success |
| PAI `LEARN → next OBSERVE` | Capture stdout/stderr/exit code as `ErrorRecord[]` and recurse |
| Arbol **Action** | Each plan/build/verify phase is a single-purpose action |
| Arbol **Pipeline** | Phase output passes the accumulated `ExecutionState` downstream |
| Arbol **Flow Loop Gate** | Failed verification re-enters the pipeline, capped by `maxIterations` |
| RecursiveMAS safety | `maxDepth`, shared `fuel`, and fixed-point rejection |

References:

- [PAI Algorithm 6.3.0](https://github.com/RemyLoveLogicAI/Personal_AI_Infrastructure/blob/main/Releases/v5.0.0/.claude/PAI/ALGORITHM/v6.3.0.md)
- [Arbol System](https://github.com/RemyLoveLogicAI/Personal_AI_Infrastructure/blob/main/Releases/v5.0.0/.claude/PAI/DOCUMENTATION/Arbol/ArbolSystem.md)
- [RecursiveMAS bounded recursion specification](https://github.com/RemyLoveLogicAI/agentic-os/pull/18)

## Storage hygiene

All build work is staged under the external share; source files are never built in place.

Default root:

```text
/Volumes/SAMSUNG SSD/LOCAL_SHARE
├── cache/      package-manager caches
├── npm/        npm/bun install prefix
├── tmp/        staged workspaces and daemon queues
├── state/      latest execution-state snapshots
├── ledgers/    append-only JSONL evidence
└── dist/       verified distributions
```

Every child command receives `npm_config_cache`, `npm_config_prefix`, `BUN_INSTALL_CACHE_DIR`, `BUN_INSTALL`, `TMPDIR`, `TEMP`, `TMP`, and `YARN_CACHE_FOLDER` pointing under that root.

For CI or a container mock, set `LOOP_HARNESS_SHARE_ROOT` to another absolute path. Production defaults to the mandated path.

## Install and build

Keep the dependency install itself on the external volume:

```bash
TOOLCHAIN="/Volumes/SAMSUNG SSD/LOCAL_SHARE/npm/loop-harness-toolchain"
npm_config_cache="/Volumes/SAMSUNG SSD/LOCAL_SHARE/cache" \
TMPDIR="/Volumes/SAMSUNG SSD/LOCAL_SHARE/tmp" \
npm install --prefix "$TOOLCHAIN" typescript@5.8.3 @types/node@20.17.30

cd services/loop-harness
PATH="$TOOLCHAIN/node_modules/.bin:$PATH" npm run build
```

No `node_modules` directory is created in the repository. TypeScript output goes
to `/Volumes/SAMSUNG SSD/LOCAL_SHARE/tmp/loop-harness/package-dist` unless
`LOOP_HARNESS_BUILD_DIR` points to another path under the share.

## Project job

A daemon job is declarative JSON:

```json
{
  "objective": "Compile the worker and pass its deterministic tests",
  "source": "/absolute/path/to/source",
  "buildCommand": "npm run build",
  "verifyCommand": "npm test",
  "distFiles": ["dist", "package.json"],
  "repairs": {
    "missing_dependencies": ["npm install"],
    "syntax_error": ["./scripts/repair-syntax.sh"],
    "test_failure": ["./scripts/repair-tests.sh"]
  },
  "maxIterations": 8,
  "maxDepth": 8,
  "fuel": 40,
  "commandTimeoutMs": 120000
}
```

The first iteration builds as-is to observe the actual failure. On failure, the next planner invocation receives the complete `ExecutionState`, including compiler/runtime output. The declarative planner selects `repairs[latest.signature]`. Library users can provide a custom `Planner` callback that edits code via `Plan.apply`.

`ExecutionState` persists the objective, `currentCode.workspace` plus its content
digest, accumulated errors, per-phase evidence, and iteration count after every
transition.

## One-shot run

```bash
bun run src/cli.ts run /path/to/project.json
```

The process exits `0` only when verification exits `0` and the distribution has been published to:

```text
/Volumes/SAMSUNG SSD/LOCAL_SHARE/dist/<execution-id>/
```

No distribution directory is created for a failed execution.

## Daemon

```bash
# Terminal 1
bun run src/cli.ts daemon

# Terminal 2
bun run src/cli.ts submit /path/to/project.json
```

Daemon queue layout:

```text
tmp/loop-harness/daemon/
├── inbox/       submitted jobs
├── processing/  atomically claimed jobs
├── completed/   final successful ExecutionState JSON
└── failed/      bounded failure state or daemon error
```

`SIGINT` and `SIGTERM` stop the daemon cleanly after the active command returns. A killed daemon leaves a claimed job in `processing/` rather than silently losing it.

## Failure semantics

- Build failures skip verification and recurse with captured evidence.
- Verification failures recurse with captured evidence.
- Unknown/unrepairable errors terminate as `no_plan`.
- Missing or unsafe declared artifacts terminate as `distribution_failed`.
- Identical code plus identical open error signatures on consecutive iterations terminate as `fixed_point`.
- Iteration, recursion-depth, and fuel limits independently bound execution.
- Distribution is gated exclusively on verification exit code `0`.
