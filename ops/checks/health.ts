import { config } from "../../packages/core/config.ts";
import {
	countEvidence,
	initEvidenceDir,
} from "../../packages/core/evidence-ledger.ts";
import { createLogger } from "../../packages/core/logger.ts";

const log = createLogger("health-check");

interface HealthResult {
	service: string;
	status: "ok" | "degraded" | "down";
	message: string;
	latencyMs?: number;
}

async function checkEvidenceLedger(): Promise<HealthResult> {
	const start = Date.now();
	try {
		initEvidenceDir();
		const count = await countEvidence();
		return {
			service: "evidence-ledger",
			status: "ok",
			message: `${count} records`,
			latencyMs: Date.now() - start,
		};
	} catch (e) {
		return {
			service: "evidence-ledger",
			status: "down",
			message: String(e),
			latencyMs: Date.now() - start,
		};
	}
}

async function checkOperatorConsole(): Promise<HealthResult> {
	const start = Date.now();
	const url = `http://${config.server.host === "0.0.0.0" ? "127.0.0.1" : config.server.host}:${config.server.port}/health`;
	try {
		const res = await fetch(url, { signal: AbortSignal.timeout(3000) });
		const body = (await res.json()) as { ok: boolean };
		return {
			service: "operator-console",
			status: body.ok ? "ok" : "degraded",
			message: `HTTP ${res.status}`,
			latencyMs: Date.now() - start,
		};
	} catch {
		return {
			service: "operator-console",
			status: "down",
			message: "Connection refused",
			latencyMs: Date.now() - start,
		};
	}
}

async function checkZoSuperServer(): Promise<HealthResult> {
	const start = Date.now();
	try {
		const res = await fetch(config.zoSuperServer.url, {
			signal: AbortSignal.timeout(3000),
		});
		const body = (await res.json()) as { ok: boolean };
		return {
			service: "zo-super-server",
			status: body.ok ? "ok" : "degraded",
			message: `HTTP ${res.status}`,
			latencyMs: Date.now() - start,
		};
	} catch {
		return {
			service: "zo-super-server",
			status: "down",
			message: "Connection refused (expected if not running)",
			latencyMs: Date.now() - start,
		};
	}
}

async function main() {
	log.info("Running health checks...");

	const results = await Promise.all([
		checkEvidenceLedger(),
		checkOperatorConsole(),
		checkZoSuperServer(),
	]);

	for (const result of results) {
		const icon =
			result.status === "ok"
				? "OK"
				: result.status === "degraded"
					? "WARN"
					: "DOWN";
		log.info(
			`[${icon}] ${result.service}: ${result.message} (${result.latencyMs}ms)`,
		);
	}

	const allOk = results.every((r) => r.status === "ok");
	const anyDown = results.some((r) => r.status === "down");

	if (allOk) {
		log.info("All systems operational");
	} else if (anyDown) {
		log.warn("Some systems are down");
	} else {
		log.warn("Some systems are degraded");
	}

	console.log(JSON.stringify({ checks: results }, null, 2));
}

main().catch(console.error);
