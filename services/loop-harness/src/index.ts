/** Public API for @agentic-os/loop-harness. */

export { runLoop } from "./loop.js";
export type { RunOptions } from "./loop.js";

export { ensureStorage, resolveShareRoot, storageEnv, DEFAULT_SHARE_ROOT } from "./storage.js";
export type { StoragePaths } from "./storage.js";

export { stageWorkspace } from "./staging.js";
export { publishDistribution } from "./distribution.js";
export { runCommand } from "./exec.js";
export { classify } from "./classify.js";
export { digestWorkspace } from "./digest.js";

export { createState, openErrors } from "./state.js";
export { Ledger, NullLedger } from "./ledger.js";
export { StateStore, NullStateStore } from "./stateStore.js";

export { loadConfig, parseConfig, projectFromConfig, ruleBasedPlanner } from "./config.js";
export type { ProjectConfig } from "./config.js";

export { runDaemon, processAvailable, submitJob, ensureDaemonDirs } from "./daemon.js";
export type { DaemonOptions, DaemonDirs } from "./daemon.js";

export type {
  Phase,
  TerminationReason,
  ExecutionStatus,
  ErrorRecord,
  ErrorSignature,
  CommandResult,
  PhaseRecord,
  Plan,
  CurrentCode,
  ExecutionState,
  Project,
  Planner,
  LoopConfig,
} from "./types.js";
export { DEFAULT_LOOP_CONFIG } from "./types.js";
