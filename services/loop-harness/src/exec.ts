/**
 * Deterministic command runner.
 *
 * Every phase that shells out does so through `runCommand`, which captures
 * stdout, stderr, and the exit code, and applies the storage-hygiene env overlay
 * so child processes cannot write caches or installs outside the external volume.
 */

import { spawn } from "node:child_process";
import type { CommandResult } from "./types.js";
import type { StoragePaths } from "./storage.js";
import { storageEnv } from "./storage.js";

const MAX_CAPTURE = 64 * 1024; // cap captured streams so a runaway build can't blow memory

function clamp(s: string): string {
  return s.length > MAX_CAPTURE ? `${s.slice(0, MAX_CAPTURE)}\n…[truncated]` : s;
}

export interface RunOptions {
  cwd: string;
  paths: StoragePaths;
  timeoutMs: number;
  env?: NodeJS.ProcessEnv;
}

/**
 * Run a shell command to completion. Never rejects for a non-zero exit — a
 * failing command is a normal, expected signal that the loop feeds back to the
 * planner. Only rejects for spawn-level impossibilities.
 */
export function runCommand(command: string, opts: RunOptions): Promise<CommandResult> {
  const start = Date.now();
  return new Promise<CommandResult>((resolve, reject) => {
    const child = spawn(command, {
      cwd: opts.cwd,
      shell: true,
      env: { ...(opts.env ?? process.env), ...storageEnv(opts.paths) },
    });

    let stdout = "";
    let stderr = "";
    let settled = false;

    const timer = setTimeout(() => {
      if (settled) return;
      stderr += `\n[loop-harness] command timed out after ${opts.timeoutMs}ms`;
      child.kill("SIGKILL");
    }, opts.timeoutMs);

    child.stdout?.on("data", (d: Buffer) => {
      if (stdout.length < MAX_CAPTURE) stdout += d.toString();
    });
    child.stderr?.on("data", (d: Buffer) => {
      if (stderr.length < MAX_CAPTURE) stderr += d.toString();
    });

    child.on("error", (err) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      reject(err);
    });

    child.on("close", (code) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolve({
        command,
        exitCode: code ?? 1,
        stdout: clamp(stdout),
        stderr: clamp(stderr),
        durationMs: Date.now() - start,
      });
    });
  });
}
