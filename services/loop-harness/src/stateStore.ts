/**
 * Durable execution-state snapshots.
 *
 * The append-only ledger proves how an execution evolved; this store provides
 * the current materialized state for operators and daemon restarts. Each save
 * replaces one small JSON file under the external volume.
 */

import { mkdirSync, renameSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import type { ExecutionState } from "./types.js";

export class StateStore {
  private readonly dir: string;

  constructor(dir: string) {
    this.dir = dir;
    mkdirSync(dir, { recursive: true });
  }

  save(state: ExecutionState): string {
    const target = join(this.dir, `${state.id}.json`);
    const pending = `${target}.pending`;
    writeFileSync(pending, `${JSON.stringify(state, null, 2)}\n`, "utf8");
    renameSync(pending, target);
    return target;
  }
}

/** A no-op state store for callers that explicitly disable snapshots. */
export class NullStateStore {
  save(_state: ExecutionState): string {
    return "";
  }
}

export type AnyStateStore = StateStore | NullStateStore;
