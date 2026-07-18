import { afterEach, beforeEach, describe, expect, test } from "bun:test";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { randomUUID } from "node:crypto";
import {
  classify,
  ensureStorage,
  processAvailable,
  runLoop,
  submitJob,
  type CommandResult,
  type ExecutionState,
  type Plan,
  type Project,
  type ProjectConfig,
} from "../src/index.js";

const realShare = "/Volumes/SAMSUNG SSD/LOCAL_SHARE";
let root = "";
let source = "";

beforeEach(() => {
  root = join(realShare, "tmp", "loop-harness-tests", randomUUID());
  source = join(root, "source");
  mkdirSync(source, { recursive: true });
});

afterEach(() => {
  if (root) rmSync(root, { recursive: true, force: true });
});

function paths() {
  return ensureStorage({ LOOP_HARNESS_SHARE_ROOT: root });
}

function write(rel: string, content: string): void {
  const target = join(source, rel);
  mkdirSync(dirname(target), { recursive: true });
  writeFileSync(target, content, "utf8");
}

function project(overrides: Partial<Project> = {}): Project {
  return {
    objective: "Produce a verified worker",
    buildCommand: "node build.mjs",
    verifyCommand: "node verify.mjs",
    distFiles: ["build"],
    planner: () => ({ steps: ["Build current source"], preBuildCommands: [] }),
    ...overrides,
  };
}

