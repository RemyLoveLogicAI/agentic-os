/**
 * @agentic-os/task-manager
 *
 * Kanban task management skill for the claw3d hermes GUI.
 *
 * @example
 * ```ts
 * import { createTaskStore, KanbanDesk } from "@agentic-os/task-manager";
 *
 * const store = createTaskStore({ persist: "local" });
 * const desk  = new KanbanDesk(store);
 *
 * const task = desk.addTask({ title: "Wire approval gate" });
 * desk.moveTask(task.id, "in_progress");
 *
 * console.log(desk.getBoard());
 * ```
 */

// Core store
export { TaskStore, createTaskStore } from "./store.js";

// UI facade
export { KanbanDesk } from "./ui/kanban-desk.js";

// Evidence
export { onTaskEvent, emitTaskEvent } from "./evidence.js";

// Sanitisation utilities (useful for downstream consumers)
export { sanitiseString, sanitiseOptionalString, sanitiseStringArray } from "./sanitise.js";

// Types
export type {
  Task,
  TaskCreateInput,
  TaskUpdateInput,
  TaskMoveInput,
  TaskListFilter,
  KanbanBoard,
  KanbanColumn,
  TaskEvent,
  TaskStoreOptions,
  PersistMode,
} from "./types.js";

export { KANBAN_COLUMNS } from "./types.js";
