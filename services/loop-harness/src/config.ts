/**
 * Declarative project config + rule-based planner for CLI/daemon jobs.
 *
 * Library consumers can supply an arbitrary Planner callback. For durable daemon
 * jobs, functions cannot be serialized, so jobs describe per-error repair
 * commands. The rule-based planner injects the most recent captured failure into
 * its decision and selects the configured repair for that signature.
 */

import { readFileSync } from "node:fs";
import type { Project, ErrorSignature, Plan, ExecutionState } from "./types.js";

export interface ProjectConfig {
  objective: string;
  /** Source tree; staged onto the external volume before execution. */
  source: string;
  buildCommand: string;
  verifyCommand: string;
  distFiles?: string[];
  /** Commands keyed by failure signature, run before the next build. */
  repairs?: Partial<Record<ErrorSignature, string[]>>;
  maxIterations?: number;
  maxDepth?: number;
  fuel?: number;
  commandTimeoutMs?: number;
}

/** Parse and validate a project config JSON file. */
export function loadConfig(path: string): ProjectConfig {
  let raw: unknown;
  try {
    raw = JSON.parse(readFileSync(path, "utf8"));
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    throw new Error(`cannot read project config '${path}': ${message}`);
  }
  return parseConfig(raw);
}

/** Validate an already-parsed daemon payload. */
export function parseConfig(raw: unknown): ProjectConfig {
  if (!raw || typeof raw !== "object") throw new Error("project config must be a JSON object");
  const obj = raw as Record<string, unknown>;
  for (const key of ["objective", "source", "buildCommand", "verifyCommand"] as const) {
    if (typeof obj[key] !== "string" || obj[key].trim().length === 0) {
      throw new Error(`project config '${key}' must be a non-empty string`);
    }
  }
  if (obj.distFiles !== undefined) {
    if (!Array.isArray(obj.distFiles) || obj.distFiles.some((v) => typeof v !== "string")) {
      throw new Error("project config 'distFiles' must be an array of strings");
    }
  }
  if (obj.repairs !== undefined) {
    if (!obj.repairs || typeof obj.repairs !== "object" || Array.isArray(obj.repairs)) {
      throw new Error("project config 'repairs' must be an object");
    }
    for (const commands of Object.values(obj.repairs as Record<string, unknown>)) {
      if (!Array.isArray(commands) || commands.some((v) => typeof v !== "string")) {
        throw new Error("each project config repair must be an array of commands");
      }
    }
  }
  return obj as unknown as ProjectConfig;
}

/** Convert a serializable ProjectConfig into the engine's Project interface. */
export function projectFromConfig(config: ProjectConfig): Project {
  return {
    objective: config.objective,
    buildCommand: config.buildCommand,
    verifyCommand: config.verifyCommand,
    distFiles: config.distFiles,
    planner: ruleBasedPlanner(config.repairs ?? {}),
  };
}

/**
 * Planner for daemon jobs. Iteration 0 bootstraps with no repair and lets the
 * build expose the current failure. Later iterations select the command list for
 * the most recent error signature. If no repair exists, the planner exhausts
 * rather than cycling forever.
 */
export function ruleBasedPlanner(
  repairs: Partial<Record<ErrorSignature, string[]>>,
): (state: ExecutionState) => Plan {
  return (state) => {
    if (state.errors.length === 0) {
      return {
        steps: ["Build current source to observe its distance from the ideal state"],
        preBuildCommands: [],
      };
    }
    const latest = state.errors[state.errors.length - 1];
    const commands = repairs[latest.signature];
    if (!commands || commands.length === 0) {
      return {
        steps: [`No configured repair for ${latest.signature}`],
        preBuildCommands: [],
        exhausted: true,
      };
    }
    return {
      steps: [
        `Observe iteration ${latest.iteration} ${latest.phase} failure (${latest.signature})`,
        `Apply configured repair: ${commands.join(" && ")}`,
        "Rebuild and verify",
      ],
      preBuildCommands: commands,
    };
  };
}
