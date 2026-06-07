/**
 * Evidence emitter for task state transitions.
 *
 * Each mutation emits a {@link TaskEvent} that can be appended to the
 * Agentic OS Evidence Ledger for auditability.
 *
 * NOTE: The listener pool is module-level (singleton).  All TaskStore
 * instances in the same process share the same event bus.  This is
 * intentional for the single-board hermes GUI use-case.  For multi-board
 * or test scenarios, use {@link removeAllListeners} between instances.
 */

import type { TaskEvent, TaskEventType, KanbanColumn } from "./types.js";

export type EvidenceListener = (event: TaskEvent) => void;

const listeners: EvidenceListener[] = [];

/**
 * Subscribe to all task evidence events.
 * Returns an unsubscribe function.
 */
export function onTaskEvent(fn: EvidenceListener): () => void {
  listeners.push(fn);
  return () => {
    const idx = listeners.indexOf(fn);
    if (idx !== -1) listeners.splice(idx, 1);
  };
}

/**
 * Remove all registered evidence listeners.
 * Useful for test teardown or multi-board scenarios.
 */
export function removeAllListeners(): void {
  listeners.length = 0;
}

/**
 * Emit a task evidence event to all registered listeners.
 */
export function emitTaskEvent(
  event: TaskEventType,
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
