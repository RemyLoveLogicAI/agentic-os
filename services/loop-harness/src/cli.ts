#!/usr/bin/env node
/** Command-line entrypoint for one-shot runs and the durable daemon. */

import { resolve } from "node:path";
import { ensureStorage } from "./storage.js";
import { loadConfig, projectFromConfig } from "./config.js";
import { runLoop } from "./loop.js";
import { runDaemon, submitJob, ensureDaemonDirs } from "./daemon.js";

function usage(): never {
  console.error(`Usage:
  loop-harness run <project.json>       run one recursive execution now
  loop-harness submit <project.json>    enqueue a job for the daemon
  loop-harness daemon [--poll <ms>]     process queued jobs until SIGINT/SIGTERM
  loop-harness paths                    print external-volume directories
`);
  process.exit(2);
}

async function main(): Promise<void> {
  const [command, arg, ...rest] = process.argv.slice(2);
  const paths = ensureStorage();

  if (command === "paths") {
    console.log(JSON.stringify({ ...paths, daemon: ensureDaemonDirs(paths) }, null, 2));
    return;
  }

  if (command === "run") {
    if (!arg) usage();
    const config = loadConfig(resolve(arg));
    const state = await runLoop(projectFromConfig(config), {
      workspace: resolve(config.source),
      paths,
      config: {
        maxIterations: config.maxIterations,
        maxDepth: config.maxDepth,
        fuel: config.fuel,
        commandTimeoutMs: config.commandTimeoutMs,
      },
    });
    console.log(JSON.stringify(state, null, 2));
    process.exitCode = state.status === "succeeded" ? 0 : 1;
    return;
  }

  if (command === "submit") {
    if (!arg) usage();
    const config = loadConfig(resolve(arg));
    config.source = resolve(config.source);
    const id = submitJob(config, paths);
    console.log(JSON.stringify({ id, status: "queued" }));
    return;
  }

  if (command === "daemon") {
    const pollIndex = [arg, ...rest].indexOf("--poll");
    const values = [arg, ...rest];
    const pollMs = pollIndex >= 0 ? Number(values[pollIndex + 1]) : 1_000;
    if (!Number.isFinite(pollMs) || pollMs <= 0) throw new Error("--poll must be a positive number");
    const controller = new AbortController();
    process.once("SIGINT", () => controller.abort());
    process.once("SIGTERM", () => controller.abort());
    console.error(`[loop-harness] daemon watching ${ensureDaemonDirs(paths).inbox}`);
    await runDaemon({ paths, pollMs, signal: controller.signal });
    return;
  }

  usage();
}

main().catch((err: unknown) => {
  console.error(err instanceof Error ? err.stack ?? err.message : String(err));
  process.exitCode = 1;
});
