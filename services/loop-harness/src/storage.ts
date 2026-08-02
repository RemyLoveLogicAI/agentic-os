/**
 * Storage hygiene layer.
 *
 * Enforces the mandate that ALL heavy software writes — local caches, package
 * manager state, temporary build workspaces, and final distributions — live
 * under a single external-volume root, never in the repository or default
 * user/home locations.
 *
 * The production root is `/Volumes/SAMSUNG SSD/LOCAL_SHARE`. It can be
 * overridden with the `LOOP_HARNESS_SHARE_ROOT` environment variable (used by
 * tests and CI, where the external volume is mocked at a container path).
 */

import { mkdirSync, existsSync } from "node:fs";
import { isAbsolute, join } from "node:path";

/** The default external-volume root mandated by the storage hygiene policy. */
export const DEFAULT_SHARE_ROOT = "/Volumes/SAMSUNG SSD/LOCAL_SHARE";

export interface StoragePaths {
  /** External-volume root. */
  root: string;
  /** Package-manager cache/home (npm_config_cache, BUN_INSTALL_CACHE_DIR, ...). */
  cache: string;
  /** npm/bun install prefix. */
  npm: string;
  /** Scratch space for per-execution workspaces. */
  tmp: string;
  /** Final distribution root — artifacts land here on verified success. */
  dist: string;
  /** Durable execution-state snapshots. */
  state: string;
  /** Append-only execution evidence ledgers. */
  ledgers: string;
}

/** Resolve the external-volume root from env, falling back to the mandate. */
export function resolveShareRoot(env: NodeJS.ProcessEnv = process.env): string {
  const override = env.LOOP_HARNESS_SHARE_ROOT?.trim();
  const root = override && override.length > 0 ? override : DEFAULT_SHARE_ROOT;
  if (!isAbsolute(root)) throw new Error(`LOOP_HARNESS_SHARE_ROOT must be absolute: ${root}`);
  return root;
}

/**
 * Compute the canonical sub-paths under the share root and ensure they exist.
 * Idempotent — safe to call on every daemon boot.
 */
export function ensureStorage(env: NodeJS.ProcessEnv = process.env): StoragePaths {
  const root = resolveShareRoot(env);
  const paths: StoragePaths = {
    root,
    cache: join(root, "cache"),
    npm: join(root, "npm"),
    tmp: join(root, "tmp"),
    dist: join(root, "dist"),
    state: join(root, "state"),
    ledgers: join(root, "ledgers"),
  };
  for (const p of Object.values(paths)) {
    if (!existsSync(p)) mkdirSync(p, { recursive: true });
  }
  return paths;
}

/**
 * Build the environment overlay that pins every package manager and temp path
 * to the external volume. Spread over `process.env` for child processes so no
 * install or cache write escapes to a default location.
 */
export function storageEnv(paths: StoragePaths): Record<string, string> {
  return {
    // npm
    npm_config_cache: paths.cache,
    npm_config_prefix: paths.npm,
    // bun
    BUN_INSTALL_CACHE_DIR: paths.cache,
    BUN_INSTALL: paths.npm,
    // generic temp
    TMPDIR: paths.tmp,
    TEMP: paths.tmp,
    TMP: paths.tmp,
    // yarn/pnpm, just in case a project uses them
    YARN_CACHE_FOLDER: paths.cache,
    // marker consumed by projects that want to self-locate the share root
    LOOP_HARNESS_SHARE_ROOT: paths.root,
  };
}
