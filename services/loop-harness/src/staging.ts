/**
 * Source staging.
 *
 * The caller may point the harness at any source tree (including a git checkout
 * on the local disk), but no build is ever run there. The tree is copied into a
 * per-execution workspace under `<share>/tmp/executions/`, ensuring compilers,
 * package managers, and runtime scratch files can only make heavy writes on the
 * external volume.
 */

import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { join } from "node:path";
import type { StoragePaths } from "./storage.js";

const EXCLUDED = new Set(["node_modules", ".git", "dist", ".cache", "coverage"]);

/** Copy a source tree to an isolated external-volume build workspace. */
export function stageWorkspace(source: string, executionId: string, paths: StoragePaths): string {
  if (!existsSync(source)) throw new Error(`source workspace does not exist: ${source}`);
  const target = join(paths.tmp, "loop-harness", "executions", executionId, "workspace");
  if (existsSync(target)) rmSync(target, { recursive: true, force: true });
  mkdirSync(target, { recursive: true });
  cpSync(source, target, {
    recursive: true,
    filter: (src) => {
      const segments = src.split(/[\\/]/);
      return !segments.some((s) => EXCLUDED.has(s));
    },
  });
  return target;
}
