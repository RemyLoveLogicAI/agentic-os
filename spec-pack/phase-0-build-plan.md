# Agentic OS Phase-0 Build Plan

## Goal
Ship a thin but real end-to-end slice: voice question → command classification → approval gate → one safe action → evidence log.

## In Scope
- Spokenly MCP connection
- Deterministic command parser
- One safe desktop action
- One safe API action
- Approval store
- Evidence log
- Minimal operator panel

## Out of Scope
- Full swarm orchestration
- Multi-device sync
- CYOA narrative layer
- Advanced packaging workflows
- Full Knowledge Graph automation

## Build Steps

### Step 1 — Foundation
- Create the repo skeleton
- Add docs and runbooks
- Define secrets and trust boundaries
- Set up logging and ledgers

### Step 2 — Voice Entry
- Connect Spokenly as the voice-question interface
- Define the tool contract for clarification requests
- Verify the local voice round-trip

### Step 3 — Deterministic Router
- Build a simple intent classifier
- Route to `safe_desktop`, `safe_api`, or `needs_approval`
- Keep the first pass rule-based

### Step 4 — Approval Gate
- Persist approval requests
- Add single-use approvals
- Add TTL expiry

### Step 5 — Execution Adapters
- Safe desktop action: paste text or open a URL
- Safe API action: query a status endpoint
- Log every action with timestamps and evidence

### Step 6 — Verification
- Smoke test the full loop
- Confirm evidence capture
- Confirm no risky action runs without approval

## Phase-0 Deliverables
- Working voice clarification path
- Working command router
- Working approval queue
- Working evidence ledger
- Working operator panel

## Exit Criteria
- A voice question can be answered through the MCP bridge.
- A command can be classified without model ambiguity.
- A risky action cannot proceed without approval.
- Every action writes an auditable record.
- The operator can inspect state from one panel.
