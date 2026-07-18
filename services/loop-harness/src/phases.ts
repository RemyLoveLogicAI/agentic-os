/**
 * The three actionable PAI phases, implemented as Arbol-style Actions.
 *
 * Each phase is a single unit of work that takes the current state, does one
 * thing, and returns updated state via the pure reducers (the Arbol passthrough
 * model, applied to ExecutionState rather than a JSON envelope).
 *
 *   plan   — PAI OBSERVE+THINK+PLAN: turn accumulated failures into a Plan.
 *   build  — PAI BUILD+EXECUTE: apply the plan, run pre-build steps + build cmd.
 *   verify — PAI VERIFY: run the deterministic verify command; exit 0 == done.
 */

import type { ExecutionState, Project, Plan, LoopConfig, CommandResult } from "./types.js";
import type { StoragePaths } from "./storage.js";
import { runCommand } from "./exec.js";
import { recordPhase, recordCommandError, recordError } from "./state.js";

function now(): string {
  return new Date().toISOString();
}

export interface PhaseDeps {
  project: Project;
  paths: StoragePaths;
  config: LoopConfig;
}

/** PLAN — ask the planner for the next mutation, given accumulated failures. */
export async function planPhase(
  state: ExecutionState,
  deps: PhaseDeps,
): Promise<{ state: ExecutionState; plan: Plan }> {
  let plan: Plan;
  try {
    plan = await deps.project.planner(state);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    const withError = recordError(state, "plan", `planner threw: ${message}`);
    return {
      state: recordPhase(withError, {
        iteration: state.iteration,
        phase: "plan",
        ok: false,
        summary: `planner threw: ${message}`,
        at: now(),
      }),
      plan: { steps: [], preBuildCommands: [], exhausted: true },
    };
  }
  const summary =
    plan.steps.length > 0 ? plan.steps.join("; ") : "no-op plan";
  return {
    state: recordPhase(state, {
      iteration: state.iteration,
      phase: "plan",
      ok: !plan.exhausted,
      summary,
      at: now(),
    }),
    plan,
  };
}

/** BUILD — apply the plan's mutation and run pre-build commands + build command. */
export async function buildPhase(
  state: ExecutionState,
  plan: Plan,
  deps: PhaseDeps,
): Promise<ExecutionState> {
  let next = state;

  // Apply the plan's working-tree mutation, if any.
  if (plan.apply) {
    try {
      const summary = await plan.apply(state.currentCode.workspace);
      next = recordPhase(next, {
        iteration: next.iteration,
        phase: "build",
        ok: true,
        summary: `apply: ${summary}`,
        at: now(),
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      return recordError(next, "build", `apply step threw: ${message}`);
    }
  }

  // Run pre-build commands (e.g. dependency install on the external volume).
  const commands = [...plan.preBuildCommands, deps.project.buildCommand];
  for (const command of commands) {
    let result: CommandResult;
    try {
      result = await runCommand(command, {
        cwd: state.currentCode.workspace,
        paths: deps.paths,
        timeoutMs: deps.config.commandTimeoutMs,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      return recordError(next, "build", `failed to spawn '${command}': ${message}`);
    }
    next = recordPhase(next, {
      iteration: next.iteration,
      phase: "build",
      ok: result.exitCode === 0,
      summary: `${command} → exit ${result.exitCode}`,
      command: result,
      at: now(),
    });
    if (result.exitCode !== 0) {
      // Build failed — capture it and stop; verify is not attempted.
      return recordCommandError(next, "build", result);
    }
  }
  return next;
}

/** VERIFY — run the deterministic verify command; exit 0 is the sole success. */
export async function verifyPhase(
  state: ExecutionState,
  deps: PhaseDeps,
): Promise<{ state: ExecutionState; ok: boolean }> {
  let result: CommandResult;
  try {
    result = await runCommand(deps.project.verifyCommand, {
      cwd: state.currentCode.workspace,
      paths: deps.paths,
      timeoutMs: deps.config.commandTimeoutMs,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return { state: recordError(state, "verify", `failed to spawn verify: ${message}`), ok: false };
  }
  const ok = result.exitCode === 0;
  let next = recordPhase(state, {
    iteration: state.iteration,
    phase: "verify",
    ok,
    summary: `${deps.project.verifyCommand} → exit ${result.exitCode}`,
    command: result,
    at: now(),
  });
  if (!ok) next = recordCommandError(next, "verify", result);
  return { state: next, ok };
}
