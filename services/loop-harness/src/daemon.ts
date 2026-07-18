/**
 * Durable local worker daemon.
 *
 * Watches `<share>/tmp/loop-harness/daemon/inbox` for JSON ProjectConfig jobs,
 * atomically claims each file, runs the recursive loop, and writes the final
 * ExecutionState to `completed/` or `failed/`. A killed daemon leaves claimed
 * jobs in `processing/`, making interrupted work visible rather than lost.
 */

import { mkdirSync, readdirSync, readFileSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { randomUUID } from "node:crypto";
import type { StoragePaths } from "./storage.js";
import type { ProjectConfig } from "./config.js";
import { parseConfig, projectFromConfig } from "./config.js";
import { runLoop } from "./loop.js";

export interface DaemonOptions {
  paths: StoragePaths;
  pollMs?: number;
  signal?: AbortSignal;
}

export interface DaemonDirs {
  root: string;
  inbox: string;
  processing: string;
  completed: string;
  failed: string;
}

export function ensureDaemonDirs(paths: StoragePaths): DaemonDirs {
  const root = join(paths.tmp, "loop-harness", "daemon");
  const dirs: DaemonDirs = {
    root,
    inbox: join(root, "inbox"),
    processing: join(root, "processing"),
    completed: join(root, "completed"),
    failed: join(root, "failed"),
  };
  for (const dir of Object.values(dirs)) mkdirSync(dir, { recursive: true });
  return dirs;
}

/** Submit a config object to a daemon inbox and return its job id. */
export function submitJob(config: ProjectConfig, paths: StoragePaths): string {
  const dirs = ensureDaemonDirs(paths);
  const id = randomUUID();
  const target = join(dirs.inbox, `${id}.json`);
  const pending = `${target}.pending`;
  writeFileSync(pending, `${JSON.stringify(config, null, 2)}\n`, "utf8");
  renameSync(pending, target);
  return id;
}

/** Process every job currently waiting in the inbox once. */
export async function processAvailable(paths: StoragePaths): Promise<number> {
  const dirs = ensureDaemonDirs(paths);
  const jobs = readdirSync(dirs.inbox)
    .filter((name) => name.endsWith(".json"))
    .sort();
  let processed = 0;

  for (const name of jobs) {
    const source = join(dirs.inbox, name);
    const claimed = join(dirs.processing, name);
    try {
      renameSync(source, claimed);
    } catch {
      // Another worker claimed it between listing and rename.
      continue;
    }

    const id = basename(name, ".json");
    try {
      const config = parseConfig(JSON.parse(readFileSync(claimed, "utf8")));
      const state = await runLoop(projectFromConfig(config), {
        workspace: config.source,
        paths,
        id,
        config: {
          maxIterations: config.maxIterations,
          maxDepth: config.maxDepth,
          fuel: config.fuel,
          commandTimeoutMs: config.commandTimeoutMs,
        },
      });
      const destination = state.status === "succeeded" ? dirs.completed : dirs.failed;
      writeFileSync(join(destination, name), `${JSON.stringify(state, null, 2)}\n`, "utf8");
      rmSync(claimed, { force: true });
    } catch (err) {
      const message = err instanceof Error ? err.stack ?? err.message : String(err);
      writeFileSync(
        join(dirs.failed, name),
        `${JSON.stringify({ id, status: "failed", termination: "aborted", error: message }, null, 2)}\n`,
        "utf8",
      );
      rmSync(claimed, { force: true });
    }
    processed += 1;
  }
  return processed;
}

/** Run the daemon until its AbortSignal fires. */
export async function runDaemon(opts: DaemonOptions): Promise<void> {
  const pollMs = opts.pollMs ?? 1_000;
  ensureDaemonDirs(opts.paths);
  while (!opts.signal?.aborted) {
    const count = await processAvailable(opts.paths);
    if (count === 0) await delay(pollMs, opts.signal);
  }
}

function delay(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve) => {
    const timer = setTimeout(resolve, ms);
    signal?.addEventListener(
      "abort",
      () => {
        clearTimeout(timer);
        resolve();
      },
      { once: true },
    );
  });
}
