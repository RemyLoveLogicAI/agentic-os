/**
 * Core type definitions for the TASK-MANAGER skill.
 *
 * All string fields are validated at the boundary via {@link sanitiseString}
 * so callers never hit "Cannot read properties of undefined (reading 'trim')".
 */

// ── Column & Status ─────────────────────────────────────────────────

export const KANBAN_COLUMNS = [
  "backlog",
  "todo",
  "in_progress",
  "review",
  "done",
  "blocked",
] as const;

export type KanbanColumn = (typeof KANBAN_COLUMNS)[number];

// ── Task ────────────────────────────────────────────────────────────

export interface Task {
  id: string;
  title: string;
  description: string;
  column: KanbanColumn;
  assignee: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface TaskCreateInput {
  title: string;
  description?: string;
  column?: KanbanColumn;
  assignee?: string;
  tags?: string[];
}

export interface TaskUpdateInput {
  title?: string;
  description?: string;
  column?: KanbanColumn;
  assignee?: string;
  tags?: string[];
}

export interface TaskMoveInput {
  id: string;
  toColumn: KanbanColumn;
}

export interface TaskListFilter {
  column?: KanbanColumn;
  assignee?: string;
}

// ── Board ───────────────────────────────────────────────────────────

export type KanbanBoard = Record<KanbanColumn, Task[]>;

// ── Evidence ────────────────────────────────────────────────────────

export interface TaskEvent {
  event: string;
  taskId: string;
  from?: KanbanColumn;
  to?: KanbanColumn;
  actor: string;
  timestamp: string;
  detail?: Record<string, unknown>;
}

// ── Persistence ─────────────────────────────────────────────────────

export type PersistMode = "rip" | "local";

export interface TaskStoreOptions {
  persist?: PersistMode;
  ledgerPath?: string;
}
