/**
 * Append-only JSONL evidence ledger.
 *
 * Realises Agentic OS's "No Proof, No Claim" doctrine for the harness: every
 * phase, failure, and distribution is written as one JSON line to a physical
 * file on the external volume, so a run is auditable after the fact.
 */

import { appendFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";

export type LedgerEventType =
  | "execution.started"
  | "phase.completed"
  | "error.captured"
  | "iteration.advanced"
  | "distribution.published"
  | "execution.terminated";

export interface LedgerEvent {
  type: LedgerEventType;
  executionId: string;
  iteration: number;
  at: string;
  detail: Record<string, unknown>;
}

export class Ledger {
  private readonly path: string;

  constructor(path: string) {
    this.path = path;
    mkdirSync(dirname(path), { recursive: true });
  }

  append(event: Omit<LedgerEvent, "at">): void {
    const record: LedgerEvent = { ...event, at: new Date().toISOString() };
    appendFileSync(this.path, `${JSON.stringify(record)}\n`, "utf8");
  }

  get file(): string {
    return this.path;
  }
}

/** A no-op ledger for tests or callers that don't want persistence. */
export class NullLedger {
  append(_event: Omit<LedgerEvent, "at">): void {
    /* intentionally empty */
  }
  get file(): string {
    return "";
  }
}

export type AnyLedger = Ledger | NullLedger;
