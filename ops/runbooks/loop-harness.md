# Loop Harness Operations

## Start

```bash
cd services/loop-harness
bun run src/cli.ts daemon
```

The daemon prints its external-volume inbox path on startup. Submit work with `bun run src/cli.ts submit <project.json>`.

## Inspect

```bash
bun run src/cli.ts paths
```

For execution `<id>`:

- current state: `/Volumes/SAMSUNG SSD/LOCAL_SHARE/state/<id>.json`
- evidence: `/Volumes/SAMSUNG SSD/LOCAL_SHARE/ledgers/<id>.jsonl`
- staged source: `/Volumes/SAMSUNG SSD/LOCAL_SHARE/tmp/loop-harness/executions/<id>/workspace`
- successful artifact: `/Volumes/SAMSUNG SSD/LOCAL_SHARE/dist/<id>`

Treat a distribution as valid only when its state says `status: "succeeded"`, `termination: "verified"`, and its `manifest.json` exists.

## Recover

Jobs in `processing/` were claimed before a daemon interruption. Inspect their state and ledger; to retry from clean source, move the original job JSON back to `inbox/` under a new filename. The new execution stages a fresh workspace and cannot blend with the interrupted build.

## Stop

Send `SIGINT` or `SIGTERM`. The daemon stops polling after the active command returns. Per-command timeout is controlled by `commandTimeoutMs` in the job.
