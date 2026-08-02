/**
 * The bounded recursive execution loop — the heart of the harness.
 *
 * One iteration = one full PAI Algorithm cycle collapsed to plan → build →
 * verify. The loop is Arbol's Loop Gate made recursive and given RecursiveMAS's
 * safety envelope: it self-recurses only while verification fails AND budget
 * remains (iterations, depth, fuel), and it rejects an unguarded cycle by
 * detecting a fixed point (same code digest + same open failures two iterations
 * running).
 *
 * Failures are never swallowed: each is captured into state and injected into
 * the next iteration's planning phase. Distribution happens exactly once, only
 * after verify exits 0.
 */

import { randomUUID } from "node:crypto";
import { join } from "node:path";
import type { ExecutionState, Project, LoopConfig } from "./types.js";
import { DEFAULT_LOOP_CONFIG } from "./types.js";
import type { StoragePaths } from "./storage.js";
import type { AnyLedger } from "./ledger.js";
import { Ledger } from "./ledger.js";
import { ensureStorage } from "./storage.js";
import { digestWorkspace } from "./digest.js";
import { stageWorkspace } from "./staging.js";
import { publishDistribution } from "./distribution.js";
import { planPhase, buildPhase, verifyPhase, type PhaseDeps } from "./phases.js";
import { StateStore, type AnyStateStore } from "./stateStore.js";
import {
  createState,
  nextIteration,
  recordError,
  setStatus,
  terminate,
  setDistPath,
  openErrors,
} from "./state.js";

export interface RunOptions {
  /** Source tree to copy into the external-volume build workspace. */
  workspace: string;
  paths?: StoragePaths;
  config?: Partial<LoopConfig>;
  ledger?: AnyLedger;
  stateStore?: AnyStateStore;
  /** Reuse an existing state id (e.g. daemon-assigned). */
  id?: string;
}

/** A signature of "where we are": digest of code + sorted open failure signatures. */
function progressKey(state: ExecutionState): string {
  const sigs = openErrors(state)
    .map((e) => e.signature)
    .sort()
    .join(",");
  return `${state.currentCode.digest}|${sigs}`;
}

/**
 * Drive `project` to a verified state or a bounded failure. Returns the final
 * ExecutionState (status `succeeded` with `distPath` set, or `failed` with a
 * `termination` reason).
 */
export async function runLoop(project: Project, opts: RunOptions): Promise<ExecutionState> {
  const paths = opts.paths ?? ensureStorage();
  const config = resolveConfig(opts.config);
  const executionId = opts.id ?? randomUUID();
  const ledger: AnyLedger =
    opts.ledger ?? new Ledger(join(paths.ledgers, `${executionId}.jsonl`));
  const stateStore: AnyStateStore = opts.stateStore ?? new StateStore(paths.state);
  const deps: PhaseDeps = { project, paths, config };

  const workspace = stageWorkspace(opts.workspace, executionId, paths);
  let state = createState({
    objective: project.objective,
    workspace,
    codeDigest: digestWorkspace(workspace),
    id: executionId,
  });
  state = setStatus(state, "running");
  stateStore.save(state);
  ledger.append({
    type: "execution.started",
    executionId: state.id,
    iteration: state.iteration,
    detail: { objective: state.objective, workspace: state.currentCode.workspace, config },
  });

  async function unroll(
    current: ExecutionState,
    depth: number,
    fuel: number,
    lastKey: string | null,
  ): Promise<ExecutionState> {
    // ── Budget gates (checked before doing work) ───────────────────
    if (current.iteration >= config.maxIterations) {
      return terminate(current, "max_iterations", "failed");
    }
    if (depth >= config.maxDepth) {
      return terminate(current, "max_depth", "failed");
    }
    if (fuel <= 0) {
      return terminate(current, "fuel_exhausted", "failed");
    }

    // ── PLAN ───────────────────────────────────────────────────────
    const planned = await planPhase(current, deps);
    current = planned.state;
    stateStore.save(current);
    logLastPhase(ledger, current);
    if (planned.plan.exhausted) {
      logCaptured(ledger, current);
      return terminate(current, "no_plan", "failed");
    }

    // ── BUILD ──────────────────────────────────────────────────────
    current = await buildPhase(current, planned.plan, deps);
    stateStore.save(current);
    logLastPhase(ledger, current);
    const buildFailed = openErrors(current).some((e) => e.phase === "build");

    // ── VERIFY (only if build produced something) ──────────────────
    let verified = false;
    if (!buildFailed) {
      const v = await verifyPhase(current, deps);
      current = v.state;
      stateStore.save(current);
      verified = v.ok;
      logLastPhase(ledger, current);
    }
    logCaptured(ledger, current);

    // ── SUCCESS: distribute exactly once ───────────────────────────
    if (verified) {
      let distPath: string;
      try {
        distPath = publishDistribution(current, project, paths);
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        current = recordError(current, "verify", `distribution failed: ${message}`);
        logCaptured(ledger, current);
        return terminate(current, "distribution_failed", "failed");
      }
      current = setDistPath(current, distPath);
      current = terminate(current, "verified", "succeeded");
      stateStore.save(current);
      ledger.append({
        type: "distribution.published",
        executionId: current.id,
        iteration: current.iteration,
        detail: { distPath },
      });
      return current;
    }

    // ── FIXED-POINT (unguarded cycle) rejection ────────────────────
    const key = progressKey(current);
    if (key === lastKey) {
      return terminate(current, "fixed_point", "failed");
    }

    // ── LEARN → next OBSERVE: recurse with a fresh digest ──────────
    const digest = digestWorkspace(current.currentCode.workspace);
    current = nextIteration(current, digest);
    stateStore.save(current);
    ledger.append({
      type: "iteration.advanced",
      executionId: current.id,
      iteration: current.iteration,
      detail: { capturedErrors: current.errors.length, fuel: fuel - 1, depth: depth + 1 },
    });
    return unroll(current, depth + 1, fuel - 1, key);
  }

  state = await unroll(state, 0, config.fuel, null);
  ledger.append({
    type: "execution.terminated",
    executionId: state.id,
    iteration: state.iteration,
    detail: { termination: state.termination, status: state.status, distPath: state.distPath },
  });
  stateStore.save(state);
  return state;
}

function resolveConfig(input?: Partial<LoopConfig>): LoopConfig {
  const config = { ...DEFAULT_LOOP_CONFIG };
  if (!input) return config;
  for (const key of Object.keys(config) as Array<keyof LoopConfig>) {
    const value = input[key];
    if (value === undefined) continue;
    if (!Number.isFinite(value) || value <= 0) {
      throw new Error(`loop config '${key}' must be a positive number`);
    }
    config[key] = value;
  }
  return config;
}

function logLastPhase(ledger: AnyLedger, state: ExecutionState): void {
  const last = state.phases[state.phases.length - 1];
  if (!last) return;
  ledger.append({
    type: "phase.completed",
    executionId: state.id,
    iteration: last.iteration,
    detail: { phase: last.phase, ok: last.ok, summary: last.summary },
  });
}

function logCaptured(ledger: AnyLedger, state: ExecutionState): void {
  for (const e of openErrors(state)) {
    ledger.append({
      type: "error.captured",
      executionId: state.id,
      iteration: e.iteration,
      detail: { phase: e.phase, signature: e.signature, exitCode: e.exitCode, command: e.command },
    });
  }
}
