/**
 * Evidence emitter for task state transitions.
 *
 * Each mutation emits a {@link TaskEvent} that can be appended to the
 * Agentic OS Evidence Ledger for auditability.
 */

import type { TaskEvent, KanbanColumn } from "./types.js";

export type EvidenceListener = (event: TaskEvent) => void;

const listeners: EvidenceListener[] = [];

export function onTaskEvent(fn: EvidenceListener): () => void {
  listeners.push(fn);
  return () => {
    const idx = listeners.indexOf(fn);
    if (idx !== -1) listeners.splice(idx, 1);
  };
}

export function emitTaskEvent(
  event: string,
  taskId: string,
  actor: string,
  opts?: { from?: KanbanColumn; to?: KanbanColumn; detail?: Record<string, unknown> },
): void {
  const record: TaskEvent = {
    event,
    taskId,
    actor,
    timestamp: new Date().toISOString(),
    ...(opts?.from !== undefined && { from: opts.from }),
    ...(opts?.to !== undefined && { to: opts.to }),
    ...(opts?.detail !== undefined && { detail: opts.detail }),
  };
  for (const fn of listeners) {
    try {
      fn(record);
    } catch {
      // Listeners must not break the pipeline.
    }
  }
}
