---
name: task-manager
description: >
  Kanban-style task management skill for Agentic OS.
  Lets agents capture work as tasks, move them across Kanban columns,
  and surface a Kanban desk inside the claw3d hermes GUI.
version: "0.1.0"
layer: orchestration-mesh
depends:
  - packages/core
  - packages/memory
tags:
  - kanban
  - task-manager
  - claw3d
  - hermes-gui
---

# TASK-MANAGER Skill

## Purpose

Provides a Kanban task board that agents can use to:

1. **Create tasks** from voice commands, API calls, or agent actions.
2. **Move tasks** across columns (`backlog` | `todo` | `in_progress` | `review` | `done` | `blocked`).
3. **Query the board** to see what is active, blocked, or completed.
4. **Persist state** through the R.I.P. canonical memory layer or a local JSON ledger.

## Integration — claw3d hermes GUI

The skill exposes a `KanbanDesk` component and a `TaskStore` API that the
claw3d hermes GUI can mount. The hermes GUI renders the board; the skill
owns the data model and state transitions.

### Mounting

```ts
import { createTaskStore } from "@agentic-os/task-manager";
import { KanbanDesk } from "@agentic-os/task-manager/ui";

const store = createTaskStore({ persist: "rip" }); // or "local"
// Render <KanbanDesk store={store} /> in the hermes GUI shell.
```

## Tool Contract

| Tool                   | Input                              | Output           |
|------------------------|------------------------------------|------------------|
| `task_create`          | `{ title, column?, assignee? }`    | `Task`           |
| `task_move`            | `{ id, toColumn }`                 | `Task`           |
| `task_update`          | `{ id, patch }`                    | `Task`           |
| `task_delete`          | `{ id }`                           | `void`           |
| `task_list`            | `{ column?, assignee? }`           | `Task[]`         |
| `kanban_snapshot`      | `{}`                               | `KanbanBoard`    |

## Columns

| Column        | Meaning                                      |
|---------------|----------------------------------------------|
| `backlog`     | Captured but not yet prioritised              |
| `todo`        | Ready to start                                |
| `in_progress` | Actively being worked on                      |
| `review`      | Awaiting verification or approval             |
| `done`        | Completed and verified                        |
| `blocked`     | Cannot proceed — requires external resolution |

## Evidence

Every state transition emits an evidence record to the Evidence Ledger:

```json
{
  "event": "task_moved",
  "taskId": "tsk_abc123",
  "from": "todo",
  "to": "in_progress",
  "actor": "agent:orchestrator",
  "timestamp": "2026-05-19T15:00:00Z"
}
```
