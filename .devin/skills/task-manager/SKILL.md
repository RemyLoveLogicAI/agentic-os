---
name: task-manager
description: >
  Install and configure the TASK-MANAGER skill for the claw3d hermes GUI.
  Use this skill when tasks need to be captured, tracked on a Kanban board,
  or when the Kanban desk needs to be mounted in the hermes GUI.
---

# TASK-MANAGER Skill — Agent Reference

## When to Use

- The user or an agent needs to capture work items as tasks.
- The Kanban desk needs to be opened or rendered in the claw3d hermes GUI.
- You see the error "Kanban Skill Not Installed" in the UI.
- You encounter "Cannot read properties of undefined (reading 'trim')" related to task data.

## Location

The skill lives at `skills/task-manager/` in the repo root.

## Quick Start

```bash
cd skills/task-manager
bun install   # or npm install
bun run build # compiles TypeScript → dist/
```

## Key Files

| File | Purpose |
|------|---------|
| `src/types.ts` | All type definitions (Task, KanbanBoard, columns) |
| `src/sanitise.ts` | Input sanitisation — prevents `.trim()` on undefined |
| `src/store.ts` | TaskStore — core CRUD + Kanban state |
| `src/evidence.ts` | Evidence emitter for the audit ledger |
| `src/ui/kanban-desk.ts` | KanbanDesk facade for hermes GUI binding |
| `src/index.ts` | Public API barrel export |
| `SKILL.md` | Skill definition and tool contract |

## Integrating with hermes GUI

```ts
import { createTaskStore } from "@agentic-os/task-manager";
import { KanbanDesk } from "@agentic-os/task-manager/ui";

const store = createTaskStore({ persist: "local" });
const desk = new KanbanDesk(store);

// Listen for board changes
desk.onChange((board) => {
  // Re-render the Kanban columns
});

// Create a task
const task = desk.addTask({ title: "Wire approval gate", column: "todo" });

// Move it
desk.moveTask(task.id, "in_progress");
```

## Troubleshooting

### "Cannot read properties of undefined (reading 'trim')"

This error occurs when raw user input reaches `.trim()` without validation.
The `sanitise.ts` module guards every string boundary:

```ts
import { sanitiseString } from "@agentic-os/task-manager";

const safe = sanitiseString(untrustedValue); // never throws on undefined
```

All TaskStore and KanbanDesk methods call `sanitiseString` internally,
so this error should not occur when using the public API.
