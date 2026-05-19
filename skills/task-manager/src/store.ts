/**
 * TaskStore — the core state container for the TASK-MANAGER skill.
 *
 * Maintains an in-memory list of tasks, validates all input through the
 * sanitisation layer, and emits evidence events on every mutation.
 */

import type {
  Task,
  TaskCreateInput,
  TaskUpdateInput,
  TaskMoveInput,
  TaskListFilter,
  KanbanBoard,
  KanbanColumn,
  TaskStoreOptions,
} from "./types.js";
import { KANBAN_COLUMNS } from "./types.js";
import { sanitiseString, sanitiseOptionalString, sanitiseStringArray } from "./sanitise.js";
import { generateTaskId } from "./id.js";
import { emitTaskEvent } from "./evidence.js";

function isValidColumn(col: string): col is KanbanColumn {
  return (KANBAN_COLUMNS as readonly string[]).includes(col);
}

function now(): string {
  return new Date().toISOString();
}

export class TaskStore {
  private tasks: Map<string, Task> = new Map();
  private actor: string;

  constructor(opts?: TaskStoreOptions) {
    this.actor = "agent:task-manager";
    // Persistence mode is recorded but storage adapters are plugged in
    // at a higher layer (R.I.P. sync or local JSON ledger).
    void opts;
  }

  // ── Create ──────────────────────────────────────────────────────

  create(input: TaskCreateInput): Task {
    const title = sanitiseString(input.title);
    if (title.length === 0) {
      throw new Error("task_create: title is required and must be a non-empty string");
    }

    const column = sanitiseString(input.column, "backlog");
    if (!isValidColumn(column)) {
      throw new Error(`task_create: invalid column "${column}"`);
    }

    const id = generateTaskId();
    const ts = now();

    const task: Task = {
      id,
      title,
      description: sanitiseString(input.description),
      column,
      assignee: sanitiseString(input.assignee),
      tags: sanitiseStringArray(input.tags),
      createdAt: ts,
      updatedAt: ts,
    };

    this.tasks.set(id, task);
    emitTaskEvent("task_created", id, this.actor, { to: task.column });
    return { ...task };
  }

  // ── Read ────────────────────────────────────────────────────────

  get(id: string): Task | undefined {
    const taskId = sanitiseString(id);
    const task = this.tasks.get(taskId);
    return task ? { ...task } : undefined;
  }

  list(filter?: TaskListFilter): Task[] {
    let result = Array.from(this.tasks.values());

    if (filter?.column !== undefined) {
      const col = sanitiseString(filter.column);
      if (col.length > 0) {
        result = result.filter((t) => t.column === col);
      }
    }

    if (filter?.assignee !== undefined) {
      const assignee = sanitiseString(filter.assignee);
      if (assignee.length > 0) {
        result = result.filter((t) => t.assignee === assignee);
      }
    }

    return result.map((t) => ({ ...t }));
  }

  snapshot(): KanbanBoard {
    const board: KanbanBoard = {
      backlog: [],
      todo: [],
      in_progress: [],
      review: [],
      done: [],
      blocked: [],
    };
    for (const task of this.tasks.values()) {
      board[task.column].push({ ...task });
    }
    return board;
  }

  // ── Update ──────────────────────────────────────────────────────

  update(id: string, patch: TaskUpdateInput): Task {
    const taskId = sanitiseString(id);
    const existing = this.tasks.get(taskId);
    if (!existing) {
      throw new Error(`task_update: no task found with id "${taskId}"`);
    }

    const updatedTitle = sanitiseOptionalString(patch.title);
    const updatedDesc = sanitiseOptionalString(patch.description);
    const updatedAssignee = sanitiseOptionalString(patch.assignee);
    const updatedTags = patch.tags !== undefined ? sanitiseStringArray(patch.tags) : undefined;

    let updatedColumn: KanbanColumn | undefined;
    if (patch.column !== undefined) {
      const col = sanitiseString(patch.column);
      if (!isValidColumn(col)) {
        throw new Error(`task_update: invalid column "${col}"`);
      }
      updatedColumn = col;
    }

    const updated: Task = {
      ...existing,
      ...(updatedTitle !== undefined && { title: updatedTitle }),
      ...(updatedDesc !== undefined && { description: updatedDesc }),
      ...(updatedColumn !== undefined && { column: updatedColumn }),
      ...(updatedAssignee !== undefined && { assignee: updatedAssignee }),
      ...(updatedTags !== undefined && { tags: updatedTags }),
      updatedAt: now(),
    };

    this.tasks.set(taskId, updated);

    emitTaskEvent("task_updated", taskId, this.actor, {
      from: existing.column,
      to: updated.column,
    });

    return { ...updated };
  }

  // ── Move ────────────────────────────────────────────────────────

  move(input: TaskMoveInput): Task {
    const taskId = sanitiseString(input.id);
    const toColumn = sanitiseString(input.toColumn);

    if (!isValidColumn(toColumn)) {
      throw new Error(`task_move: invalid column "${toColumn}"`);
    }

    const existing = this.tasks.get(taskId);
    if (!existing) {
      throw new Error(`task_move: no task found with id "${taskId}"`);
    }

    const fromColumn = existing.column;
    const moved: Task = {
      ...existing,
      column: toColumn,
      updatedAt: now(),
    };

    this.tasks.set(taskId, moved);
    emitTaskEvent("task_moved", taskId, this.actor, { from: fromColumn, to: toColumn });
    return { ...moved };
  }

  // ── Delete ──────────────────────────────────────────────────────

  delete(id: string): boolean {
    const taskId = sanitiseString(id);
    const existing = this.tasks.get(taskId);
    if (!existing) return false;
    this.tasks.delete(taskId);
    emitTaskEvent("task_deleted", taskId, this.actor, { from: existing.column });
    return true;
  }

  // ── Utilities ───────────────────────────────────────────────────

  get size(): number {
    return this.tasks.size;
  }

  clear(): void {
    this.tasks.clear();
  }
}

/**
 * Factory function used by the hermes GUI integration.
 */
export function createTaskStore(opts?: TaskStoreOptions): TaskStore {
  return new TaskStore(opts);
}
