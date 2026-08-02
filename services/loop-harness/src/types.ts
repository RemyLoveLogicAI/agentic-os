/**
 * Core type definitions for the loop-harness.
 *
 * The harness is a local worker daemon that drives a software objective from
 * CURRENT STATE to IDEAL STATE (PAI Algorithm doctrine) by unrolling a bounded
 * recursive loop of Arbol-style phases — plan → build → verify — feeding every
 * captured failure back into the next iteration's planning phase.
 *
 * The vocabulary intentionally fuses two source systems:
 *   - PAI Algorithm phases: OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN
 *     (collapsed here into the three actionable phases plan/build/verify, with
 *     observe+learn folded into the recursion boundary).
 *   - Arbol primitives: an Action is one unit of work; a Pipeline chains Actions
 *     via the passthrough model; the loop is Arbol's Loop Gate with maxIterations.
 */

/** The PAI Algorithm phases surfaced by the harness. */
export type Phase = "plan" | "build" | "verify";

/** Why a recursive loop stopped unrolling. */
export type TerminationReason =
  | "verified" // verify exited 0 — objective reached IDEAL STATE
  | "max_iterations" // iteration budget exhausted without success
  | "max_depth" // recursion depth bound hit
  | "fuel_exhausted" // shared fuel budget spent
  | "fixed_point" // two consecutive iterations produced identical state (no progress)
  | "no_plan" // planner produced no actionable change for a known failure
  | "distribution_failed" // verify passed but artifacts could not be published
  | "aborted"; // externally cancelled

/** Lifecycle status of an execution. */
export type ExecutionStatus = "pending" | "running" | "succeeded" | "failed";

/**
 * A single captured failure — a compiler error, runtime crash, missing
 * `node_modules`, syntax error, or non-zero verification. These records are the
 * feedback signal injected into the next iteration's planning phase.
 */
export interface ErrorRecord {
  /** Iteration (0-based) in which the failure was observed. */
  iteration: number;
  /** Phase that produced the failure. */
  phase: Phase;
  /** The command that failed, if the failure came from a shell command. */
  command?: string;
  /** Process exit code (non-zero), or null for non-process failures. */
  exitCode: number | null;
  /** Captured stdout (may be truncated). */
  stdout: string;
  /** Captured stderr (may be truncated). */
  stderr: string;
  /** A coarse, matchable classification used by planners to select a repair. */
  signature: ErrorSignature;
  /** ISO-8601 timestamp. */
  at: string;
}

/** Coarse classification of a failure, derived from its output. */
export type ErrorSignature =
  | "missing_dependencies" // node_modules crash / "Cannot find module" / "command not found"
  | "syntax_error" // parse/syntax failure
  | "type_error" // type-check failure
  | "test_failure" // tests ran and failed
  | "runtime_error" // uncaught exception at runtime
  | "build_failure" // generic non-zero build
  | "unknown";

/** Result of running a shell command inside the sandbox. */
export interface CommandResult {
  command: string;
  exitCode: number;
  stdout: string;
  stderr: string;
  /** Wall-clock duration in milliseconds. */
  durationMs: number;
}

/** Record of one phase execution within an iteration. */
export interface PhaseRecord {
  iteration: number;
  phase: Phase;
  ok: boolean;
  /** Human-readable summary of what the phase did. */
  summary: string;
  /** The command result, when the phase shelled out. */
  command?: CommandResult;
  at: string;
}

/**
 * A plan is the planner's output for one iteration: the mutation to apply
 * before building, expressed as an ordered list of steps plus an optional
 * patch to the working tree. Planners translate accumulated ErrorRecords into
 * a plan; this is the LEARN → next-OBSERVE bridge.
 */
export interface Plan {
  /** Ordered, human-readable steps this plan will take. */
  steps: string[];
  /**
   * Shell commands to run during the build phase, in order, before the
   * project's own build command. Used e.g. to install dependencies on the
   * external volume after a `missing_dependencies` failure.
   */
  preBuildCommands: string[];
  /**
   * Optional mutation applied to the working directory before building.
   * Receives the absolute workspace path; may write/patch files. Returning a
   * summary string documents the change for the ledger.
   */
  apply?: (workspace: string) => Promise<string> | string;
  /**
   * Set when the planner cannot make progress on the current failures. The
   * loop terminates with `no_plan` when this is true.
   */
  exhausted?: boolean;
}

/** Materialized pointer and digest for the code being evolved. */
export interface CurrentCode {
  /** External-volume working tree used by build and verification actions. */
  workspace: string;
  /** Stable content digest used for fixed-point detection. */
  digest: string;
}

/**
 * The immutable-ish execution state threaded through the recursion. Mutations
 * are performed only via the pure reducers in `state.ts`, which return a new
 * object, so any two iterations can be compared for a fixed point.
 */
export interface ExecutionState {
  /** Stable id for this execution. */
  id: string;
  /** What we are trying to achieve. */
  objective: string;
  /**
   * Current code location and content digest. If two iterations begin from the
   * same digest and the same open failures, the loop is making no progress.
   */
  currentCode: CurrentCode;
  /** All failures observed so far, oldest first. */
  errors: ErrorRecord[];
  /** Per-phase audit trail. */
  phases: PhaseRecord[];
  /** 0-based count of completed iterations. */
  iteration: number;
  /** Current lifecycle status. */
  status: ExecutionStatus;
  /** Set once the loop terminates. */
  termination?: TerminationReason;
  /** Absolute path of the published distribution, set on success. */
  distPath?: string;
  startedAt: string;
  updatedAt: string;
}

/**
 * A Project is the unit of work the harness drives. It supplies the deterministic
 * build and verify commands and a planner. This keeps the loop engine generic:
 * the same engine handles a TypeScript worker, a Python package, or anything with
 * a build+verify command pair.
 */
export interface Project {
  objective: string;
  /**
   * Command that produces the artifact (compile/bundle/install). Run from the
   * workspace root. A non-zero exit is a build failure and is fed back to the
   * planner.
   */
  buildCommand: string;
  /**
   * Deterministic verification command. Exit code 0 is the sole success
   * signal that authorizes distribution.
   */
  verifyCommand: string;
  /**
   * Files that constitute the distribution, relative to the workspace. Copied
   * verbatim to the dist root on success. When omitted, the whole workspace
   * (minus caches) is published.
   */
  distFiles?: string[];
  /** The planner that turns accumulated failures into the next plan. */
  planner: Planner;
}

/**
 * A Planner is PAI's OBSERVE+THINK+PLAN collapsed into a pure(-ish) function:
 * given the current state (objective + accumulated failures + iteration), it
 * returns the plan for the upcoming iteration. On iteration 0 the error list is
 * empty and the planner returns its bootstrap plan.
 */
export type Planner = (state: ExecutionState) => Promise<Plan> | Plan;

/** Tuning knobs for the bounded recursive loop (Arbol Loop Gate). */
export interface LoopConfig {
  /** Hard cap on iterations. Reaching it terminates with `max_iterations`. */
  maxIterations: number;
  /** Recursion depth bound (mirrors RecursiveMAS `max_depth`). */
  maxDepth: number;
  /** Shared fuel budget decremented once per iteration (RecursiveMAS `fuel`). */
  fuel: number;
  /** Per-command timeout in milliseconds. */
  commandTimeoutMs: number;
}

export const DEFAULT_LOOP_CONFIG: LoopConfig = {
  maxIterations: 10,
  maxDepth: 10,
  fuel: 100,
  commandTimeoutMs: 120_000,
};
