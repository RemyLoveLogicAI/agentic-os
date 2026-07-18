/**
 * Distribution publisher.
 *
 * Copies the verified artifact into a per-execution directory under the external
 * volume's `dist` root. This runs ONLY after the verify phase exits 0 — the
 * single success signal that authorizes distribution.
 */

import { cpSync, mkdirSync, rmSync, writeFileSync, existsSync } from "node:fs";
import { isAbsolute, join, relative, resolve, sep } from "node:path";
import type { ExecutionState, Project } from "./types.js";
import type { StoragePaths } from "./storage.js";

const EXCLUDED = new Set(["node_modules", ".git", "cache", "tmp"]);

/**
 * Publish the workspace (or the project's declared dist files) to
 * `<share>/dist/<executionId>/` and write a manifest. Returns the absolute
 * distribution path.
 */
export function publishDistribution(
  state: ExecutionState,
  project: Project,
  paths: StoragePaths,
): string {
  const target = join(paths.dist, state.id);
  // Remove any stale publication for a reused execution id before validation.
  if (existsSync(target)) rmSync(target, { recursive: true, force: true });

  if (project.distFiles && project.distFiles.length > 0) {
    const workspaceRoot = resolve(state.currentCode.workspace);
    for (const rel of project.distFiles) {
      const src = resolve(workspaceRoot, rel);
      const withinWorkspace = relative(workspaceRoot, src);
      if (
        withinWorkspace === ".." ||
        withinWorkspace.startsWith(`..${sep}`) ||
        isAbsolute(withinWorkspace)
      ) {
        throw new Error(`distribution path must stay inside the workspace: ${rel}`);
      }
      if (!existsSync(src)) throw new Error(`declared distribution file does not exist: ${rel}`);
    }
  }

  // Validation above ensures a failed publication never creates a directory.
  mkdirSync(target, { recursive: true });

  if (project.distFiles && project.distFiles.length > 0) {
    for (const rel of project.distFiles) {
      const src = resolve(state.currentCode.workspace, rel);
      cpSync(src, join(target, rel), { recursive: true });
    }
  } else {
    cpSync(state.currentCode.workspace, target, {
      recursive: true,
      filter: (src) => {
        const seg = src.split(/[\\/]/);
        return !seg.some((s) => EXCLUDED.has(s));
      },
    });
  }

  const manifest = {
    executionId: state.id,
    objective: state.objective,
    iterations: state.iteration + 1,
    verifiedAt: new Date().toISOString(),
    buildCommand: project.buildCommand,
    verifyCommand: project.verifyCommand,
    errorsEncountered: state.errors.length,
    source: state.currentCode.workspace,
  };
  writeFileSync(join(target, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`, "utf8");

  return target;
}
