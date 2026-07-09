# Agentic OS

A voice-native, governed runtime for autonomous agents. Agentic OS closes the execution gap between "the model said something" and "the system actually did something" — with an audit trail to prove it.

## What it does

- **Voice in** — Speak a command. The system transcribes and routes it.
- **Deterministic routing** — A rule-based intent classifier sends the command to the right handler without LLM drift.
- **Approval gating** — Risky actions pause for human approval with a TTL.
- **Substrate-bound execution** — Actions hit real APIs, desktops, and services.
- **Evidence ledger** — Every command, route, approval, and action is logged to SQLite and JSONL.

## The "No Proof, No Claim" Doctrine

1. **Functional Substrate** — The only canonical state is physical SQLite and JSONL audit trails.
2. **ZeroLang Consensus** — Type-safe, multi-persona consensus grading for every mission.
3. **Synthesis-Augmented Intelligence (SAI)** — Local model fine-tuning via the Dream Machine.

## Architecture

```
Voice / Dictation / Shortcut / Agent
              │
              ▼
       Deterministic Router
              │
              ▼
      Approval Gate (TTL)
              │
              ▼
    Execution Adapters (desktop, API, agent)
              │
              ▼
       Evidence Ledger (SQLite + JSONL)
```

## Status

Agentic OS is the integrating flagship for LoveLogicAI. The current proof slice is the `CAR Kernel` (Command-Action-Replay) under `src/metropolis/car-kernel/`, plus the `TASK-MANAGER` skill for the claw3d hermes GUI under `skills/task-manager/`.

See [ROADMAP.md](ROADMAP.md) for the full phased plan.

## Quick start

```bash
# Install dependencies
npm install

# Build the task-manager skill
cd skills/task-manager
bun install
bun run build

# Run the CAR kernel example
cd ../..
npm run example:car
```

## Components

| Component | Path | Purpose |
|-----------|------|---------|
| `CARKernel` | `src/metropolis/car-kernel/kernel.ts` | Command in, events out, state updated |
| `CAROrchestrator` | `src/metropolis/car-kernel/orchestrator.ts` | Dispatch loop and adapter wiring |
| `EventStore` | `src/metropolis/car-kernel/eventStore.ts` | Append-only event log |
| `ToolRouter` | `src/metropolis/car-kernel/toolRouter.ts` | Maps command names to handlers |
| `State` | `src/metropolis/car-kernel/state.ts` | State reducer and replay |
| `TASK-MANAGER` | `skills/task-manager/` | Kanban task store and hermes GUI desk |

## Example

```ts
import { CARKernel } from './src/metropolis/car-kernel/index.js';

const kernel = new CARKernel();

kernel.registerTool('ping', async (args: Record<string, unknown>) => ({
  pong: true,
  args,
}));

await kernel.dispatch({
  type: 'AGENT_REGISTER',
  payload: { agentId: 'operator-1', capabilities: ['ping'] },
  issuedAt: new Date().toISOString(),
  issuedBy: 'system',
});

const events = await kernel.dispatch({
  type: 'TOOL_INVOKE',
  payload: { agentId: 'operator-1', tool: 'ping', args: { message: 'hello' } },
  issuedAt: new Date().toISOString(),
  issuedBy: 'operator-1',
});

console.log(events);
console.log(kernel.getState());
```

## Design principles

1. **Agents must act, not just chat** — The output is a changed world state, not a paragraph.
2. **Trust by verification** — Every action is logged and reproducible.
3. **Voice-first, not voice-only** — Voice is the fastest path; text and API are still available.
4. **Recover first, escalate later** — Systems agents handle failures before a human sees them.

## License

MIT — see [LICENSE](LICENSE) for details.