describe("recursive loop", () => {
  test("publishes only after deterministic verification exits 0", async () => {
    write(
      "build.mjs",
      'import {mkdirSync,writeFileSync} from "node:fs"; mkdirSync("build",{recursive:true}); writeFileSync("build/worker.js","export const ok = true;\\n");',
    );
    write(
      "verify.mjs",
      'import {existsSync} from "node:fs"; process.exit(existsSync("build/worker.js") ? 0 : 1);',
    );

    const state = await runLoop(project(), { workspace: source, paths: paths() });

    expect(state.status).toBe("succeeded");
    expect(state.termination).toBe("verified");
    expect(state.distPath?.startsWith(join(root, "dist"))).toBe(true);
    expect(existsSync(join(state.distPath!, "build", "worker.js"))).toBe(true);
    expect(existsSync(join(state.distPath!, "manifest.json"))).toBe(true);
    expect(existsSync(join(root, "state", `${state.id}.json`))).toBe(true);
    expect(existsSync(join(root, "ledgers", `${state.id}.jsonl`))).toBe(true);
  });

  test("feeds a syntax failure into the next planner invocation", async () => {
    write("build.mjs", 'throw new SyntaxError("Unexpected token in worker.ts");');
    write("verify.mjs", "process.exit(0);");
    const observations: ExecutionState[] = [];

    const state = await runLoop(
      project({
        planner: (current): Plan => {
          observations.push(current);
          if (current.errors.length === 0) {
            return { steps: ["Observe the compiler"], preBuildCommands: [] };
          }
          expect(current.errors.at(-1)?.signature).toBe("syntax_error");
          return {
            steps: ["Repair syntax"],
            preBuildCommands: [],
            apply: (workspace) => {
              writeFileSync(
                join(workspace, "build.mjs"),
                'import {mkdirSync,writeFileSync} from "node:fs"; mkdirSync("build",{recursive:true}); writeFileSync("build/worker.js","fixed");',
              );
              return "replaced invalid build source";
            },
          };
        },
      }),
      { workspace: source, paths: paths(), config: { maxIterations: 3 } },
    );

    expect(state.status).toBe("succeeded");
    expect(state.iteration).toBe(1);
    expect(observations).toHaveLength(2);
    expect(observations[1].errors[0].stderr).toContain("Unexpected token");
  });

  test("captures runtime verification errors and repairs them on the next cycle", async () => {
    write(
      "build.mjs",
      'import {mkdirSync,writeFileSync} from "node:fs"; mkdirSync("build",{recursive:true}); writeFileSync("build/worker.js","built");',
    );
    write("verify.mjs", 'throw new ReferenceError("workerBoot is not defined");');

    const state = await runLoop(
      project({
        planner: (current) => {
          if (current.errors.length === 0) {
            return { steps: ["Build and verify"], preBuildCommands: [] };
          }
          expect(current.errors.at(-1)?.phase).toBe("verify");
          expect(current.errors.at(-1)?.signature).toBe("runtime_error");
          return {
            steps: ["Repair runtime verification"],
            preBuildCommands: [],
            apply: (workspace) => {
              writeFileSync(join(workspace, "verify.mjs"), "process.exit(0);");
              return "defined the runtime entrypoint";
            },
          };
        },
      }),
      { workspace: source, paths: paths(), config: { maxIterations: 3 } },
    );

    expect(state.status).toBe("succeeded");
    expect(state.errors.some((e) => e.signature === "runtime_error")).toBe(true);
  });

  test("stops at the iteration cap and never publishes a failed build", async () => {
    write(
      "build.mjs",
      'import {writeFileSync,readFileSync,existsSync} from "node:fs"; const n=existsSync("nonce")?Number(readFileSync("nonce","utf8")):0; writeFileSync("nonce",String(n+1));',
    );
    write("verify.mjs", 'console.error("AssertionError: still wrong"); process.exit(1);');

    const state = await runLoop(
      project({
        planner: () => ({ steps: ["Try again"], preBuildCommands: [] }),
      }),
      {
        workspace: source,
        paths: paths(),
        config: { maxIterations: 2, maxDepth: 5, fuel: 10 },
      },
    );

    expect(state.status).toBe("failed");
    expect(state.termination).toBe("max_iterations");
    expect(state.distPath).toBeUndefined();
    expect(existsSync(join(root, "dist", state.id))).toBe(false);
  });

  test("fails closed when a verified distribution file is missing", async () => {
    write("build.mjs", "process.exit(0);");
    write("verify.mjs", "process.exit(0);");

    const state = await runLoop(project({ distFiles: ["build/missing-worker.js"] }), {
      workspace: source,
      paths: paths(),
    });

    expect(state.status).toBe("failed");
    expect(state.termination).toBe("distribution_failed");
    expect(state.distPath).toBeUndefined();
    expect(existsSync(join(root, "dist", state.id))).toBe(false);
  });

  test("pins child cwd, caches, installs, and temp files to the share", async () => {
    write(
      "build.mjs",
      `import {mkdirSync,writeFileSync} from "node:fs";
const data={cwd:process.cwd(),cache:process.env.npm_config_cache,prefix:process.env.npm_config_prefix,bun:process.env.BUN_INSTALL_CACHE_DIR,tmp:process.env.TMPDIR};
mkdirSync("build",{recursive:true}); writeFileSync("build/env.json",JSON.stringify(data));`,
    );
    write("verify.mjs", "process.exit(0);");

    const state = await runLoop(project(), { workspace: source, paths: paths() });
    const env = JSON.parse(readFileSync(join(state.distPath!, "build", "env.json"), "utf8")) as {
      cwd: string;
      cache: string;
      prefix: string;
      bun: string;
      tmp: string;
    };

    expect(env.cwd.startsWith(root)).toBe(true);
    expect(env.cache.startsWith(root)).toBe(true);
    expect(env.prefix.startsWith(root)).toBe(true);
    expect(env.bun.startsWith(root)).toBe(true);
    expect(env.tmp.startsWith(root)).toBe(true);
    expect(state.currentCode.workspace.startsWith(join(root, "tmp"))).toBe(true);
  });

  test("daemon claims a queued job and writes its terminal state", async () => {
    write(
      "build.mjs",
      'import {mkdirSync,writeFileSync} from "node:fs"; mkdirSync("build",{recursive:true}); writeFileSync("build/worker.js","ok");',
    );
    write("verify.mjs", "process.exit(0);");
    const storage = paths();
    const config: ProjectConfig = {
      objective: "Build queued worker",
      source,
      buildCommand: "node build.mjs",
      verifyCommand: "node verify.mjs",
      distFiles: ["build"],
    };

    const id = submitJob(config, storage);
    expect(await processAvailable(storage)).toBe(1);

    const terminal = JSON.parse(
      readFileSync(join(storage.tmp, "loop-harness", "daemon", "completed", `${id}.json`), "utf8"),
    ) as ExecutionState;
    expect(terminal.status).toBe("succeeded");
    expect(terminal.distPath).toBe(join(root, "dist", id));
    expect(existsSync(join(storage.tmp, "loop-harness", "daemon", "processing", `${id}.json`))).toBe(false);
  });
});

describe("failure classification", () => {
  test("recognizes node_modules crashes", () => {
    const result: CommandResult = {
      command: "node worker.js",
      exitCode: 1,
      stdout: "",
      stderr: "Error: Cannot find module 'left-pad'\\nRequire stack: /app/node_modules/x.js",
      durationMs: 5,
    };
    expect(classify(result)).toBe("missing_dependencies");
  });
});
