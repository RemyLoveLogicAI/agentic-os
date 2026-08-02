/**
 * Pure reducers for {@link ExecutionState}.
 *
 * Every transition returns a new object; the input is never mutated. This keeps
 * the recursion referentially honest and lets any two iterations be compared for
 * a fixed point.
 */

import { randomUUID } from "node:crypto";
import type {
  ExecutionState,
  ErrorRecord,
  PhaseRecord,
  ExecutionStatus,
  TerminationReason,
  CommandResult,
  Phase,
  ErrorSignature,
} from "./types.js";
import { classify } from "./classify.js";

function now(): string {
  return new Date().toISOString();
}

/** Create the initial state for an objective. */
export function createState(input: {
  objective: string;
  workspace: string;
  codeDigest: string;
  id?: string;
}): ExecutionState {
  const ts = now();
  return {
    id: input.id ?? randomUUID(),
    objective: input.objective,
    currentCode: {
      workspace: input.workspace,
      digest: input.codeDigest,
    },
    errors: [],
    phases: [],
    iteration: 0,
    status: "pending",
    startedAt: ts,
    updatedAt: ts,
  };
}

/** Append a phase record to the audit trail. */
export function recordPhase(state: ExecutionState, phase: PhaseRecord): ExecutionState {
  return { ...state, phases: [...state.phases, phase], updatedAt: now() };
}

/**
 * Record a failure derived from a failed command. The failure is both appended
 * to `errors` (the feedback signal for planning) and classified.
 */
export function recordCommandError(
  state: ExecutionState,
  phase: Phase,
  result: CommandResult,
): ExecutionState {
  const record: ErrorRecord = {
    iteration: state.iteration,
    phase,
    command: result.command,
    exitCode: result.exitCode,
    stdout: result.stdout,
    stderr: result.stderr,
    signature: classify(result),
    at: now(),
  };
  return { ...state, errors: [...state.errors, record], updatedAt: now() };
}

/** Record a non-process failure (e.g. a planner or apply-step threw). */
export function recordError(
  state: ExecutionState,
  phase: Phase,
  message: string,
  signature: ErrorSignature = "unknown",
): ExecutionState {
  const record: ErrorRecord = {
    iteration: state.iteration,
    phase,
    exitCode: null,
    stdout: "",
    stderr: message,
    signature,
    at: now(),
  };
  return { ...state, errors: [...state.errors, record], updatedAt: now() };
}

/** Advance to the next iteration, refreshing the code digest. */
export function nextIteration(state: ExecutionState, codeDigest: string): ExecutionState {
  return {
    ...state,
    currentCode: { ...state.currentCode, digest: codeDigest },
    iteration: state.iteration + 1,
    updatedAt: now(),
  };
}

/** Set the lifecycle status. */
export function setStatus(state: ExecutionState, status: ExecutionStatus): ExecutionState {
  return { ...state, status, updatedAt: now() };
}

/** Terminate the loop with a reason. */
export function terminate(
  state: ExecutionState,
  reason: TerminationReason,
  status: ExecutionStatus,
): ExecutionState {
  return { ...state, termination: reason, status, updatedAt: now() };
}

/** Mark the published distribution path on success. */
export function setDistPath(state: ExecutionState, distPath: string): ExecutionState {
  return { ...state, distPath, updatedAt: now() };
}

/** The failures observed during the most recent iteration (the planner's focus). */
export function openErrors(state: ExecutionState): ErrorRecord[] {
  return state.errors.filter((e) => e.iteration === state.iteration);
}
