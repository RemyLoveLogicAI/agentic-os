/**
 * Content digest of a working directory, used for fixed-point detection.
 *
 * Hashes the relative path + contents of every tracked file (excluding cache,
 * dependency, and build-output directories) into a single stable hex string.
 * Two iterations that begin from the same digest and the same open failures are
 * making no progress, so the loop terminates with `fixed_point`.
 */

import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const IGNORED = new Set(["node_modules", ".git", "dist", "cache", "tmp", ".cache"]);

function walk(dir: string, root: string, acc: string[]): void {
  let entries: string[];
  try {
    entries = readdirSync(dir).sort();
  } catch {
    return;
  }
  for (const name of entries) {
    if (IGNORED.has(name)) continue;
    const full = join(dir, name);
    let st;
    try {
      st = statSync(full);
    } catch {
      continue;
    }
    if (st.isDirectory()) {
      walk(full, root, acc);
    } else if (st.isFile()) {
      let content = "";
      try {
        content = readFileSync(full, "utf8");
      } catch {
        content = `\u0000binary:${st.size}`;
      }
      acc.push(`${relative(root, full)}\u0000${content}`);
    }
  }
}

/** Compute a stable content digest for a workspace directory. */
export function digestWorkspace(workspace: string): string {
  const acc: string[] = [];
  walk(workspace, workspace, acc);
  return createHash("sha256").update(acc.join("\u0001")).digest("hex");
}
