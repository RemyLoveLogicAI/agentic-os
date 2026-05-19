/**
 * KanbanDesk — the UI-facing facade for the claw3d hermes GUI.
 *
 * This module provides a framework-agnostic data model that the hermes
 * GUI renderer can bind to.  It wraps a {@link TaskStore} and exposes
 * reactive-friendly accessors.
 *
 * The hermes GUI is responsible for the actual DOM rendering; this layer
 * ensures every value is pre-sanitised so the renderer never encounters
 * `undefined.trim()` or similar null-reference errors.
 */

import type {
  Task,
  TaskCreateInput,
  KanbanBoard,
  KanbanColumn,
  TaskListFilter,
} from "../types.js";
import { KANBAN_COLUMNS } from "../types.js";
import { sanitiseString } from "../sanitise.js";
import { TaskStore } from "../store.js";

export type BoardChangeListener = (board: KanbanBoard) => void;

export class KanbanDesk {
  private store: TaskStore;
  private listeners: BoardChangeListener[] = [];

  constructor(store: TaskStore) {
    this.store = store;
  }

  // ── Reactive helpers ────────────────────────────────────────────

  onChange(fn: BoardChangeListener): () => void {
    this.listeners.push(fn);
    return () => {
      const idx = this.listeners.indexOf(fn);
      if (idx !== -1) this.listeners.splice(idx, 1);
    };
  }

  private notify(): void {
    const board = this.store.snapshot();
    for (const fn of this.listeners) {
      try {
        fn(board);
      } catch {
        // Listener errors must not break the desk.
      }
    }
  }

  // ── Column metadata ─────────────────────────────────────────────

  get columns(): readonly KanbanColumn[] {
    return KANBAN_COLUMNS;
  }

  columnLabel(col: KanbanColumn): string {
    const labels: Record<KanbanColumn, string> = {
      backlog: "Backlog",
      todo: "To Do",
      in_progress: "In Progress",
      review: "Review",
      done: "Done",
      blocked: "Blocked",
    };
    return labels[col] ?? sanitiseString(col);
  }

  // ── Delegated operations ────────────────────────────────────────

  addTask(input: TaskCreateInput): Task {
    const task = this.store.create(input);
    this.notify();
    return task;
  }

  moveTask(id: string, toColumn: KanbanColumn): Task {
    const task = this.store.move({ id, toColumn });
    this.notify();
    return task;
  }

  removeTask(id: string): boolean {
    const ok = this.store.delete(id);
    if (ok) this.notify();
    return ok;
  }

  getBoard(): KanbanBoard {
    return this.store.snapshot();
  }

  getTasks(filter?: TaskListFilter): Task[] {
    return this.store.list(filter);
  }

  getTask(id: string): Task | undefined {
    return this.store.get(id);
  }

  get taskCount(): number {
    return this.store.size;
  }
}
